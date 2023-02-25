import os
import urllib

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
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


def parse_book_page(html_page):
    title_with_author = html_page.find('table').find('h1').text
    title = title_with_author.split('::')[0].strip()
    author = title_with_author.split('::')[1].strip()
    comments = html_page.find_all(class_='texts')
    genres = html_page.find('span', class_='d_book').find_all('a')

    book_img_url = html_page.find('div', class_='bookimage').find('img')['src']
    absolute_img_url = urllib.parse.urljoin('https://tululu.org/', book_img_url)

    serialized_book_page = {
        'title': title,
        'author': author,
        'comments': [comment.find(class_='black').text for comment in comments],
        'genres': [genre.text for genre in genres],
        'book_img_url': absolute_img_url
    }
    return serialized_book_page


if __name__ == '__main__':
    for id in range(1, 11):
        try:
            download_url = f"https://tululu.org/txt.php?id={id}"
            book_url = f"https://tululu.org/b{id}/"
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)

            html_page = BeautifulSoup(response.text, 'lxml')
            serialized_book_page = parse_book_page(html_page)

            filename = f"{id}. {serialized_book_page['title']}.txt"
            download_txt(download_url, filename)
            download_image(serialized_book_page['book_img_url'])
            
            print(f"Downloaded: {serialized_book_page['title']} - {serialized_book_page['author']}")
        except requests.HTTPError:
            continue
