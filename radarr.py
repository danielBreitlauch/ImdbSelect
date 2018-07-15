from json import JSONDecodeError
import requests
import config


class Radarr:
    def __init__(self):
        self.cache_all_movie_data = {}
        self.cache_all_movies_in_radarr = None
        self.cache_all_movies_imdb_in_radarr = {}

    def get_movie_data(self, imdb_id):
        if not self.cache_all_movies_in_radarr:
            all = self.get_all_movies_in_radarr()
            self.cache_all_movies_in_radarr = set([movie['title'] + str(movie['year']) for movie in all])
            self.cache_all_movies_imdb_in_radarr = {movie['imdbId']: movie for movie in all}

        if imdb_id in self.cache_all_movies_imdb_in_radarr:
            return self.cache_all_movies_imdb_in_radarr[imdb_id]

        if imdb_id not in self.cache_all_movie_data:
            try:
                r = requests.get(
                    config.radarr_url + '/api/movie/lookup/imdb?imdbId=' + imdb_id + '&apikey=' + config.radarr_apiKey)
                self.cache_all_movie_data[imdb_id] = r.json()
            except JSONDecodeError:
                return None
        return self.cache_all_movie_data[imdb_id]

    def add_movie(self, movie):
        movie["ProfileId"] = config.radarr_profile
        movie["rootFolderPath"] = config.radarr_base_path
        movie["monitored"] = "true"
        # TODO: add command to search the movie

        r = requests.post(config.radarr_url + '/api/movie?apikey=' + config.radarr_apiKey, None, movie)
        return r.status_code

    def remove_movie(self, movie):
        requests.delete(config.radarr_url + '/api/movie/' + str(movie['id']) + '?apikey=' + config.radarr_apiKey)

    def get_all_movies_in_radarr(self):
        r = requests.get(config.radarr_url + '/api/movie?apikey=' + config.radarr_apiKey)
        return r.json()

    def get_all_downloaded_movies(self):
        return [movie for movie in self.get_all_movies_in_radarr() if movie['downloaded']]

    def get_all_non_downloaded_movies(self):
        return [movie for movie in self.get_all_movies_in_radarr() if not movie['downloaded']]

    def movie_exist(self, movie=None, imdb_id=None):
        if not self.cache_all_movies_in_radarr:
            all = self.get_all_movies_in_radarr()
            self.cache_all_movies_in_radarr = set([movie['title'] + str(movie['year']) for movie in all])
            self.cache_all_movies_imdb_in_radarr = {movie['imdbId']:movie for movie in all}

        if imdb_id:
            return imdb_id in self.cache_all_movies_imdb_in_radarr
        else:
            return movie['title'] + str(movie['year']) in self.cache_all_movies_in_radarr

