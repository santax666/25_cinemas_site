import re
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup


def get_film_id(film_name, year):
    film = re.sub(r'(-)(\d+)$', r' \2', film_name)
    url = 'https://suggest-kinopoisk.yandex.net/suggest-kinopoisk'
    query = {'srv': 'kinopoisk', 'part': film, '_': datetime.now().timestamp()}
    content = requests.get(url, params=query).json()[2]
    films_data = [json.loads(x) for x in content]
    films = [x for x in films_data if x['searchObjectType'] == 'COBJECT']
    for film_info in films:
        if film_info.get('title') == film and film_info['years'][0] == year:
            return str(film_info['entityId'])
    else:
        return str(films[0]['entityId'])


def get_ratings(kp_id):
    cache_url = 'http://webcache.googleusercontent.com/search?q=cache:'
    url = '{0}https://www.kinopoisk.ru/film/{1}'.format(cache_url, kp_id)
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    kp_rate = getattr(soup.find('span', {'class': 'rating_ball'}), 'text', None)
    kp_vote = getattr(soup.find('span', {'class': 'ratingCount'}), 'text', None)
    imdb_style = 'color:#999;font:100 11px tahoma, verdana'
    imdb = getattr(soup.find('div', {'style': imdb_style}), 'text', None)
    return (kp_rate, kp_vote,), imdb
