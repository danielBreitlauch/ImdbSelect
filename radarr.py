from json import JSONDecodeError
import requests

from Movie import Movie


class MovieNotFoundError(Exception):
    def __init__(self, imdb_id):
        self.imdb_id = imdb_id


class Radarr:
    def __init__(self, url, base_path, api_key, quality_profile):
        self.url = url
        self.base_path = base_path
        self.api_key = api_key
        self.quality_profile = quality_profile

        self.cache_all_movie_data = {}
        self.all_movies_by_imdb = {movie.imdb_id(): movie for movie in self.get_all_movies_in_radarr() if movie.has_imdb_id()}

        for movie in [movie for movie in self.get_all_movies_in_radarr() if not movie.has_imdb_id()]:
            print("warning! this movie does not hav a imdb id: " + str(movie))

    def get_movie(self, imdb_id):
        if imdb_id in self.all_movies_by_imdb:
            return self.all_movies_by_imdb[imdb_id]

        if imdb_id not in self.cache_all_movie_data:
            try:
                r = requests.get(
                    self.url + '/api/movie/lookup/imdb?imdbId=' + imdb_id + '&apikey=' + self.api_key)
                self.cache_all_movie_data[imdb_id] = Movie(r.json(), imdb_id)
            except JSONDecodeError:
                raise MovieNotFoundError(imdb_id)
        return self.cache_all_movie_data[imdb_id]

    def add_movie(self, movie):
        movie.add(self.quality_profile, self.base_path)

        r = requests.post(self.url + '/api/movie?apikey=' + self.api_key, None, movie.raw())

        if r.status_code == 200 and movie.has_imdb_id():
            self.all_movies_by_imdb[movie.imdb_id()] = movie
        return r.status_code

    def remove_movie(self, movie):
        requests.delete(self.url + '/api/movie/' + movie.id() + '?apikey=' + self.api_key)

    def get_all_movies_in_radarr(self):
        r = requests.get(self.url + '/api/movie?apikey=' + self.api_key)
        return [Movie(x) for x in r.json()]

    def get_all_downloaded_movies(self):
        return [movie for movie in self.get_all_movies_in_radarr() if movie.downloaded()]

    def get_all_non_downloaded_movies(self):
        return [movie for movie in self.get_all_movies_in_radarr() if not movie.downloaded()]

    def movie_exist(self, imdb_id):
        return imdb_id in self.all_movies_by_imdb
