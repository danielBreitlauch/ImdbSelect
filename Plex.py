from plexapi.server import PlexServer
from collections import Counter
import config


class Plex():
    def __init__(self):
        self.plex = PlexServer(config.plex_url, config.plex_token)

    def most_plex_actors(self):
        actors = Counter(
            [role.tag.encode('utf-8') for movie in self.plex.library.section(config.plex_movie_lib_name).all() for role in
             movie.roles])
        sorted_limited_actors = sorted(actors.items(), key=lambda x: x[1], reverse=True)[
                                :config.author_min_movie_threshold]
        return [actor[0].decode("utf-8") for actor in sorted_limited_actors]

