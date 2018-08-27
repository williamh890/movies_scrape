import json
import multiprocessing as mp
import pathlib as pl

import requests

from cache import cache_json

with open('/home/wbhorn/Documents/keys/moviedb.key', 'r') as f:
    API_KEY = f.read().strip()


def main():
    with open('movies.csv') as f:
        movie_titles = f.read().split('\n')

    pool = mp.Pool(10)
    movies = pool.map(scrape, movie_titles)


def scrape(movie_title):
    print(movie_title)
    movie_search(movie_title)


@cache_json
def movie_search(movie):
    db = TMDB(API_KEY)

    return db.search_movie(movie)


class TMDB:
    def __init__(self, api_key):
        self.base_url = 'https://api.themoviedb.org/3/search/movie'
        self.api_key = api_key

    def base_params(self):
        return {
            'api_key': self.api_key,
            'language': 'en-US',
            'page': '1',
            'include_adult': 'false'
        }

    def search_movie(self, movie):
        req = requests.get(self.base_url, params={
            **self.base_params(),
            'query': movie,
        })

        return json.loads(req.text)


if __name__ == "__main__":
    main()
