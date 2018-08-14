import unicodedata
import sys

from imdb import IMDb


class Imdb:

    punctuation = dict.fromkeys(i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith('P'))

    def __init__(self):
        self.ia = IMDb()
        self.summary_cache = {}
        self.title_cache = {}

    def imdb_id_list_from_person(self, name, role='actx', filter='movie'):
        persons = self.ia.search_person(name)
        if len(persons) == 0:
            return []

        full_person = self.ia.get_person(persons[0].getID(), info=["filmography"])

        ids = []
        for kind in full_person['filmography']:
            if role == 'actx':
                if 'actor' in kind:
                    for movie in kind['actor']:
                        if movie.data['kind'] == filter:
                            ids.append('tt' + movie.movieID)
                if 'actress' in kind:
                    for movie in kind['actress']:
                        if movie.data['kind'] == filter:
                            ids.append('tt' + movie.movieID)
            elif role in kind:
                for movie in kind[role]:
                    if movie.data['kind'] == filter:
                        ids.append('tt' + movie.movieID)
        return ids

    def transform_id(self, imdb_id):
        return imdb_id[2:]

    def get_movie_summary(self, imdb_id):
        if imdb_id in self.summary_cache:
            return self.summary_cache[imdb_id]

        movie = self.ia.get_movie(self.transform_id(imdb_id))
        summary = movie.summary()
        self.summary_cache[imdb_id] = summary
        return summary

    def get_movie_title_year(self, imdb_id):
        if imdb_id in self.title_cache:
            return self.title_cache[imdb_id]

        movie = self.ia.get_movie(self.transform_id(imdb_id))
        if 'year' in movie:
            title = movie['title'] + " (" + movie['year'] + ")"
        else:
            title = movie['title'] + " (????)"
        self.title_cache[imdb_id] = title
        return title

    def compare_wo_punctuation(self, name1, name2):
        name1 = name1.translate(Imdb.punctuation).replace('  ', ' ').lower()
        name2 = name2.translate(Imdb.punctuation).replace('  ', ' ').lower()
        return name1 == name2

    def search_movie(self, title, year=None, strict=True):
        candidates = []
        for movie in self.ia.search_movie(title):
            if movie['kind'] != 'movie':
                continue
            if movie['title'] == title or not strict and self.compare_wo_punctuation(movie['title'], title):
                candidates.append(movie)
                continue
            self.ia.update(movie, 'release info')
            if 'akas' in movie:
                for aka in movie['akas']:
                    if title.lower() == aka.split('::')[0].lower():
                        candidates.append(movie)
                        break

        for movie in candidates:
            if not year or movie['year'] == year:
                return movie

            if movie['title'] == title and movie['year'] == year + 1:
                return movie

            self.ia.update(movie, 'release dates')
            if 'release dates' in movie.data:
                for date in movie['release dates']:
                    whole_date = date.split('::')[1]
                    if str(year) in whole_date:
                        return movie
                    if movie['title'] == title and str(year + 1) in whole_date and 'December' in whole_date:
                        return movie
        return None
