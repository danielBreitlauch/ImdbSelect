from datetime import datetime, timedelta, timezone

from Imdb import Imdb
from Preferences import Preferences
from Radarr import Radarr, MovieNotFoundError
from colorama import Fore, Style


class ImdbSelect:
    def __init__(self, config):
        self.radarr = Radarr(config.radarr_url, config.radarr_base_path, config.radarr_api_key, config.radarr_quality_profile)
        self.imdb = Imdb()
        self.ask = Preferences(self.imdb)

    def get_movies_from_actors(self, actors):
        movies = []
        for actor in actors:
            for imdb_id in self.imdb.imdb_id_list_from_person(actor):
                try:
                    movies.append(self.radarr.get_movie(imdb_id))
                except MovieNotFoundError:
                    pass
        return movies

    def add_all(self, actors, rating_above=0, votes_above=0, manual=False, retry=True):
        for count, actor in enumerate(actors):
            print("[ " + str(count) + "/" + str(len(actors)) + " ] going through all movies with: " + actor)
            movie_data_map, error_list = self.collect_movie_data(actor, retry)
            err_title = [self.imdb.get_movie_title_year(imdb_id) for imdb_id in error_list]
            print('Could not find ' + str(len(error_list)) + ': ' + ', '.join(err_title))
            self.choices(movie_data_map, rating_above, votes_above, manual, prepare=True)
            movies_to_add = self.choices(movie_data_map, rating_above, votes_above, manual)
            self.add_movies(movies_to_add)

    def collect_movie_data(self, actor, retry=True):
        movie_data_map = {}
        error_list = []
        movies = self.imdb.imdb_id_list_from_person(actor)
        print("[ " + str(len(movies)) + " ] ", end='', flush=True)
        next_print = 10
        for count, imdb_id in enumerate(movies):
            try:
                if not self.ask.is_answered_no(imdb_id) and not self.radarr.movie_exist(imdb_id):
                    movie_data_map[imdb_id] = self.radarr.get_movie(imdb_id, retry)
                print('.', end='', flush=True)
            except MovieNotFoundError:
                error_list.append(imdb_id)
                print(Fore.RED + '.' + Style.RESET_ALL, end='', flush=True)

            if 100 * count // len(movies) >= next_print:
                print(str(next_print) + "%", end='', flush=True)
                next_print += 10
        print("/")
        return movie_data_map, error_list

    def choices(self, movie_data_map, rating_above=None, votes_above=None, manual=False, prepare=False):
        movies_to_add = []
        for imdb_id, movie in movie_data_map.items():
            if rating_above and votes_above:
                if not movie.rating_above(rating_above):
                    if not prepare:
                        print("\t" + str(movie) + " has too low ratings")
                    continue
                if not movie.votes_above(votes_above):
                    if not prepare:
                        print("\t\t" + str(movie) + " has not enough votes")
                    continue

                if manual:
                    if self.ask.ask(imdb_id, movie, prepare):
                        movies_to_add.append(movie)
                else:
                    if not prepare:
                        print(str(movie) + " has good ratings")
                    movies_to_add.append(movie)
            elif manual and self.ask.ask(imdb_id, movie, prepare):
                    movies_to_add.append(movie)

        return movies_to_add

    def add_movies(self, movies_to_add):
        for movie in movies_to_add:
            status = self.radarr.add_movie(movie)
            if status / 100 == 4:
                print("\t" + movie.short_string() + " exists already.")
            else:
                print("\t" + movie.short_string() + " added.")

    def delete_non_downloaded_movies_added_ago(self, time_delta=timedelta(days=1)):
        movies = self.radarr.get_all_non_downloaded_movies()
        filtered = [movie for movie in movies if movie.added_date() > datetime.now(timezone.utc) - time_delta]

        count = len(filtered)
        for movie in filtered:
            print(count, movie.title())
            count -= 1
            self.radarr.remove_movie(movie)


