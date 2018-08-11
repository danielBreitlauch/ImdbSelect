import jsonpickle


class FailedToGetMovies:
    def __init__(self):
        self.file_name = "failedToGetMovies.db"
        self.failed = self.load()

    def save(self):
        with open(self.file_name, 'w') as f:
            f.write(jsonpickle.encode(self.failed))

    def load(self):
        try:
            with open(self.file_name, "r") as f:
                return jsonpickle.decode(f.read())
        except IOError:
            return {}

    def failed_already(self, imdb_id):
        return imdb_id in self.failed

    def mark_failed(self, imdb_id):
        self.failed[imdb_id] = True
        self.save()
