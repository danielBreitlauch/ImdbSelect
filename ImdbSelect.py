#!/usr/bin/env python3

from json import JSONDecodeError
from collections import Counter
from plexapi.server import PlexServer

import requests
from imdb import IMDb
import config

ia = IMDb()


def get_movie_data(imdb_id):
    try:
        r = requests.get(
            config.radarr_url + '/api/movie/lookup/imdb?imdbId=' + imdb_id + '&apikey=' + config.radarr_apiKey)
        return r.json()
    except JSONDecodeError:
        return None


def add_movie(movie):
    movie["ProfileId"] = config.radarr_profile
    movie["rootFolderPath"] = config.radarr_base_path
    movie["monitored"] = "true"

    r = requests.post(config.radarr_url + '/api/movie?apikey=' + config.radarr_apiKey, None, movie)
    return r.status_code


def imdb_id_list_from_person(name, role='actor'):
    persons = ia.search_person(name)
    if len(persons) == 0:
        return []

    full_person = ia.get_person(persons[0].getID(), info=["filmography"])

    ids = []
    for kind in full_person['filmography']:
        if role in kind:
            for movie in kind[role]:
                ids.append('tt' + movie.movieID)
    return ids


def most_plex_actors():
    plex = PlexServer(config.plex_url, config.plex_token)
    actors = Counter([role.tag.encode('utf-8') for movie in plex.library.section(config.plex_movie_lib_name).all() for role in movie.roles])
    sorted_limited_actors = sorted(actors.items(), key=lambda x: x[1], reverse=True)[:config.author_min_movie_threshold]
    return [actor[0].decode("utf-8") for actor in sorted_limited_actors]


actors = most_plex_actors()
actors += config.actors

for actor in actors:
    print("adding all movies with: " + actor)
    for imdb_id in imdb_id_list_from_person(actor):
        movie = get_movie_data(imdb_id)
        if not movie:
            continue

        status = add_movie(movie)
        if status / 100 == 4:
            print("\t" + movie['title'] + " exists already.")
        else:
            print("\t" + movie['title'] + " added.")
