#!/usr/bin/env python3

import config
from ImdbSelect import ImdbSelect
from Plex import Plex

plex = Plex(config.plex_url, config.plex_token, config.plex_movie_lib_name, config.author_min_movie_threshold)
worker = ImdbSelect(config)


actors = plex.most_common_actors()
actors += config.actors

worker.add_all(actors, manual=True)
