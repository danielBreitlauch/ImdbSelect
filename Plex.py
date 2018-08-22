from plexapi.server import PlexServer
from collections import Counter


class Plex:
    def __init__(self, url, token, movie_lib_name):
        self.plex = PlexServer(url, token)
        self.movie_lib_name = movie_lib_name

    def most_common_actors(self, author_min_movie_threshold):
        actors = Counter([role.tag.encode('utf-8') for movie in
                          self.plex.library.section(self.movie_lib_name).all() for role in movie.roles])

        sorted_actors = sorted(actors.items(), key=lambda x: x[1], reverse=True)
        sorted_limited_actors = sorted_actors[:author_min_movie_threshold]
        return {actor[0].decode("utf-8") for actor in sorted_limited_actors}
