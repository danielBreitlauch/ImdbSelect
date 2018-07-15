from imdb import IMDb
import config


class Imdb:
    def __init__(self):
        self.ia = IMDb()

    def imdb_id_list_from_person(self, name, role='actor'):
        persons = self.ia.search_person(name)
        if len(persons) == 0:
            return []

        full_person = self.ia.get_person(persons[0].getID(), info=["filmography"])

        ids = []
        for kind in full_person['filmography']:
            if role in kind:
                for movie in kind[role]:
                    ids.append('tt' + movie.movieID)
        return ids