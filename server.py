import re
import kinopoisk as kp
from afisha_api import afisha_films
from datetime import datetime
from werkzeug.contrib.cache import SimpleCache
from flask import Flask, render_template, request, jsonify, abort


CACHE_TIME = 12 * 60 * 60
TITLE = {'schedule': 'Сеансы в кинотеатрах Москвы',
         'search': 'Список фильмов по запросу "{}"',
         'api': 'Информация о работе с API',
         '404': 'Ошибка 404'}


def get_films_schedule():
    cinema_count = 29
    schedule = afisha.get_schedule()
    films = [x for x in schedule['Items'] if x['PlaceCount'] > cinema_count]
    cache.set('schedule', films, CACHE_TIME)
    return films


def get_film_info(film_id):
    film = afisha.get_film_info(film_id).get('Data') or abort(404)
    film['Tags'] = ', '.join(d['Name'] for d in film['Tags'])
    film['kp_id'] = kp.get_film_id(film['Name'][1:-1], int(film['Year']))
    film['kp'], film['imdb'] = kp.get_ratings(film['kp_id'])
    if film['imdb'] is not None:
        film['imdb'] = re.split(r'[:,(,)]', film['imdb'])[1:-1]
    release = film['ReleaseRusDate']
    if release is not None:
        film['Exit'] = datetime.strptime(release[:-6], "%Y-%m-%dT%H:%M:%S")
    cache.set(film_id, film, CACHE_TIME)
    return film


app = Flask(__name__)
cache = SimpleCache()
afisha = afisha_films()


@app.route('/')
def show_films_schedule():
    films = cache.get('schedule') or get_films_schedule()
    return render_template('films.html', films=films, title=TITLE['schedule'])


@app.route('/film/<int:film_id>')
def show_film_info(film_id):
    film = cache.get(film_id) or get_film_info(film_id)
    return render_template('film.html', film=film, title=film['Name'])


@app.route('/search')
def show_found_films():
    query = request.args.get('query', '')
    films = afisha.search_film(query).get('Items', [])
    return render_template('films.html', title=TITLE['search'].format(query),
                           films=films)


@app.route('/api/<kind>')
def get_api(kind):
    if kind == 'info':
        return render_template('api.html', title=TITLE['api'])
    api_dict = {'schedule': (afisha.get_schedule, request.args.get('date', 1)),
                'search': (afisha.search_film, request.args.get('name', '')),
                'film': (afisha.get_film_info, request.args.get('id', 0))}
    api_func, func_arg = api_dict[kind]
    return jsonify(api_func(func_arg))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('not_found.html', title=TITLE['404']), 404


if __name__ == '__main__':
    app.run()
