from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from database import engine

import summer_practice.products.models

from summer_practice.products.routes import router_products, router_blacklist, router_stores
from summer_practice.tasks.routes import router_task

summer_practice.products.models.Base.metadata.create_all(bind=engine)


description = """
## Swagger UI не позволяет выбирать схемы в запросах, там, где их несколько, не знаю почему. 
### Поэтому советую открыть '/redoc' и вручную изменять тело запроса
**В ReDoc можно выбрать схему запроса и скопировать её, а протестировать запрос, 
не пользуясь никаким сторонним приложением, можно в Swagger UI (/docs)** 

***FindTheBestThing API*** поможет Вам с поиском наилучшей цены с разных магазинов! 🚀

## Товары


**Вы сможете посмотреть название товара, его цену, а также перейти на страницу товара в магазине.**

В том числе:
* ~~Аналитику товаров по конкретному магазину (_not implemented_).~~

**Upd.** На данный момент реализованы только структуры магазинов и их продуктов, с которыми можно взаимодействовать.

Запросы поддерживают несколько схем запросов и ответов, их можно просмотреть в раскрывшемся запросе - schemas.
Документация не такая гибкая, какую хотелось бы видеть, поэтому эти схемы нельзя выбрать. Остаётся лишь писать вручную.
Но я намеренно отказываюсь от разделения каждого запроса для каждой модели/схемы. Не профессионально)

"""


app = FastAPI(
    title="FindTheBestThing",
    description=description,
    summary="Лучшее решение для лучших!",
    version="0.0.1",
)


@app.get("/", name='redirect',
         description="**Используется для редиректа с корневого пути в документацию**")
def read_root():
    return RedirectResponse('/docs')


app.include_router(router_task)
app.include_router(router_stores)
app.include_router(router_products)
app.include_router(router_blacklist)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)
