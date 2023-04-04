import json
import os

from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

with open('media/books.json', 'r') as file:
    books_json = file.read()

books = json.loads(books_json)
books_by_pages = list(chunked(books, 10))


def render_template(books_by_pages):
    pages_path = 'pages'
    os.makedirs(pages_path, exist_ok=True)
    pages_number_range = list(range(1, len(books_by_pages) + 1))
    for page_number, books_on_page in enumerate(books_by_pages, start=1):
        books_on_couples = list(chunked(books_on_page, 2))
        template = env.get_template('template.html')
        index_filepath = os.path.join(pages_path, f'index{page_number}.html')

        rendered_page = template.render(
            books_on_couples=books_on_couples,
            pages_number_range=pages_number_range,
            current_page=page_number
        )
        with open(index_filepath, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def on_reload():
    render_template(books_by_pages)
    print('Site rebuilted')


on_reload()

server = Server()
server.watch('template.html', on_reload)
server.serve(root='.', default_filename='pages/index1.html')
