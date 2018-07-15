#!/usr/bin/env python3

import config
from ImdbSelect import ImdbSelect
from Plex import Plex

plex = Plex()
worker = ImdbSelect()

# actors = plex.most_plex_actors()
actors = config.actors

worker.add_all(actors, manual=True)
