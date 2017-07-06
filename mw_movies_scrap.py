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

    first_search_url = search_results[-1][0]

    return first_search_url


if __name__ == "__main__":
    movies_titles = read_movies_from_file("MW-Movies.dat")

    # Just do one for testing
    movie_title = movies_titles[0]
    print(movie_title)


    search_url = search_wikipedia(movie_title)
    print(search_url)


    request = requests.get(search_url)
    movie_soup = BeautifulSoup(request.text, "html.parser")

    with open("bravehear_tables.html", "w") as file:
        for row in movie_soup.find_all("table", {"class": "infobox"}):
            try:
                file.write(row)
                file.write("\n\n")
            except:
                pass
