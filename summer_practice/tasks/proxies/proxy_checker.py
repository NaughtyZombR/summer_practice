import requests
from concurrent import futures

from summer_practice.tasks.proxies.config import HTTPS_PROXIES_GOOD_FILENAME, HTTP_PROXIES_RAW_FILENAME, PATH_TO_FOLDER


def get_proxies(filepath):
    with open(filepath, 'a+') as file:
        file.seek(0)  # Перемещение к началу файла
        content = file.read().strip().split('\n')
    return content


def check_proxy(proxy, out_filepath):
    proxies = {
        "http": f"http://{proxy}/",
        "https": f"http://{proxy}/"
    }

    # url = 'https://api.ipify.org'
    url = 'https://aliexpress.ru/'

    try:
        response = requests.get(url, proxies=proxies, timeout=15)
        assert 'uuid' in response.text
        with open(out_filepath, "a+") as file:
            existing_proxies = file.read().strip().split('\n')
            if proxy not in existing_proxies:
                file.write(proxy + '\n')
                print("New Working proxy:", proxy)
        return proxy
    except:
        return None


def check_proxies():
    proxies = get_proxies(PATH_TO_FOLDER() + HTTPS_PROXIES_GOOD_FILENAME) + \
        get_proxies(PATH_TO_FOLDER() + HTTP_PROXIES_RAW_FILENAME)

    open(PATH_TO_FOLDER() + HTTPS_PROXIES_GOOD_FILENAME, 'w+').close()


    # num_threads = multiprocessing.cpu_count() * 2  # Увеличиваем количество потоков
    with futures.ThreadPoolExecutor(max_workers=200) as executor:
        executor.map(check_proxy, proxies, [PATH_TO_FOLDER() + HTTPS_PROXIES_GOOD_FILENAME] * len(proxies))


if __name__ == "__main__":
    import os

    # Получаем текущий рабочий каталог (где запущен скрипт)
    current_working_directory = os.getcwd()

    # Получаем путь к директории на два уровня выше
    two_levels_up = os.path.abspath(os.path.join(current_working_directory, "..", "..", ".."))

    os.chdir(two_levels_up)
    check_proxies()
