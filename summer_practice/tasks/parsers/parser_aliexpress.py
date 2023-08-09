import random

import re
import time

import requests
from bs4 import BeautifulSoup

from summer_practice.tasks.proxies.config import PATH_TO_FOLDER, HTTPS_PROXIES_GOOD_FILENAME

# На данный момент нигде не используется. Если время и желание будет -- доделаю.
# Лучше использовать "API", т.к. невозможно получить извне количество страниц в разделе.
"""def _get_aliexpress_products_from_api(jsess_id, page, proxy):
    # cookies = {'JSESSIONID': 'ca8f5183-4db6-4039-8da0-d884f853d248'.upper()}
    cookies = {'JSESSIONID': jsess_id.upper()}

    headers = {
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9',
        'bx-v': '2.5.1',
        'content-type': 'application/json',
        'origin': 'https://aliexpress.ru',
        'referer': 'https://aliexpress.ru/category/327/mobile-phones.html',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/112.0.0.0 YaBrowser/23.5.4.674 Yowser/2.5 Safari/537.36',
    }

    params = {
        '_bx-v': '2.5.1',
    }

    json_data = {
        'catId': '327',
        'g': 'n',
        'storeIds': [],
        'pgChildren': [],
        'aeBrainIds': [],
        'page': page,
        'searchInfo': 'category:eyJ0aXRsZSI6Ik1vYmlsZSBQaG9uZXMiLCAic2x1ZyI6Im1vYmlsZS1waG9uZXMiLCAiaWQiOiIzMjcifQ==',
        'source': 'nav_category',
    }

    response = requests.post(
        'https://aliexpress.ru/aer-jsonapi/v1/category_filter',
        params=params,
        cookies=cookies,
        headers=headers,
        json=json_data,
    )

    print(response.text)
    """


def _parse_aliexpress_page(page_number: int = 1, proxy: str = '') -> list[dict] | None:
    result = list()

    url = f"https://aliexpress.ru/category/327/mobile-phones.html?g=y&page={page_number}"

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
        'YaBrowser/23.5.4.674 Yowser/2.5 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.9 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'
    ]

    cookies = [
        'aep_usuc_f=b_locale=ru_RU&c_tp=RUB&region=RU&site=rus&province=917477670000000000&city=917477679070000000; '
        'aer_abid=ea3fb624b10d723c; '
        'xman_f=w9gehwViBvYV4nSxRH/n3uLfyd7eD2NEl9hb96URKzfOG0ZawUJ7Rg99X3gfQfYfsNadY12BkJgdsil+/WzwuFiFr'
        '/d1JJ5Yla5tkhMkiNiiN7JMbMyj3g==; xman_t=6tUoBgMvf0WSTQ/xgaNDi31oZ5Cs71cetl1DW0S+1JTcWidsW2gn6oysuQIxdRdO; '
        'xman_us_f=x_locale=ru_RU&x_l=0&acs_rt=006abcbe587a4f5887e6dbfc77fc3660',
        'acs_usuc_t=x_csrf=12l83dq6xuwup&acs_rt=bfb653a1f77a4ed89ec1c34c37f3f8cd; '
        'xman_t=TQuaeJfdlxU5ab/NNw8DthUybq650ceEiAUpecJIQ1HYmsBk2oGY4tQE0VqgWgPm; '
        'xman_f=+vojTaMHnWES81BvI0JHJNYojKlWt8zghWzk2efd4WrKqGLXpKju93o/W+/KXbi+POvyKTxJT3yTzLuaqy8rO5N+AQcB66XP3h7u'
        '/yLJzwH4zFmzncRMBA==; xman_us_f=x_locale=en_US&x_l=0&x_c_chg=1&acs_rt=41ce268b4a29485b9dc6f07b0cb83e53; '
        'intl_locale=en_US; aep_usuc_f=site=rus&c_tp=RUB&region=RU&b_locale=en_US; aer_abid=de265e28a4b34280; '
        'a_t_info={"name":"","id":"29da18a5-d767-4809-ac92-0ed29a2c1d1b"}; '
        'autoRegion=lastGeoUpdate=1689697098&regionCode=917483860000000000&cityCode=917483866975000000&countryCode=RU'
        '; cna=TKk9HTT6O3gCAbzqxBtqn3Yt; tmr_lvid=aae0b760811b3f79cef9eec8b0059030; tmr_lvidTS=1689697098890; '
        '_ga=GA1.2.1594597128.1689697099; _gid=GA1.2.115769720.1689697099; _gat_UA-164782000-1=1; '
        'intl_common_forever=zteRs4iFzvjIISxj4MXUayHMw7pmtpKQ/6rM8TfRYsWpP2wK7Iybpw==; '
        'JSESSIONID=2269B528A0FB04CAAD2B6EE5835E68FE; _ym_uid=1689697099627969311; _ym_d=1689697099; '
        'tmr_detect=1|1689697098952; _ym_isad=1; _ym_visorc=b; '
        'isg=BExMG7p-RCkZUlDV7bZGfMqwHap-hfAvfEhNfaYNWPeaMew7zpXAv0KD1SEJYiiH; '
        'tfstk=cD7OB2Z87J2GZ-eD8FE3ur3_xKwlw6wvdf9mkN9Siz-5wp1DWabRtRr6GLJT9; '
        'l=fBEsOSymN3muGSzSBOfaFurza77OSIRYYuPzaNbMi9fPObfB5-zRB1_rOQ86C3MNFsi9R38c3lSXBeYBq3xonxvt0UmaJyHmndLHR35..',
        'acs_usuc_t=x_csrf=pu56mp4bb5ui&acs_rt=cff780d6f0b64956ab589168ae49f1c6; '
        'xman_t=wKP5MbejQub7gwGUfdJO86e1bY6z2J628XdYeZJza5IoblGOhBMUCrl6izzrbdA3; '
        'xman_f=ae7VWbKXh1yO/7Y8X9Ood3K45Yh0uif'
        '/LhE5487xCNegpvIfF7Ao30720bG00w55FZNdmEuDCpGffzOPnLKYeYWJHUTibwpzHK261HR0ymQ7MsBCBgKBkA==; '
        'xman_us_f=x_locale=en_US&x_l=0&x_c_chg=1&acs_rt=0a85e2c7bb944f0e89c32af09c8b239b; intl_locale=en_US; '
        'aep_usuc_f=site=rus&c_tp=RUB&region=RU&b_locale=en_US; aer_abid=33888c6bf75f1d6b; a_t_info={"name":"",'
        '"id":"ef40d0f4-81aa-4511-8367-855ccea7aaea"}; _ga=GA1.2.146212160.1689697146; '
        '_gid=GA1.2.1328447529.1689697146; _gat_UA-164782000-1=1; tmr_lvid=2a45b2e03e000eb41f612fd56a1d7ad1; '
        'tmr_lvidTS=1689697145755; _ym_uid=1689697146173875201; _ym_d=1689697146; cna=e6k9HdeExHcCAbzqxBuBylsi; '
        '_ym_isad=2; autoRegion=lastGeoUpdate=1689697142&regionCode=917483860000000000&cityCode=917483866975000000'
        '&countryCode=RU; _ym_visorc=b; intl_common_forever=JjYBZZ60Ub2oV0cG3undtuUwkXV3q35b+udfDB2OU+4PXoupWT6teA==; '
        'JSESSIONID=F6733B80432778A73B6B8F4F4E7313EB; xlly_s=1; tmr_detect=0%7C1689697155857; '
        'tfstk=cXpCByij-y4It8kuKwiw1BocyHX5ZqrfVX_HAq3BlGJ7HExCiYwVldV6ZzBP2G1..; '
        'l=fBE-zJ5rN3msmOTvBOfwnurza77OGIRfguPzaNbMi9fP_85p59FNB1_rObY9CnMNesgwJ3lDK4dwB7L1QyhVOt0msmKdlZCE3dLz_Eld.; '
        'isg=BMbGrxUx3me3UYqDW96NDKbdF7xIJwrhorcd7LDv3-nEs2fNGbVh8dCFi_d_GwL5',
        'acs_usuc_t=x_csrf=g0e_amubqolh&acs_rt=350de5017c4246c48a53e5352010f144; '
        'xman_t=DFqzW61blFxIms591xT9grANbtkkGLe8eaj6mYRQQFB0VtX/mPsvTLKpIA+8yfrX; '
        'xman_f=8zXxJ3J9XreZURXM9YwJcr89g1B9'
        '/F5vsjs4PsWElnbdBbOmvCQyc9pMCsAiS5VDHSyMQBlyFIt3W5RPB05j3IT2tP0a07S5NS1bLK6WCvndSL9tN1vZvA==; '
        'xman_us_f=x_locale=en_US&x_l=0&x_c_chg=1&acs_rt=a02fab58250740b8b8fe1d94d93ff618; intl_locale=en_US; '
        'aep_usuc_f=site=rus&c_tp=RUB&region=RU&b_locale=en_US; aer_abid=ac42c66c61e80821; a_t_info={"name":"",'
        '"id":"44378ebf-31dd-4ed5-8ec5-2025647d72b6"}; '
        'autoRegion=lastGeoUpdate=1689697327&regionCode=917483860000000000&cityCode=917483866975000000&countryCode=RU'
        '; tmr_lvid=848e6c87884b540d5226e2abee583031; tmr_lvidTS=1689697328422; _ga=GA1.2.1861046991.1689697328; '
        'intl_common_forever=mjymKtx6yS71Jf49Rth8rTAOAn+Yu+T+CFBuafCyT/PKQWUEu0JLBA==; '
        'JSESSIONID=BD153774A3A046D4AB779755EF5598DF; _gid=GA1.2.1417125110.1689697328; _gat_UA-164782000-1=1; '
        '_ym_uid=1689697328846930047; _ym_d=1689697328; cna=Mao9HdDAwl4CAbzqxBsniMm5; _ym_isad=2; _ym_visorc=b; '
        'isg=BKurfhvBS0SVNZcQsWmRXxOiOs-VwL9CRwigXx0oh-pBvMsepZBPkkmeEuTShxc6; '
        'l=fBjr1S8gN3mFRIL2BOfaFurza77OSIRYYuPzaNbMi9fPOM5B5YERB1_r_wL6C3MNFsn9R3lDK4dwBeYBq7Vonxvt0UmaJyHmndLHR35..; '
        'tfstk=dTcB7ZTXxMjCwSN_D9TZCvom5QNW0DO4Jaa'
        '-o4CFyWFLNUiEcgrzUeq82lgPLkKHKzCSDc4P8WELBGEtfk8oL05S14mLY883YA_SocNrV4Y3yun-VukeQIun'
        '-7VJ00O2g2vRz7K2IYi0t2Vuwn-2gIun-mY2MyBm6fTQ3o_SM5qGsuyQD2OGw_G1gJZxJl18Sf6ZFsrjsO655-f75o865TXo0g2ws; '
        'xlly_s=1; tmr_detect=0%7C1689697331154',
        'acs_usuc_t=x_csrf=fzat2rhljrri&acs_rt=cc1128937c474f05902b273a1870fecd; '
        'xman_t=JxFMNSrBQQjJIp2X6eoDTJNy/s7UlZNm4lsaFMdeaL1wHg6elr/CUyhNPpyYpSQJ; '
        'xman_f=p+vpb73EvptR0Q7JZ7JZdDfs8oxSZZfEv6a5xWAoLgh//FIoc0xLE+/V1pXCRmxDZ5avcy'
        '/gwTp9S8YNrdqDpaMoDygh81c3cs1ueHNonIdyRNCLF3gD4Q==; '
        'xman_us_f=x_locale=en_US&x_l=0&x_c_chg=1&acs_rt=df75ff3fce9c42b494081a193d9ca713; intl_locale=en_US; '
        'aep_usuc_f=site=rus&c_tp=RUB&region=RU&b_locale=en_US; aer_abid=ea577bf7403199ae; a_t_info={"name":"",'
        '"id":"60d4591f-8b3a-45a8-bc3d-9399fd99c76f"}; cna=Yao9HT7T4X0CAbzqxBsXOpqf; '
        'tmr_lvid=525dfe93f5ae2bfeb97f675533706a2d; tmr_lvidTS=1689697376508; tmr_detect=1|1689697376552; '
        '_ga=GA1.2.42066045.1689697377; _gid=GA1.2.866061850.1689697377; _gat_UA-164782000-1=1; '
        'autoRegion=lastGeoUpdate=1689697375&regionCode=917483860000000000&cityCode=917483866975000000&countryCode=RU'
        '; _ym_uid=1689697377920586170; _ym_d=1689697377; _ym_isad=1; '
        'intl_common_forever=228DjlRncel+CYjIwTaNqszHeeyWDPQphm0x0jqBTrTy8KZHpZ5iYA==; '
        'JSESSIONID=64AA96D514C008055EB6DBB395C15A90; '
        'isg=BGVlUPIZbdJvZ4kOa5sfbkjXdCGfohk07Te0BmdKIRyrfoXwL_IpBPMcCPoI5THs; '
        'tfstk=c4gRBvt9zKvospp3uzKD8eQf4E9Gwg9Lh_whJ4w1swxqB-10JV0tiL-7ORyJM; '
        'l=fBPhzjj7N3mHg4sLBOfaFurza77OSIRYYuPzaNbMi9fPOLfB5mVFB1_r_HL6C3MNFsi9R38c3lSXBeYBq3xonxvt0UmaJyHmndLHR35..; '
        '_ym_visorc=b; xlly_s=1',
        'x5sec'
        '=7b22733b32223a223563663564643934373134316335383130363535363938333632363438386365222c2261656272696467653b3222'
        '3a2263636461323037383238656433646135386136643563383534366635636331384350333432715547455069533270666834646f514d'
        '4e376d6c2b482b2f2f2f2f2f77464141773d3d227d; '
        'acs_usuc_t=x_csrf=l1_02rw6jc9e&acs_rt=891fa13021e14d768f77c0971a3ca5c6; '
        'xman_t=bFZqfEisfZpSHe2LxVh1/nO/ShUQvjNku2DqoPVoT7uY+7WQiG9Bd6WDlZHG0L6z; '
        'xman_f=PayqN+YGtWPmhqpjV1qPs9LJRlicBpwcakIrJiGaJO51b6tW8oRzO1msodKHhbD5OMo7NspSM0I9Y6h'
        '+cYT5h7R0NVT12gWDNd5b7PUi3Vg/8r3/ROhpzw==; '
        'xman_us_f=x_locale=en_US&x_l=0&x_c_chg=1&acs_rt=df75ff3fce9c42b494081a193d9ca713; intl_locale=en_US; '
        'aep_usuc_f=site=rus&c_tp=RUB&region=RU&b_locale=en_US; aer_abid=c79c92280b2e3b66; '
        'cna=Yao9HT7T4X0CAbzqxBsXOpqf; _ga=GA1.2.873359429.1689697411; _gid=GA1.2.1833028729.1689697411; '
        '_gat_UA-164782000-1=1; a_r_t_info={"name":"","id":""}; a_t_info={"name":"",'
        '"id":"cd7ceaf1-bbfc-4f4c-8c0d-f8270a459c48"}; tmr_lvid=525dfe93f5ae2bfeb97f675533706a2d; '
        'tmr_lvidTS=1689697376508; tmr_detect=1|1689697413109; _ym_uid=1689697377920586170; _ym_d=1689697413; '
        '_ym_isad=1; autoRegion=lastGeoUpdate=1689697412&regionCode=917483860000000000&cityCode=917483866975000000'
        '&countryCode=RU; xlly_s=1; '
        'tfstk=dNhX7FYBmijbWJN7vtTrFxuF5iVsfmOUkNat-VCVWSFY1FiqAGraQEqTXugN3oKDnPCsv04NuSEYegE-Vo8i3c5sNVmY0R800Y_s'
        '-0NZfVY0Wlntflk2UBumo5V9YcOeTq2cn5KeEAi3iqVg6HufwlNtoDYe9v6yQn1FhCgXV_fP9ACjwddVO6G7kEqKluaurbabhke8VO'
        '-cTkZtDO_7K1a7YUT5IOvEU2KA.; '
        'l=fBPhzjj7N3mHglokKOfwPurza77OSIRAguPzaNbMi9fPOa5w5b0CB1_r_fLeC3MNFseXR38c3lSXBeYBqHxnnxvt0UmaJyHmnY9gx8C..; '
        'isg=BEFBtM67wSbzFC0Srycj2kTDUI1bbrVgUYMQ-qOWPcinimFc677FMG-AbObMgk2Y; '
        'intl_common_forever=KZEswAe1hGjLqEim9DSIBShiJEdzAKBFzmDmb9KbD3T244oC4CNF8Q==; '
        'JSESSIONID=6AD55BD8951A65F48135422D5B05B548; _ym_visorc=b'
    ]

    headers = {
        'User-Agent': random.choice(user_agents),
        'Content-Type': 'application/json',
        'Cookie': random.choice(cookies)
    }

    if proxy:
        proxy = f"http://{proxy}/"

    try:
        response = requests.get(url=url, headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=15)

        soup = BeautifulSoup(response.content, 'lxml')

        # TODO: попытаться реализовать через метод _get_aliexpress_products_from_api
        # uuid = json.loads(soup.find('script', {"id": "__AER_DATA__"}).text).get('widgets')[0].get('uuid')

        products_content_div = soup.findAll("div", {"class": re.compile('^product-snippet_ProductSnippet__content.*')})

        for product_content_div in products_content_div:
            product_desc_div = product_content_div.find("div",
                                                        {"class": re.compile(
                                                            '^product-snippet_ProductSnippet__description.*')})

            product_title_raw = product_desc_div.find("div",
                                                      {"class": re.compile('^product-snippet_ProductSnippet__name.*')})
            product_rating_raw = product_desc_div.find("div",
                                                       {"class": re.compile('^product-snippet_ProductSnippet.*')})
            product_bought_raw = product_desc_div.find("div",
                                                       {"class": re.compile('^product-snippet_ProductSnippet__sold.*')})
            product_price_raw = product_desc_div.find("div",
                                                      {"class": re.compile('^snow-price_SnowPrice__main.*')})

            product_url = product_content_div.find("a").get('href')
            product_image = product_content_div.find("picture").find("source").get("srcset")
            product_title = product_title_raw.text if product_title_raw is not None else ""
            product_rating = product_rating_raw.text if product_rating_raw is not None else ""
            product_bought = product_bought_raw.text if product_bought_raw is not None else ""
            product_price = product_price_raw.text if product_price_raw is not None else ""

            current_price = float(product_price.replace(" ", "").replace(',', '.')[:-1])

            result.append(
                {
                    'title': product_title,
                    'price': current_price,
                    'rating': product_rating,
                    'bought': product_bought,
                    'url': product_url,
                    'picture': product_image
                }
            )

    except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) \
            as error:
        print(error)
        print(f"Bad proxy {proxy}")

        return None

    return result


def parse_aliexpress(start_page: int = 1, total_pages: int = 1, use_proxies: bool = False) -> list[dict] | None:
    # proxies: list[str] | None = None

    is_proxies_list_empty = False
    is_need_new_proxy = False
    proxies = list()
    proxy = ""

    if use_proxies:
        proxies = get_proxies(PATH_TO_FOLDER() + HTTPS_PROXIES_GOOD_FILENAME)
        is_need_new_proxy = True

    for page_number in range(start_page, total_pages + 1):
        while not is_proxies_list_empty:

            if is_need_new_proxy and use_proxies:
                try:
                    proxy = proxies.pop()
                    is_need_new_proxy = False
                except IndexError:
                    is_proxies_list_empty = True
                    break

            data = _parse_aliexpress_page(page_number, proxy)

            if data:
                yield data
                time.sleep(5)  # Вынужденная мера, для того, чтобы слишком быстро не отлетали прокси
                break
            elif use_proxies:
                is_need_new_proxy = True
            else:
                break

    # return result


def get_proxies(filepath):
    with open(filepath, 'a+') as file:
        file.seek(0)  # Перемещение к началу файла
        content = file.read().strip().split('\n')
    return content


# def main():
#
#
#     parse_aliexpress(1, 10, proxies)


if __name__ == '__main__':
    for product_dict in parse_aliexpress(1, 20,
                                         use_proxies=False):

        # title = product_dict['title']
        # _len = 15
        # if len(title) >= _len:
        #     title = title[:max(title[:_len + 1].rfind(' '))] + '...'

        print(product_dict)
