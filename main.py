#!/usr/bin/env python3

import config
from ImdbSelect import ImdbSelect
from Plex import Plex

plex = Plex(config.plex_url, config.plex_token, config.plex_movie_lib_name, config.author_min_movie_threshold)
worker = ImdbSelect(config)


actors = plex.most_common_actors()
actors -= config.actors_blacklist

print("Most favorite plex actors: " + str(actors))
print("Adding configured actors: " + str(config.actors))
actors = actors.union(config.actors)

worker.add_all(actors, rating_above=7.5, votes_above=300)
worker.add_all(actors, rating_above=6, votes_above=100, manual=True)
worker.add_all(actors, manual=True)
