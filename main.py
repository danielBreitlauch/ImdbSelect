#!/usr/bin/env python3

import config
from Imdb import Imdb
from ImdbSelect import ImdbSelect
from Plex import Plex
from Score11 import Score11

worker = ImdbSelect(config)

score11 = Score11(Imdb())
imdb_ids = score11.imdb_ids_for_sneak('Paderborn', 'Cineplex', minimum_rating=6.5, maximum_rating=7.0)

worker.add_all_imdb_ids(imdb_ids, rating_above=7.5, votes_above=200, retry=False)
worker.add_all_imdb_ids(imdb_ids, rating_above=6, votes_above=100, manual=True, retry=False)
worker.add_all_imdb_ids(imdb_ids, manual=True, retry=False)


plex = Plex(config.plex_url, config.plex_token, config.plex_movie_lib_name)
actors = plex.most_common_actors(author_min_movie_threshold=10)
actors -= config.actors_blacklist

print("Most favorite plex actors: " + str(actors))
print("Adding configured actors: " + str(config.actors))
actors = actors.union(config.actors)

worker.add_all_actors(actors, rating_above=7.5, votes_above=300, retry=False)
worker.add_all_actors(actors, rating_above=6, votes_above=100, manual=True, retry=False)
worker.add_all_actors(actors, manual=True, retry=False)
