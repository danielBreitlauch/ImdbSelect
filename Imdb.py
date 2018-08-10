from imdb import IMDb


class Imdb:
    def __init__(self):
        self.ia = IMDb()

    def imdb_id_list_from_person(self, name, role='actx'):
        persons = self.ia.search_person(name)
        if len(persons) == 0:
            return []

        full_person = self.ia.get_person(persons[0].getID(), info=["filmography"])

        ids = []
        for kind in full_person['filmography']:
            if role == 'actx':
                if 'actor' in kind:
                    for movie in kind['actor']:
                        ids.append('tt' + movie.movieID)
                if 'actress' in kind:
                    for movie in kind['actress']:
                        ids.append('tt' + movie.movieID)
        return ids
