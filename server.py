from afisha_api import afisha
from flask import Flask, render_template
from werkzeug.contrib.cache import SimpleCache


app = Flask(__name__)
cache = SimpleCache()
api = afisha()


@app.route('/')
@app.route('/page/<int:page_id>')
def show_films(page_id=1):
    films_dict = {}
    films = api.schedule_cinema((page_id-1)*9)
    films_pages = (films['maxCount']-1) // 9 + 1
    for film in films['list']:
        film.update(api.film_info(film['id']))
        film['rate_int'] = int(film['rate'])
        cache.set(film['id'], film, 12*60*60)
    return render_template('films.html', films=enumerate(films),
                           pages=(films_pages, page_id,))


@app.route('/film/<int:film_id>')
def show_film_info(film_id):
    film_info = cache.get(film_id)
    return render_template('film.html', film=film_info)


if __name__ == '__main__':
    app.run(debug=True)
