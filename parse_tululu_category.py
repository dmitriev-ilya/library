import urllib
import argparse
import sys
import time
import json

import requests
from bs4 import BeautifulSoup

from main import get_response, parse_book_page, download_txt, download_image


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


def extract_book_id_from_url(book_url):
    raw_book_id = urllib.parse.urlsplit(book_url)[2]
    book_id = int(''.join(filter(str.isdigit, raw_book_id)))
    return book_id


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

    scince_fiction_books_url = parse_scince_fiction_books_url(args.start_page, args.end_page)
    books = []

    for number, book_url in enumerate(scince_fiction_books_url, start=1):
        active_loop = True
        while active_loop:
            try:
                book_page_response = get_response(book_url)
                parsed_book_page = parse_book_page(book_page_response)

                book_id = extract_book_id_from_url(book_url)

                filename = f"{number}-я книга. {parsed_book_page['title']}.txt"
                book_path = download_txt(book_id, filename)
                image_path = download_image(parsed_book_page['book_img_url'])
                title = parsed_book_page['title']
                author = parsed_book_page['author']

                print(f"Название: {title}")
                print(f"Автор: {author}")
                print()

                book_card = {
                    'title': title,
                    'author': author,
                    'img_src': image_path,
                    'book_path': book_path,
                    'comments': parsed_book_page['comments'],
                    'genres': parsed_book_page['genres']
                }
                books.append(book_card)

                active_loop = False
            except requests.HTTPError:
                sys.stderr.write(f'A book with ID {book_id} does not exist \n\n')
                active_loop = False
            except requests.exceptions.ConnectionError:
                sys.stderr.write("Connection lost. Trying to reconnecting \n\n")
                time.sleep(2)

    books_json = json.dumps(books, ensure_ascii=False)
    with open("books.json", "w", encoding='utf8') as file:
        file.write(books_json)
