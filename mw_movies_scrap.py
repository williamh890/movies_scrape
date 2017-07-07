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
        isMovie = True
        data_labels = ["Box office", "Starring", "Running time"]
        try:
            data = [table_data[label] for label in data_labels]
        except:
            print("Error, not all labels present in {}".format(str(data_labels)))
            continue
        else:
            file.write(movie_title + ",\n")

        for label in data_labels:
            print("Writing label {} to file".format(label))
            try:
                write_data(label, table_data, file)
                file.write(",\n")
            except:
                continue
        print("done.\n")
        return


if __name__ == "__main__":
    movie_titles = read_movies_from_file("MW-Movies.dat")
    with open("movie_data.csv", "w") as file:
        for movie in movie_titles:
            get_movie_data(movie, file)
