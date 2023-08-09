import sys

from rocketry import Rocketry
from rocketry.conds import every
from rocketry.args import TerminationFlag
from rocketry.exc import TaskTerminationException

from summer_practice.crud import update_object, create_object, get_object, filter_objects
# from summer_practice import schemas, crud
from summer_practice.products import crud, schemas, models
from summer_practice.database import SessionLocal
from summer_practice.tasks.parsers.parser_chitai_gorod import parse_books
from summer_practice.tasks.parsers.parser_aliexpress import parse_aliexpress
from summer_practice.tasks.proxies import proxy_leecher, proxy_checker
from summer_practice.tasks.proxies.config import PATH_TO_FOLDER, HTTP_PROXIES_RAW_FILENAME, HTTPS_PROXIES_GOOD_FILENAME

app = Rocketry()


# Запуск в отдельном потоке. Повторять каждые четыре часа, с момента запуска (Изначально выключено)
@app.task(every("4 hours"), execution="thread", disabled=False)
async def do_parse_data_from_aliexpress(flag=TerminationFlag()):
    """Получает данные с мирового интернет-магазина AliExpress, посредстом парсинга всей страницы.
    Взаимодейтсвие с API в стадии разработки (код закомментирован)."""
    with SessionLocal() as db:  # Повторение логики из main

        store = get_object(db=db, model=models.Store, title="AliExpress")
        if store is None:
            store_schema = schemas.StoreCreate(title="AliExpress",
                                               url="https://aliexpress.ru/",
                                               items_model="Product")
            store = create_object(db=db, model=models.Store, schema=store_schema)

        for products_dict in parse_aliexpress(1, 20,
                                              use_proxies=True):  # Пока что не реализован автоматический подсчёт страниц
            for product_dict in products_dict:
                # Проверка, если задача была принудительно завершена.
                if flag.is_set():
                    raise TaskTerminationException()

                title = product_dict['title']
                _len = 15
                if len(title) >= _len:
                    last_space_index = title[:_len + 1].rfind(' ')
                    if last_space_index != -1:
                        title = title[:last_space_index] + '...'
                    else:
                        title = title[:_len] + '...'

                db_product = crud.get_product_by_url(db=db, model=models.Product,
                                                     product_url=product_dict['url'], store=store)

                if db_product:
                    if crud.is_product_in_blacklist(db, db_product):
                        print(f"Продукт '{title}' в чёрном списке.")
                        continue

                    print(f"Продукт '{title}' с таким url уже существует. Обновляю данные.")
                    update_object(db=db, model=db_product, schema=schemas.BookBase(**product_dict))
                    continue

                product_schem = schemas.ProductCreate(**product_dict)
                if crud.create_object(db, model=models.Product, schema=product_schem, store=store):
                    sys.stdout.write(f"Продукт '{title}' успешно добавлен." + '\n')
                    sys.stdout.flush()


# Запуск в отдельном потоке. Повторять каждые четыре часа, с момента запуска (Изначально выключено)
@app.task(every("6 hours"), execution="thread", disabled=True)
async def do_parse_data_from_chitai_gorod(flag=TerminationFlag()):
    """Использует API интернет-магазина Читай-Город, который был выявлен посредстом узучения кода скриптов и запросов"""
    with SessionLocal() as db:  # Повторение логики из main
        for book_dict in parse_books(from_page=1, to_page=500):

            # Проверка, если задача была принудительно завершена.
            if flag.is_set():
                raise TaskTerminationException()

            store = get_object(db=db, model=models.Store, title="Читай-Город")
            if store is None:
                store_schema = schemas.StoreCreate(title="Читай-Город",
                                                   url="https://chitai-gorod.ru/",
                                                   items_model="Book")
                store = create_object(db=db, model=models.Store, schema=store_schema)

            db_book = crud.get_product_by_url(db, model=models.Book, product_url=book_dict['url'], store=store)

            if db_book:
                if crud.is_product_in_blacklist(db, db_book):
                    print(f"Продукт {db_book.title} в чёрном списке.")
                    continue

                print(f"Книга '{book_dict['title']}' {book_dict['year_publishing']} с таким url уже существует. "
                      f"Обновляю данные.")
                update_object(db=db, model=db_book, schema=schemas.BookBase(**book_dict))
                continue

            book_schem = schemas.BookCreate(**book_dict)

            if create_object(db=db, model=models.Book, schema=book_schem, store=store):
                sys.stdout.write(f"Книга '{book_dict['title']}' {book_dict['year_publishing']} успешно добавлена "
                                 f"в магазин {store.title}" + '\n')
                sys.stdout.flush()


# Запуск в отдельном потоке. Повторять каждые четыре часа, с момента запуска (Изначально выключено)
@app.task(every("1 hours"), execution="thread", disabled=True)
async def do_proxy_processes(flag=TerminationFlag()):
    """Изначально получает небольшой список публичных прокси (proxy_leecher), а затем производит их валидацию,
    посредством отправки запроса на сайт https://aliexpress.ru/"""

    print("Начинаю получать список прокси.")
    proxy_leecher.start_leech()

    with open(PATH_TO_FOLDER() + HTTP_PROXIES_RAW_FILENAME) as f:
        print("Прокси получено: " + str(sum(1 for _ in f)))

    if flag.is_set():
        raise TaskTerminationException()
    # Не нравится мне, как тут прекращение работы реализовано, но... нет времени на придумывание новой логики ;(((
    print("Начинаю валидировать список прокси.")
    proxy_checker.check_proxies()

    with open(PATH_TO_FOLDER() + HTTPS_PROXIES_GOOD_FILENAME) as f:
        print("Всего валидных прокси: " + str(sum(1 for _ in f)))


if __name__ == "__main__":
    # import os
    #
    # # Получаем текущий рабочий каталог (где запущен скрипт)
    # current_working_directory = os.getcwd()
    #
    # # Получаем путь к директории на два уровня выше
    # two_levels_up = os.path.abspath(os.path.join(current_working_directory, "..", ".."))
    #
    # os.chdir(two_levels_up)

    # Run only Rocketry
    app.run()
