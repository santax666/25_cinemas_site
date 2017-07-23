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
    url = 'http://www.kinopoisk.ru/rating/{}.xml'.format(kp_id)
    soup = BeautifulSoup(requests.get(url).content, 'lxml')
    kp_rate = kp_votes = imdb_rate = imdb_votes = '-'
    kp = (soup('kp_rating') or [False])[0]
    if kp:
        kp_rate, kp_votes = kp.text, kp['num_vote']
    imdb = (soup('imdb_rating') or [False])[0]
    if imdb:
        imdb_rate, imdb_votes = imdb.text, imdb['num_vote']
    return (kp_rate, kp_votes,), (imdb_rate, imdb_votes,)
