import multiprocessing as mp
import pathlib as pl
import re

from bs4 import BeautifulSoup
import requests


def main():
    with open('movies.csv') as f:
        movies = f.read().split('\n')

    for movie in movies:
        scrape(movie)


def scrape(movie):
    cache = pl.Path(__file__).parent / 'cache' / f'{movie}.html'
    if cache.exists():
        with cache.open('r') as f:
            text = f.read()
    else:
        google_search = f'https://www.google.com/search?q={movie}'
        text = requests.get(google_search).text
        with cache.open('w') as f:
            f.write(text)

    bs_parse(text)


def re_parse(r_text):
    print(list(re.findall('\d\d\%', r_text)))


def bs_parse(r_text):
    movie_soup = BeautifulSoup(r_text, "lxml")

    for link in movie_soup.find_all('a'):
        if 'rottentomatoes' in link['href']:
            print(list(link.children))


if __name__ == "__main__":
    main()
