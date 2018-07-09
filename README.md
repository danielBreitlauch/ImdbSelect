## ImdbSelect ##
Automate adding movies to radarr.


About
--------

ImdbSelect adds movies of your favorite actors to radarr.
This can be done explicitly by listing your favorite actors.
But the script can also extract your favorite actors from your plex library.
The script will then check imdb for all movies of these actors and add all new movies to radarr.

Features
--------

* Automatic movie selection of favorite actors
* Automatic extraction of your favorite actors (by counting occurrence in your plex library)
    
Installation
--------

ImdbSelect is compatible with Python 3. 
```
python ./setup.py install
```

Run
--------

Generally edit config.py.
```
cp config_example.py config.py

python imdbSelect.py
```