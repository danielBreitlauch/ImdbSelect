import requests
from bs4 import BeautifulSoup
import re
from Imdb import Imdb
from colorama import Fore, Style


class Score11:

    base_url = 'https://www.score11.de'
    city_param = 'SPO'
    cinema_param = 'SPK'
    screening_param = 'SPN'
    entries_per_page_param = 'PGL'
    page_param = 'TPG'

    params = {'QU': 0, 'TVE': 'DE', entries_per_page_param: 99}

    def __init__(self, imdb):
        self.imdb = imdb

    def imdb_id_list_from_sneak(self, city, cinema=None, screening=None, minimum_rating=0.0):
        if not cinema:
            cinemas = self.sneak_cinema_options(city)
            print("Found these cinemas: " + ', '.join(cinemas))
        else:
            cinemas = [cinema]

        if not screening:
            screenings = {}
            for cinema in cinemas:
                screenings[cinema] = self.sneak_screening_options(city, cinema)
                print("Cinemas: " + cinema + "\nFound these screening: " + ', '.join(screenings[cinema]))
        else:
            screenings = {cinema: [screening]}

        movies = {}  # is a dict to keep the movie list unique
        for cinema in cinemas:
            for screening in screenings[cinema]:
                movies.update(self.get_sneak_titles(city, cinema, screening))

        movies = sorted(movies.values(), key=lambda m: m['rating'])
        movies = [m for m in movies if m['rating'] > minimum_rating]
        return self.search_movies(movies)

    def search_movies(self, movies):
        imdb_ids = []
        for count, movie in enumerate(movies, start=1):
            print("[ " + str(count) + "/" + str(len(movies)) + " ]")
            print("\t" + movie['title'] + " (" + str(movie['year']) + ") score11: " + str(movie['rating']))
            match = self.imdb.search_movie(movie['title'], movie['year'], False)
            if match:
                print("\tFound: " + match['title'] + " (" + str(match['year']) + ")")
                imdb_ids.append(match.movieID)
                continue

            self.get_movie_details(movie)
            found = False
            for title, year in movie['title_years']:
                print("\tTry: " + title + " (" + str(year) + ")")
                match = self.imdb.search_movie(title, year, False)
                if match:
                    print("\tFound: " + match['title'] + " (" + str(match['year']) + ")")
                    imdb_ids.append(match.movieID)
                    found = True
                    break
            if not found:
                print(Fore.RED + '\tNo match' + Style.RESET_ALL)
        return imdb_ids

    def sneak_cinema_options(self, city):
        r = requests.get(Score11.base_url + '/sneakpreview.php', params={Score11.city_param: city})
        soup = BeautifulSoup(r.text, 'html.parser')
        select = soup.find('select', {'name': Score11.cinema_param})
        options = select.findAll('option')
        options = [o.get_text() for o in options[1:]]
        for index, o in enumerate(reversed(options)):
            for i_index, ro in enumerate(options[:len(options) - index - 1]):
                options[i_index] = ro.replace(o, u'')
        return options

    def sneak_screening_options(self, city, cinema):
        params = {
            Score11.city_param: city,
            Score11.cinema_param: cinema
        }
        r = requests.get(Score11.base_url + '/sneakpreview.php', params=params)
        soup = BeautifulSoup(r.text, 'html.parser')
        select = soup.find('select', {'name': Score11.screening_param})
        options = select.findAll('option')
        options = [o.get_text() for o in options[1:]]
        for index, o in enumerate(reversed(options)):
            for i_index, ro in enumerate(options[:len(options) - index - 1]):
                options[i_index] = ro.replace(o, u'')

        return options

    def get_sneak_titles(self, city, cinema, screening):
        params = Score11.params
        params[Score11.city_param] = city
        params[Score11.cinema_param] = cinema
        params[Score11.screening_param] = screening
        movies = {}
        page = 1
        while True:
            params[Score11.page_param] = page
            r = requests.get(Score11.base_url + '/sneakpreview.php', params=params)
            page_movies = self.parse_page(r.text)
            movies.update(page_movies)
            page += 1
            if len(page_movies) == 0:
                return movies

    def parse_page(self, content):
        movies = {}
        soup = BeautifulSoup(content, 'html.parser')
        rows = soup.findAll('tr', {'class': "lvct2"})
        for row in rows:
            cells = row.find_all("td")
            extended = cells[3].find(text=True, recursive=False).strip()
            movie = {
                'date': cells[0].get_text().strip().replace(u'\xa0', u' '),
                'title': cells[3].find("a").get_text().replace(u'\x96', u'-'),
                'year': int(extended[:4]),
                'rating': float(cells[5].get_text()),
                'votes': int(cells[6].get_text()),
                'link': cells[3].find("a").get('href'),
            }

            movies[movie['title'] + str(movie['year'])] = movie
        return movies

    def get_movie_details(self, movie):
        r = requests.get(Score11.base_url + movie['link'])
        soup = BeautifulSoup(r.text, 'html.parser')
        title_years = []
        title, year = self.extract_title_year(soup.find('h1', {'class': "mt1"}).get_text())
        if title and year:
            title_years.append((title, year))

        for title_year in soup.findAll('span', {'class': "mt2"}):
            title, year = self.extract_title_year(title_year.get_text())
            if title and year:
                title_years.append((title, year))

        movie['title_years'] = title_years

    def extract_title_year(self, title_year):
        m = re.search('(.*) \(.*(\d\d\d\d)\)', title_year)
        if m:
            title = m.group(1)
            year = int(m.group(2))
            return title, year
        return None, None


s = Score11(Imdb())

for x in s.imdb_id_list_from_sneak('Paderborn', 'Cineplex', minimum_rating=8.0):
    print(x)
