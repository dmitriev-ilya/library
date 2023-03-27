import json

from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

with open("books.json", "r") as file:
    books_json = file.read()

books = json.loads(books_json)


def on_reload():
    template = env.get_template('template.html')
    rendered_page = template.render(books=books)
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    print("Site rebuilted")


on_reload()

server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
