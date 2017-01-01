from afisha_api import afisha
from flask import Flask, render_template
from werkzeug.contrib.cache import SimpleCache


app = Flask(__name__)
cache = SimpleCache()
api = afisha()


@app.route('/')
def show_films():
    films_dict = cache.get('films')
    if films_dict is None:
        films_dict = {}
        films_list = api.schedule_cinema()
        for film in films_list:
            id = film.get('id')
            films_dict[id] = api.film_info(id)
            films_dict[id]['rate_int'] = int(films_dict[id]['rate'])
            schedule = api.film_schedule(id)
            films_dict[id]['cinema_count'] = schedule['maxCount']
            films_dict[id]['schedule'] = schedule['list']
            review = api.film_review(id)
            films_dict[id]['review_count'] = review['maxCount']
            films_dict[id]['review'] = review['list']
            photos = api.film_photos(id)
            films_dict[id]['photos_count'] = photos['maxCount']
            films_dict[id]['photos'] = photos['list']
            films_dict[id]['id'] = id
        cache.set('films', films_dict, 12*60*60)
    sorted_films = sorted(films_dict.items(), reverse=True,
                              key=lambda x: x[1]['cinema_count'])
    return render_template('films_list.html', films=enumerate(sorted_films))


@app.route('/film/<int:film_id>')
def show_film_info(film_id):
    films = cache.get('films')
    film_info = films.get(film_id)
    return render_template('film_info.html', film=film_info)


@app.route('/film/content/<int:film_id>')
def show_film_content(film_id):
    films = cache.get('films')
    film_info = films.get(film_id)
    return render_template('film_content.html',
                           content=(enumerate(film_info['trailers']),
                                    enumerate(film_info['photos'])))


if __name__ == '__main__':
    app.run()
