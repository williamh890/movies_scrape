import pathlib as pl
import json

import subprocess
import os

import requests


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

    def download_poster(self, key, path):
        if pl.Path(path).exists():
            return

        try:
            with open(os.devnull, 'w') as FNULL:
                subprocess.check_call([
                    'curl', '-o', path, f'https://image.tmdb.org/t/p/w500{key}'
                ], stdout=FNULL, stderr=subprocess.STDOUT)
        except:
            print(f'failed to download {path}')
