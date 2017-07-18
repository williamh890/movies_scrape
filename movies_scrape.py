import requests
from bs4 import BeautifulSoup
import json
import time
from multiprocessing.dummy import Pool as ThreadPool
import threading
import itertools


class Analitics(object):
    def __init__(self):
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

        if len(self.failed_movies) > 1:
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


class FileNotFoundError(object):
    pass


class ScrapeMovieData(object):

    def __init__(self, movies):
        self.analitics = Analitics()

        if isinstance(movies, str):
            try:
                self.movies = self.__read_movies_from_file(movies)
            except:
                raise FileNotFoundError("File {} not found".format(movies))

        elif isinstance(movies, list):
            self.movies = movies

        else:
            raise ValueError("Value passed to constructor must be a txt file " +
                             "with movies or a list of movie names")

    def run(self):
        movies_data = []

        self.analitics.start_run()

        pool = ThreadPool(10)
        params = zip(self.movies, itertools.repeat(self.analitics))
        movies_data = pool.map(self.__get_movie_data, params)

        self.analitics.end_run()
        self.analitics.results()

        return movies_data

    def __read_movies_from_file(self, file):
        movies = []
        with open(file, "r") as movies_file:
            for movie in movies_file:
                movies.append(movie.strip())

        return movies

    def __search_wikipedia(self, movie):
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

    def __get_movie_data(self, params):
        return self.get_movie_data(*params)

    def get_movie_data(self, movie, stats=None):
        run_text = ""
        stats = self.statis if stats is None else stats

        if stats is not None:
            stats.start_movie(movie)

        run_text += movie + "\n"

        search_results = self.__search_wikipedia(movie)

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

            labels = ["Box office", "Starring", "Running time", "Release date", "Budget", "Country"]

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
                movie_data.update({'title': movie})

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


class Actor(object):
    def __init__(self, name):
        self.name = name
        self.movies = set()

    def add_movie(self, movie):
        self.movies.add(movie)


def get_actor_set(movies):
    # All the actors
    actors = {}

    # Look through all the movies
    for movie in movies:
        stars = movie.get("Starring", None)

        # If there is actors listed
        if stars is not None:
            for star in stars:
                if star in actors:
                    pass


def write_movie_data(filename, outfile="movies_data.json"):
    scraper = ScrapeMovieData(filename)
    movies_data = scraper.run()

    with open(outfile, "w") as f:
        f.write(json.dumps(movies_data, indent=4))


def get_total_watchtime(movies, unit="minutes"):
    runtimes = [(m['title'], m["Running time"][0].split()[0])
                for m in movies if m.get("Running time") is not None]

    total_watchtime = 0
    for t in runtimes:
        try:
            total_watchtime += int(t[1])
        except Exception:
            pass

    return {
        'seconds': total_watchtime * 60,
        'minutes': total_watchtime,
        'hours': total_watchtime / 60,
        'days': total_watchtime / (60 * 24)
    }.get(unit, total_watchtime)


def test_total_watchtimes():
    with open("movies_data.json", "r") as f:
        movies = json.loads(f.read())

    watchtime_days = get_total_watchtime(movies, unit="days")
    watchtime_hrs = get_total_watchtime(movies, unit="hours")
    print("Time watched: {} days or {} hours".format(watchtime_days, watchtime_hrs))


if __name__ == "__main__":
    write_movie_data("MW-Movies.txt")

    with open("movies_data.json", "r") as f:
        movies = json.loads(f.read())
        get_actor_set(movies)
