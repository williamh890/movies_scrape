import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from multiprocessing.dummy import Pool as ThreadPool
import threading
import itertools


class Analitics(object):
    def __init__(self, movies):
        self.failed = 0
        self.succeeded = 0
        self.failed_movies = []
        self.get_times = []
        self.start_time = 0
        self.end_time = 0
        self.movie_starts = {}
        self.lock = threading.Lock()

    @property
    def percent_succeeded(self):
        return self.succeeded / (self.succeeded + self.failed) * 100

    @property
    def time_elapsed(self):
        with self.lock:
            if self.end_time == 0:
                return time.time() - self.start_time
            else:
                return self.end_time - self.start_time

    def start_movie(self, name):
        with self.lock:
            self.movie_starts[name] = time.time()

    def end_movie(self, name):
        with self.lock:
            movie_end = time.time()
            elapsed = movie_end - self.movie_starts[name]

            self.get_times.append(elapsed)

    def start_run(self):
        self.start_time = time.time()

    def end_run(self):
        self.end_time = time.time()

    def results(self):
        print("Run took {}").format(nice_time(self.time_elapsed))
        print("{} succeeded, {} failed, ({}%)".format(
            self.succeeded, self.failed, self.percent_succeeded))

        avg_time = mean(self.get_times)
        print("Average get time: {}".format(avg_time))

        m_str = ""
        for m in self.failed_movies:
            m_str += m + ", "
        m_str = m_str[:-2]

        print("Failed movies: {}".format(m_str))

    def add_failed_movie(self, movie):
        with self.lock:
            self.failed_movies.append(movie)


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def nice_time(elapsed):
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)


def read_movies_from_file(file):
    movies = []
    with open(file, "r") as movies_file:
        for movie in movies_file:
            movies.append(movie.strip())

    return movies


def search_wikipedia(movie):
    url = "https://en.wikipedia.org/w/api.php"
    param = {"search": movie,
             "action": "opensearch",
             "limit": 8,
             "namespace": 0,
             "format": "json"}

    # Make the request an load the json
    search_results = requests.get(url, param).text.replace(u'\xa0', u' ')
    search_results = json.loads(search_results)

    try:
        search_results = search_results[-1]
    except:
        print(search_results)
        return None

    return search_results


def get_movie_data(params):
    run_text = ""
    movie, stats = params

    if stats is not None:
        stats.start_movie(movie)

    # Just do one for testing
    movie_title = movie
    run_text += movie_title + "\n"

    search_results = search_wikipedia(movie_title)

    if search_results is None:
        run_text += "No search results found"
        return

    movie_data = {}
    # Look through all wikipedia search results
    for search_url in search_results:
        run_text += search_url + "\n"
        request = requests.get(search_url)
        movie_soup = BeautifulSoup(request.text, "lxml")

        table_data = []
        table = movie_soup.find("table", {"class": "infobox"})

        # Cant find the data table
        if table is None:
            run_text += "Cant find table data...\n"
            continue

        for tr in table.find_all("tr"):
            table_row = tr.text.split("\n")
            table_row = [r for r in table_row if r != ""]
            table_data.append(table_row)

        old_table_data, table_data = table_data, {}

        for r in old_table_data:
            try:
                table_data.update({r[0].strip(): r[1:]})
            except:
                try:
                    run_text += "Cant remove whitespace on {}...\n".format(r[0])
                except:
                    pass

        labels = ["Box office", "Starring", "Running time"]

        for label in labels:
            try:
                movie_data[label] = table_data[label]
            except:
                run_text += "Error, label {} not present in search\n".format(label)
                continue
            else:
                run_text += "Successfully got {}\n".format(label)

        if movie_data != {}:
            run_text += "done.\n\n"
            movie_data.update({'title': movie_title})

            if stats is not None:
                stats.end_movie(movie)
                with stats.lock:
                    stats.succeeded += 1
            print(run_text)
            return movie_data

    print(run_text)

    if stats is not None:
        stats.end_movie(movie)
        with stats.lock:
            stats.failed += 1
        stats.add_failed_movie(movie)


def find_movies(movie_titles, show=False):
    movies_data = []
    analitics = Analitics(movie_titles)

    analitics.start_run()

    pool = ThreadPool(10)
    params = zip(movie_titles, itertools.repeat(analitics))
    movies_data = pool.map(get_movie_data, params)

    analitics.end_run()
    analitics.results()

    return movies_data


def find_movies_data(movies, show=True):

    if isinstance(movies, str):
        try:
            movies = read_movies_from_file(movies)
        except:
            print("Error reading movies from file {}".format(movies))

        return find_movies(movies, show)

    elif isinstance(movies, list):
        return find_movies(movies, show)


def get_actor_set(movies_data):
    # All the actors
    actors = {}

    # Look through all the movies
    for movie_data in movies_data:
        stars = movie_data.get("Starring", None)

        # If there is actors listed
        if stars is not None:
            for star in stars:
                if star in actors:
                    pass


def write_dict_to_csv(dict, file_name):
    with open(file_name, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in dict.items():
            writer.writerow([key, value])


if __name__ == "__main__":
    movies_data = find_movies_data("MW-Movies.txt", show=True)

    with open("movies_data.json", "w") as f:
        f.write(json.dumps(movies_data, indent=4))
