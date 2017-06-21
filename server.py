import re
import kinopoisk as kp
from afisha_api import afisha
from datetime import datetime
from werkzeug.contrib.cache import SimpleCache
from flask import Flask, render_template, request, jsonify


CACHE_TIME = 12 * 60 * 60

app = Flask(__name__)
cache = SimpleCache()
api = afisha()

@app.route('/')
def show_films_schedule():
    films = cache.get('schedule')
    if films is None:
        films_info = api.schedule()
        films = [x for x in films_info['Items'] if x['PlaceCount'] > 29]
        cache.set('schedule', films, CACHE_TIME)
    return render_template('films.html', films=films, kind=('schedule', '',))


@app.route('/film/<int:film_id>')
def show_film_info(film_id):
    film = cache.get(film_id)
    if film is None:
        film = api.film_info(film_id).get('Data')
        if film is None:
            return render_template('films.html', kind=('404', film_id,))
        film['Tags'] = ', '.join(d['Name'] for d in film['Tags'])
        film['kp_id'] = kp.get_film_id(film['Name'][1:-1], int(film['Year']))
        film['kp'], film['imdb'] = kp.get_ratings(film['kp_id'])
        if film['imdb'] is not None:
            film['imdb'] = re.split(r'[:,(,)]', film['imdb'])[1:-1]
        release = film['ReleaseRusDate']
        if release is not None:
            film['Exit'] = datetime.strptime(release[:-6], "%Y-%m-%dT%H:%M:%S")
        cache.set(film_id, film, CACHE_TIME)
    return render_template('film.html', film=film)


@app.route('/search')
def show_found_films():
    query = request.args.get('query', '')
    films = api.search(query)['Items'] if query != '' else []
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
