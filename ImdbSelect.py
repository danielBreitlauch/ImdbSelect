from dateutil import parser
from datetime import datetime, timedelta, timezone

from Imdb import Imdb
from Preferences import Preferences
from Radarr import Radarr


class ImdbSelect():
    def __init__(self):
        self.ask = Preferences()
        self.imdb = Imdb()
        self.radarr = Radarr()

    def get_movies_from_actors(self, actors):
        movies = []
        for actor in actors:
            for imdb_id in self.imdb.imdb_id_list_from_person(actor):
                movie = self.radarr.get_movie_data(imdb_id)
                if movie:
                    movies.append(movie)
        return movies

    def collect_movie_data(self, actor):
        movie_data_map = {}
        for imdb_id in self.imdb.imdb_id_list_from_person(actor):
            if self.ask.is_answered_no(imdb_id):
                print("\t" + imdb_id + " answered no already.")
                continue

            movie = self.radarr.get_movie_data(imdb_id)
            if not movie:
                continue
            if self.radarr.movie_exist(imdb_id=imdb_id):
                print("\t" + movie['title'] + " (" + str(movie['year']) + ") exists already.")
                continue

            if not self.ask.is_answered(imdb_id):
                print("\t" + movie['title'] + " (" + str(movie['year']) + ") will ask.")

            movie_data_map[imdb_id] = movie
        return movie_data_map

    def choices(self, movie_data_map, rating_above=0, votes_above=0, manual=False):
        movies_to_add = []
        for imdb_id, movie in movie_data_map.items():
            if manual:
                add = self.ask.ask(imdb_id, movie)
            else:
                add = movie['ratings']['votes'] > votes_above and movie['ratings']['value'] > rating_above

            if add:
                movies_to_add.append(movie)
        return movies_to_add

    def add_movies(self, movies_to_add):
        for movie in movies_to_add:
            status = self.radarr.add_movie(movie)
            if status / 100 == 4:
                print("\t" + movie['title'] + " exists already.")
            else:
                print("\t" + movie['title'] + " added.")

    def add_all(self, actors, rating_above=0, votes_above=0, manual=False):
        for actor in actors:
            print("going through all movies with: " + actor)
            movie_data_map = self.collect_movie_data(actor)
            movies_to_add = self.choices(movie_data_map, rating_above, votes_above, manual)
            self.add_movies(movies_to_add)

    def delete_non_downloaded_movies_added_ago(self, time_delta=timedelta(days=1)):
        movies = self.radarr.get_all_non_downloaded_movies()
        threshold = datetime.now(timezone.utc) - time_delta

        filtered = [movie for movie in movies if parser.parse(movie['added']) > threshold]

        count = len(filtered)
        for movie in filtered:
            print(count, movie['title'])
            count -= 1
            self.radarr.remove_movie(movie)


