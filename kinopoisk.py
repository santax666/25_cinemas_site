import re
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup


def get_film_id(name_film, year):
    name = re.sub(r'(-)(\d+)$', r' \2', name_film)
    url = 'https://suggest-kinopoisk.yandex.net/suggest-kinopoisk'
    payload = {'srv': 'kinopoisk', 'part': name,
               '_': int(datetime.now().timestamp())}
    films_data = requests.get(url, params=payload).json()[2]
    for film_info in films_data:
        film = json.loads(film_info)
        if film['searchObjectType'] == 'COBJECT':
            if film.get('title') == name and film['years'][0] == year:
                return str(film['entityId'])


def get_ratings(kp_id):
    cache_url = 'http://webcache.googleusercontent.com/search?q=cache:'
    url = '{0}https://www.kinopoisk.ru/film/{1}'.format(cache_url, kp_id)
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    kp_rate = getattr(soup.find('span', {'class': 'rating_ball'}), 'text', None)
    kp_vote = getattr(soup.find('span', {'class': 'ratingCount'}), 'text', None)
    imdb_style = 'color:#999;font:100 11px tahoma, verdana'
    imdb = getattr(soup.find('div', {'style': imdb_style}), 'text', None)
    return (kp_rate, kp_vote,), imdb
