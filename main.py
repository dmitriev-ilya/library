import os

import requests


os.makedirs("books", exist_ok=True)

for id in range(1, 11):
    url = f"https://tululu.org/txt.php?id={id}"
    response = requests.get(url)
    response.raise_for_status()

    filename = os.path.join("books", f"id{id}.txt")
    with open(filename, 'wb') as file:
        file.write(response.content)
