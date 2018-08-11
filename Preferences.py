import jsonpickle


class Preferences:
    def __init__(self, imdb):
        self.imdb = imdb
        self.file_name = "moviePreference.db"
        self.selections = self.load()

    def save(self):
        with open(self.file_name, 'w') as f:
            f.write(jsonpickle.encode(self.selections))

    def load(self):
        try:
            with open(self.file_name, "r") as f:
                return jsonpickle.decode(f.read())
        except IOError:
            return {}

    def is_answered(self, imdb_id):
        return imdb_id in self.selections

    def is_answered_no(self, imdb_id):
        return imdb_id in self.selections and not self.selections[imdb_id]

    def ask(self, imdb_id, movie, prepare=False):
        if prepare:
            self.imdb.get_movie_summary(imdb_id)
            return

        print(str(movie))

        if imdb_id in self.selections:
            print("Using previous answer: " + str(self.selections[imdb_id]))
            return self.selections[imdb_id]

        for i in range(5):
            inp = input("Adding yes/no/undecided/show summary? (y/n/u/s): ")
            if inp == "y":
                self.selections[imdb_id] = True
                self.save()
                return True
            if inp == "n":
                self.selections[imdb_id] = False
                self.save()
                return False
            if inp == "s":
                print(self.imdb.get_movie_summary(imdb_id) + "\n")
            if inp == "u":
                return False
        return False
