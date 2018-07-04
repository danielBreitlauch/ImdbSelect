from json import JSONDecodeError

import requests
from imdb import IMDb

url = 'http://barkeeper.local.:7878'
apiKey = '601218dcca124ec4a0c877ec3284d8da'
base_path = '/tank/Media/Filme'
profile = '6'

ia = IMDb()

#r = requests.get('http://barkeeper.local.:7878/api/profile?apikey=601218dcca124ec4a0c877ec3284d8da')
#print(r.text)


def add_movie(imdb_id):
    try:
        print("adding: " + imdb_id)
        r = requests.get(url + '/api/movie/lookup/imdb?imdbId=' + imdb_id + '&apikey=' + apiKey)
        movie = r.json()
    except JSONDecodeError:
        return

    movie["ProfileId"] = profile
    movie["rootFolderPath"] = base_path
    movie["monitored"] = "true"

    print("adding: " + movie['title'])
    requests.post(url + '/api/movie?apikey=' + apiKey, None, movie)


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


for imdb_id in imdb_id_list_from_person('Johnny Depp'):
    add_movie(imdb_id)
