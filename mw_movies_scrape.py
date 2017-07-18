import requests
from bs4 import BeautifulSoup
import json


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
             "limit": 5,
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


def write_data(label, data, file):
    line = label + ","
    for data in data[label]:
        line += data + ","
    line = line[:-1] + "\n"
    file.write(line)


def get_movie_data(movie, file):
    # Just do one for testing
    movie_title = movie
    print(movie_title)

    search_results = search_wikipedia(movie_title)

    if search_results is None:
        print("No search results found")
        return

    movie_data = {}
    # Look through all wikipedia search results
    for search_url in search_results:
        print(search_url)
        request = requests.get(search_url)
        movie_soup = BeautifulSoup(request.text, "lxml")

        table_data = []
        table = movie_soup.find("table", {"class": "infobox"})

        # Cant find the data table
        if table is None:
            print("Cant find table data...")
            continue

        for tr in table.find_all("tr"):
            table_row = tr.text.split("\n")
            table_row = [r for r in table_row if r != ""]
            table_data.append(table_row)

        try:
            table_data = {r[0].strip(): r[1:] for r in table_data}
        except:
            print("Cant remove whitespace...")
            continue

        labels = ["Box office", "Starring", "Running time"]

        for label in labels:
            try:
                movie_data[label] = table_data[label]
            except:
                print("Error, label {} not present in search".format(label))
                continue
            else:
                print("Successfully got {}".format(label))

        if movie_data != {}:
            print("done.\n")
            return {movie_title: movie_data}


def find_movies(movie_titles):
    movies_data = {}

    for movie in movie_titles:
        movie_data = get_movie_data(movie, file)
        name, data = movie_data.items()[0]

        movies_data[name] = data

    return movies_data


def find_movies_data(movies):

    if isinstance(movies, str):
        try:
            movies = read_movies_from_file(movies)
        except:
            print("Error reading movies from file {}".format(movies))

        return find_movies(movies)

    elif isinstance(movies, list):
        return find_movies(movies)


if __name__ == "__main__":
    movies_data = find_movies_data("testing_movies.txt")

    print(json.dumps(movies_data, indent=4))
