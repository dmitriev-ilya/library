import urllib
import argparse

import requests
from bs4 import BeautifulSoup


def parse_scince_fiction_books_url(start_page, end_page):
    scince_fiction_books_url = []
    for page_number in range(start_page, end_page + 1):
        category_page_url = f"https://tululu.org/l55/{page_number}/"
        category_page_response = requests.get(category_page_url)
        category_page_response.raise_for_status()

        html_page = BeautifulSoup(category_page_response.text, 'lxml')
        books = html_page.find_all('table', class_='d_book')
        for book in books:
            book_id = book.find('a')['href']
            absolute_book_url = urllib.parse.urljoin(category_page_response.url, book_id)
            scince_fiction_books_url.append(absolute_book_url)
    return scince_fiction_books_url


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Скрипт для постраничного парсинга URL-адресов книг в категории научной фантастики сайта tululu.org/')
    parser.add_argument(
        "-s",
        "--start_page",
        help='номер страницы сайта с которой начинается парсинг',
        default=1,
        type=int
    )
    parser.add_argument(
        "-e",
        "--end_page",
        help='номер страницы сайта на которой заканчивается парсинг',
        default=4,
        type=int
    )
    args = parser.parse_args()

    print(parse_scince_fiction_books_url(args.start_page, args.end_page))
