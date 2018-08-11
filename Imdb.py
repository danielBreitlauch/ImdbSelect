from imdb import IMDb


class Imdb:
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

    def get_movie_title(self, imdb_id):
        if imdb_id in self.title_cache:
            return self.title_cache[imdb_id]

        movie = self.ia.get_movie(self.transform_id(imdb_id))
        title = movie['title']
        self.title_cache[imdb_id] = title
        return title
