import json
import multiprocessing as mp
import pathlib as pl

from tmdb import TMDB
from cache import cache_json

with open('/home/wbhorn/Documents/keys/moviedb.key', 'r') as f:
    API_KEY = f.read().strip()

DB = TMDB(API_KEY)


def main():
    with open('movies.csv') as f:
        movie_titles = f.read().split('\n')

    threaded(movie_titles)


def threaded(movie_titles):
    pool = mp.Pool(5)
    movie_results = pool.map(scrape, movie_titles)
    pool.map(download_poster, filter(lambda x: x, movie_results))


def single(movie_titles):
    movie_results = [scrape(movie) for movie in movie_titles]

    for r in filter():
        download_poster(r)


def download_poster(movie):
    key, title = [movie[k] for k in ['poster_path', 'title']]

    img_type = pl.Path(key).suffix

    DB.download_poster(key, f'movie-posters/{title}{img_type}')


def scrape(movie_title):
    movie_results = movie_search(movie_title)

    try:
        best_result = get_top_result(movie_results)
    except KeyError:
        print(movie_title)
    else:
        return best_result


def get_top_result(results):
    top_result = sorted(
        results['results'],
        key=lambda v: v['vote_count']
    )[-1]

    return top_result


@cache_json
def movie_search(movie):
    results = DB.search_movie(movie)

    if results.get('status_code', False) == 25:
        raise Exception('Reached limit')

    if len(results['results']) == 0:
        raise Exception(f'No Results: {Movie}')

    return results


if __name__ == "__main__":
    main()
