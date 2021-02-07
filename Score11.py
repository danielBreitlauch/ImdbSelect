from bs4 import BeautifulSoup
import re
from colorama import Fore, Style
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session


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
        self.session = Session()
        self.session.mount('https://', HTTPAdapter(
            max_retries=Retry(total=5, status_forcelist=[500, 503])
        ))

    def imdb_ids_for_sneak(self, city, cinema=None, screening=None, minimum_rating=0.0, maximum_rating=9999.0):
        movies = self.score11_movies(city, cinema, screening, minimum_rating, maximum_rating)
        imdb_ids = []
        for count, movie in enumerate(movies, start=1):
            print("[ " + str(count) + "/" + str(len(movies)) + " ]")
            print("\t" + movie['title'] + " (" + str(movie['year']) + ") score11: " + str(movie['rating']))
            imdb_id = self.imdb_id_for_movie(movie)
            if imdb_id:
                imdb_ids.append(imdb_id)
            else:
                print(Fore.RED + '\tNo match on imdb found' + Style.RESET_ALL)
        return imdb_ids

    def score11_movies(self, city, cinema=None, screening=None, minimum_rating=0.0, maximum_rating=9999.0):
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

        score11_movies = {}  # is a dict to keep the movie list unique
        for cinema in cinemas:
            for screening in screenings[cinema]:
                score11_movies.update(self.get_sneak_titles(city, cinema, screening))

        score11_movies = sorted(score11_movies.values(), key=lambda m: m['rating'])
        return [m for m in score11_movies if minimum_rating < m['rating'] <= maximum_rating]

    def imdb_id_for_movie(self, movie):
        match = self.imdb.search_movie(movie['title'], movie['year'], False)
        if match:
            return 'tt' + match.movieID

        self.get_movie_details(movie)
        for title, year in movie['title_years']:
            match = self.imdb.search_movie(title, year, False)
            if match:
                return 'tt' + match.movieID

        return None

    def sneak_cinema_options(self, city):
        r = self.session.get(Score11.base_url + '/sneakpreview.php', params={Score11.city_param: city})
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
        r = self.session.get(Score11.base_url + '/sneakpreview.php', params=params)
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
            r = self.session.get(Score11.base_url + '/sneakpreview.php', params=params)
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
                'rating': float(cells[5].get_text()),
                'votes': int(cells[6].get_text()),
                'link': cells[3].find("a").get('href'),
            }

            if is_int(extended[:4]):
                movie['year'] = int(extended[:4])
            else:
                movie['year'] = -1

            movies[movie['title'] + str(movie['year'])] = movie
        return movies

    def get_movie_details(self, movie):
        r = self.session.get(Score11.base_url + movie['link'])
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

def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
