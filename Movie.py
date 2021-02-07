from dateutil import parser


class Movie:
    def __init__(self, json, imdb_id=None):
        self.json = json
        if imdb_id and not self.has_imdb_id():
            self.json['imdbId'] = imdb_id

    def add(self, quality_profile, base_path):
        self.json["ProfileId"] = quality_profile
        self.json["rootFolderPath"] = base_path
        self.json["monitored"] = "true"

    def raw(self):
        return self.json

    def id(self):
        return str(self.json['id'])

    def url(self):
        if self.has_imdb_id():
            return "https://www.imdb.com/title/" + self.json['imdbId']
        else:
            return ""

    def rating_above(self, rating_above):
        return 'ratings' in self.json and 'value' in self.json['ratings'] and self.json['ratings']['value'] > rating_above

    def votes_above(self, votes_above):
        return 'ratings' in self.json and 'votes' in self.json['ratings'] and self.json['ratings']['votes'] > votes_above

    def rating(self):
        if 'ratings' in self.json and 'value' in self.json['ratings'] and 'votes' in self.json['ratings']:
            return "ratings: " + str(self.json['ratings']['value']) + "/10, votes: " + str(self.json['ratings']['votes'])
        else:
            return "<has no ratings>"

    def year(self):
        if 'year' in self.json:
            return str(self.json['year'])
        else:
            return '<has no year>'

    def title(self):
        if 'title' in self.json:
            return self.json['title']
        else:
            return '<has no title>'

    def downloaded(self):
        return self.json['downloaded']

    def has_imdb_id(self):
        return 'imdbId' in self.json

    def imdb_id(self):
        return self.json['imdbId']

    def tmdb_id(self):
        return self.json['tmdbId']

    def added_date(self):
        return parser.parse(self.json['added'])

    def short_string(self):
        return self.title() + " (" + self.year() + ")"

    def __str__(self):
        return self.title() + " (" + self.year() + ") - " + self.url() + " (" + self.rating() + ")"
