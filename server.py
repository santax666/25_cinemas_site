from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
from werkzeug.contrib.cache import SimpleCache


class afisha:

    def __init__(self):
        header = {'Host': 'mobile.api.afisha.ru', 'User-Agent': 'okhttp/3.6.0',
                  'X-Afisha-Session-ID': '', 'X-Afisha-City-ID': '2',
                  'X-Afisha-Key': '41D338CEC1884CC88F95A7D0A4803E7F',
                  'X-Afisha-ClientVersion': '3.3.5',
                  'X-Afisha-Platform': 'Android'}
        self.url = 'https://mobile.api.afisha.ru/v2.5'
        self.session = requests.Session()
        self.session.headers = header
        self.session.verify = False

    def schedule(self, date=1, offset=0, limit=1000):
        params = {'themeID': 2, 'sortOrder': 0, 'dateRangeID': date,
                  'range.Limit': limit, 'range.Offset': offset}
        films_url = '{}/themeevents'.format(self.url)
        return self.session.get(films_url, params=params).json()

    def film_info(self, film_id=0):
        film_url = '{0}/creations/16-{1}'.format(self.url, film_id)
        return self.session.get(film_url).json()

    def search(self, name, offset=0, limit=1000):
        arg = {'searchString': name, 'searchThemeID': 2,
               'range.Offset': offset, 'range.Limit': limit}
        search_url = '{}/searchitems'.format(self.url)
        return self.session.get(search_url, params=arg).json()


def film_id_from_kp_plus(name, year):
    url = 'https://suggest-kinopoisk.yandex.net/suggest-kinopoisk'
    payload = {'srv': 'kinopoisk', 'part': name,
               '_': int(datetime.now().timestamp())}
    films_data = requests.get(url, params=payload).json()[2]
    for film_info in films_data:
        film = json.loads(film_info)
        if film['searchObjectType'] == 'COBJECT':
            if film.get('title') == name and film['years'][0] == year:
                return str(film['entityId'])


def kp_imdb_ratings(kp_id):
    cache_url = 'http://webcache.googleusercontent.com/search?q=cache:'
    url = '{0}https://www.kinopoisk.ru/film/{1}'.format(cache_url, kp_id)
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    kp_rate = getattr(soup.find('span', {'class': 'rating_ball'}), 'text', '-')
    kp_vote = getattr(soup.find('span', {'class': 'ratingCount'}), 'text', '-')
    imdb_style = 'color:#999;font:100 11px tahoma, verdana'
    imdb = getattr(soup.find('div', {'style': imdb_style}), 'text', '-')
    return (kp_rate, kp_vote,), imdb


app = Flask(__name__)
cache = SimpleCache()
api = afisha()


@app.route('/')
def show_films_schedule():
    cache_time = 12 * 60 * 60
    films = cache.get('schedule')
    if films is None:
        films_info = api.schedule()
        films = [x for x in films_info['Items'] if x['PlaceCount'] > 29]
        cache.set('schedule', films, cache_time)
    return render_template('films.html', films=films, kind=('schedule', '',))


@app.route('/film/<int:film_id>')
def show_film_info(film_id):
    cache_time = 12 * 60 * 60
    film = cache.get(film_id)
    if film is None:
        film = api.film_info(film_id)['Data']
        film['Tags'] = ', '.join(d['Name'] for d in film['Tags'])
        film['kp_id'] = film_id_from_kp_plus(film['Name'], int(film['Year']))
        film['kp'], film['imdb'] = kp_imdb_ratings(film['kp_id'])
        release = film['ReleaseRusDate']
        if release is not None:
            film['Exit'] = datetime.strptime(release[:-6], "%Y-%m-%dT%H:%M:%S")
        cache.set(film_id, film, cache_time)
    return render_template('film.html', film=film)


@app.route('/search')
def show_found_films():
    films = []
    query = request.args.get('query', '')
    if query != '':
        films = api.search(query)['Items']
    return render_template('films.html', films=films, kind=('search', query,))


@app.route('/api/<kind>')
def get_api(kind):
    if kind == 'info':
        return render_template('api.html')
    api_dict = {'schedule': (api.schedule, request.args.get('date', 1),),
                'search': (api.search, request.args.get('name', ''),),
                'film': (api.film_info, request.args.get('id', 0),)}
    api_func, func_arg = api_dict[kind]
    return jsonify(api_func(func_arg))


if __name__ == '__main__':
    app.run()
