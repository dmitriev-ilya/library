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


for id in range(1, 11):
    try:
        download_url = f"https://tululu.org/txt.php?id={id}"
        book_url = f"https://tululu.org/b{id}/"
        response = requests.get(book_url)
        response.raise_for_status()
        check_for_redirect(response)

        soup = BeautifulSoup(response.text, 'lxml')
        title_with_author = soup.find('table').find('h1').text
        title = title_with_author.split('::')[0].strip()
        author = title_with_author.split('::')[1].strip()

        comments = soup.find_all(class_='texts')

        genres = soup.find('span', class_='d_book').find_all('a')

        print(title)
        print([genre.text for genre in genres])
        #for comment in comments:
        #    print(comment.find(class_='black').text)

        #filename = f"{id}. {title}.txt"
        #download_txt(download_url, filename)
    except requests.HTTPError:
        print('Book not found')


"""
for id in range(1, 11):
    try:
        book_url = f"https://tululu.org/b{id}/"
        response = requests.get(book_url)
        response.raise_for_status()
        check_for_redirect(response)

        soup = BeautifulSoup(response.text, 'lxml')
        post_img_url = soup.find('div', class_='bookimage').find('img')['src']
        absolute_img_url = urllib.parse.urljoin('https://tululu.org/', post_img_url)
        download_image(absolute_img_url)

    except requests.HTTPError:
        print('Book not found')
"""
