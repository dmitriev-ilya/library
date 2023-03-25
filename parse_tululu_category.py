import urllib
import argparse
import sys
import time
import json
import os

import requests
from bs4 import BeautifulSoup

from main import get_response, parse_book_page, download_txt, download_image


def parse_scince_fiction_book_urls(start_page, end_page):
    scince_fiction_book_urls = []
    for page_number in range(start_page, end_page + 1):
        active_loop = True
        while active_loop:
            try:
                category_page_url = f"https://tululu.org/l55/{page_number}/"
                category_page_response = get_response(category_page_url)

                html_page = BeautifulSoup(category_page_response.text, 'lxml')
                books = html_page.select('.d_book')
                for book in books:
                    book_id = book.select_one('a')['href']
                    absolute_book_url = urllib.parse.urljoin(category_page_response.url, book_id)
                    scince_fiction_book_urls.append(absolute_book_url)
                active_loop = False
            except requests.HTTPError:
                sys.stderr.write(f'A page number {page_number} does not exist \n\n')
                active_loop = False
            except requests.exceptions.ConnectionError:
                sys.stderr.write("Connection lost. Trying to reconnecting \n\n")
                time.sleep(2)
    return scince_fiction_book_urls


def extract_book_id_from_url(book_url):
    raw_book_id = urllib.parse.urlsplit(book_url)[2]
    book_id = int(''.join(filter(str.isdigit, raw_book_id)))
    return book_id


def get_category_pages_amount(category_url):
    category_response = requests.get(category_url)
    category_response.raise_for_status()

    html_category_page = BeautifulSoup(category_response.text, 'lxml')
    pages_amount = html_category_page.select('.npage')[-1].text
    return int(pages_amount)


if __name__ == '__main__':
    category_url = "https://tululu.org/l55/"
    pages_amount = get_category_pages_amount(category_url)

    parser = argparse.ArgumentParser(
        description='Скрипт для постраничного парсинга URL-адресов книг \
         в категории научной фантастики сайта tululu.org/'
    )
    parser.add_argument(
        "-s",
        "--start_page",
        help='номер страницы сайта с которой начинается парсинг, по умолчанию - 1',
        default=1,
        type=int
    )
    parser.add_argument(
        "-e",
        "--end_page",
        help='номер страницы сайта на которой заканчивается парсинг, по умолчанию - все оставшиеся страницы',
        default=pages_amount,
        type=int
    )
    parser.add_argument(
        "-s_i",
        "--skip_imgs",
        help='не скачивать картинки',
        action='store_true'
    )
    parser.add_argument(
        "-s_t",
        "--skip_txt",
        help='не скачивать текст книг',
        action='store_true'
    )
    parser.add_argument(
        "-j",
        "--json_path",
        help='путь к файлу .json для записи информации о книгах',
        default="books.json",
        type=str
    )
    parser.add_argument(
        "-f",
        "--dest_folder",
        help='путь к каталогу с результатами парсинга: картинкам, книгам, JSON',
        default="",
        type=str
    )
    args = parser.parse_args()

    images_folder = os.path.join(args.dest_folder, 'images')
    books_folder = os.path.join(args.dest_folder, 'books')

    scince_fiction_book_urls = parse_scince_fiction_book_urls(args.start_page, args.end_page)
    books = []

    for number, book_url in enumerate(scince_fiction_book_urls, start=1):
        active_loop = True
        while active_loop:
            try:
                book_page_response = get_response(book_url)
                parsed_book_page = parse_book_page(book_page_response)

                book_id = extract_book_id_from_url(book_url)

                filename = f"{number}-я книга. {parsed_book_page['title']}.txt"
                if args.skip_txt:
                    book_path = 'the path is missing'
                else:
                    book_path = download_txt(book_id, filename, books_folder)
                if args.skip_imgs:
                    image_path = 'the path is missing'
                else:
                    image_path = download_image(parsed_book_page['book_img_url'], images_folder)
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

    json_path = os.path.join(args.dest_folder, args.json_path)

    with open(json_path, "w", encoding='utf8') as file:
        json.dump(books, file, ensure_ascii=False)
