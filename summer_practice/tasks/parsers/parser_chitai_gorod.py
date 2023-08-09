import requests


def get_headers_with_access_token() -> dict:
    # Set Requirement Cookies into requests Session
    return {"Authorization":
            requests.post('https://web-gate.chitai-gorod.ru/api/v1/auth/anonymous').json()['token'].get('accessToken')}


# Нигде не используется, но в теории может. В функции parse_books можно указать category, по которой будет производиться
# парсинг. По умолчанию там None, что значит, что будут получены абсолютно все КНИГИ (-18030), независимо от категории.
def get_categories() -> dict:
    categories = requests.get("https://web-gate.chitai-gorod.ru/api/v1/categories/tree?slug=-18030",
                              headers=get_headers_with_access_token()).json()['data']['children'][0]['children']

    # генератор словаря для объединения словарей с категориями
    combined_dict = {category.get('title'): category.get('slug') for category in categories}

    return combined_dict


def parse_books(from_page: int | None = None, to_page: int | None = None,
                category: str | None = None, per_page: int = 200):
    per_page = min(max(per_page, 1), 200)  # Валидация, чтобы не вышли за пределы. От 1, до 200 включительно.

    current_page = from_page if from_page else 1
    last_page = to_page if to_page else 0

    category = category if category else "-18030"

    # Getting data from pages
    while True:
        data_json = requests.get(
            f'https://web-gate.chitai-gorod.ru/api/v1/products?category={category}'
            f'&page={current_page}'
            f'&perPage={per_page}',
            headers=get_headers_with_access_token()) \
            .json()

        if last_page == 0:
            total_books = data_json['meta']['total']
            books_per_page = data_json['meta']['perPage']

            # rounding up
            last_page = int(-1 * (total_books / books_per_page) // 1 * -1)

        if current_page >= last_page:
            break

        for book_json in data_json['data']:
            title: str = book_json['title']

            authors = [
                f"{author.get('lastName', '')} {author.get('firstName', '')} {author.get('middleName', '')}".strip()
                for author in book_json['authors']
            ]

            description: str = book_json['description']
            picture_url: str = "https://cdn.img-gorod.ru/" + book_json['picture']

            price: float = float(book_json['price'])

            year_publishing: int = book_json['yearPublishing']

            # rating_count = book_json['rating']['count']
            # rating_votes = book_json['rating']['votes']

            publisher: str = book_json['publisher'].get('title')

            pages: str = book_json['pages']

            category_book: str = book_json['category'].get('title')

            url: str = "https://www.chitai-gorod.ru/" + book_json['url']

            book_resp = {
                'title': title,
                'year_publishing': year_publishing,
                'description': description,
                'authors': authors,
                'publisher': publisher,
                'pages': pages,
                'category': category_book,
                'picture': picture_url,
                'price': price,
                'url': url,
            }

            yield book_resp

        current_page += 1


if __name__ == "__main__":
    # print(get_categories())

    for book in parse_books(to_page=13):
        print(book)
    # print(*parse_cars(), sep='\n')
