import os
import urllib
import argparse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(book_id, filename, folder='books/'):
    download_url = "https://tululu.org/txt.php"
    params = {'id': book_id}
    response = requests.get(download_url, params=params)
    response.raise_for_status()
    check_for_redirect(response)

    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, sanitize_filename(filename))
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def download_image(url, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    os.makedirs(folder, exist_ok=True)
    filename = urllib.parse.urlsplit(url)[2].split('/')[-1]
    filepath = os.path.join(folder, urllib.parse.unquote(filename))
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def parse_book_page(book_url):
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response)

    html_page = BeautifulSoup(response.text, 'lxml')

    title, author = html_page.find('table').find('h1').text.split('::')

    comments = html_page.find_all(class_='texts')
    genres = html_page.find('span', class_='d_book').find_all('a')

    book_img_url = html_page.find('div', class_='bookimage').find('img')['src']
    absolute_img_url = urllib.parse.urljoin(response.url, book_img_url)

    parsed_book_page = {
        'title': title.strip(),
        'author': author.strip(),
        'comments': [comment.find(class_='black').text for comment in comments],
        'genres': [genre.text for genre in genres],
        'book_img_url': absolute_img_url
    }
    return parsed_book_page


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Скрипт для массового скачивания книг с сайта tululu.org/')
    parser.add_argument(
        "-s",
        "--start_id",
        help='id книги с которой начинается диапазон скачивания',
        default=1,
        type=int
    )
    parser.add_argument(
        "-e",
        "--end_id",
        help='id книги которым заканичвается диапазон скачивания',
        default=10,
        type=int
    )
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id + 1):
        try:
            book_url = f"https://tululu.org/b{book_id}/"
            parsed_book_page = parse_book_page(book_url)

            filename = f"{book_id}. {parsed_book_page['title']}.txt"
            download_txt(book_id, filename)
            download_image(parsed_book_page['book_img_url'])

            print(f"Название: {parsed_book_page['title']}")
            print(f"Автор: {parsed_book_page['author']}")
            print()
        except requests.HTTPError:
            continue
