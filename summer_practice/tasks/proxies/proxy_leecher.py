import re

import requests
from bs4 import BeautifulSoup

from summer_practice.tasks.proxies.config import PATH_TO_FOLDER, HTTP_PROXIES_RAW_FILENAME


def https_proxy_leeches(out_filepath):
    response = requests.get("https://checkerproxy.net/getAllProxy")

    soup = BeautifulSoup(response.content, 'lxml')

    div_with_archives = soup.find('div', {'class': 'archive'})
    a_with_links = div_with_archives.findAll('a')

    links = [link.get('href') for link in a_with_links]

    for link in links:
        print(f'Архив от {link}. {links.index(link)}/{len(links)}')

        try:
            url = 'https://checkerproxy.net/api' + link

            response_api = requests.get(url)

            if response_api.status_code != 200:
                print(f'Не найдено. Архив от {link}')
                continue

            api_json = response_api.json()

            with open(f"{out_filepath}" + HTTP_PROXIES_RAW_FILENAME, "a+") as file:
                for proxy in api_json:
                    proxy_type = proxy.get('type')
                    if proxy_type == 4:
                        existing_proxies = file.read().strip().split('\n')
                        if proxy not in existing_proxies:
                            file.write(proxy.get('addr') + '\n')

        except Exception as e:
            print(e)


def leech_from_github(out_filepath):
    response = requests.get('https://raw.githubusercontent.com/Bardiafa/Proxy-Leecher/main/proxies.txt')
    raw_data = response.text
    ipv4_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}:\d+\b"  # Регулярное выражение для поиска IPv4 адресов
    ipv4_addresses = re.findall(ipv4_pattern, raw_data)
    with open(f"{out_filepath}" + HTTP_PROXIES_RAW_FILENAME, "a") as file:
        file.write('\n'.join(ipv4_addresses) + '\n')
    print("Выгрузил с GitHub")


def start_leech():
    open(PATH_TO_FOLDER() + HTTP_PROXIES_RAW_FILENAME, 'w+').close()

    leech_from_github(PATH_TO_FOLDER())
    https_proxy_leeches(PATH_TO_FOLDER())


if __name__ == "__main__":
    import os

    # Получаем текущий рабочий каталог (где запущен скрипт)
    current_working_directory = os.getcwd()

    # Получаем путь к директории на два уровня выше
    two_levels_up = os.path.abspath(os.path.join(current_working_directory, "..", "..", ".."))

    os.chdir(two_levels_up)

    start_leech()
