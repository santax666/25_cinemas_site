import requests


class afisha_films:
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

    def get_schedule(self, date=1, offset=0, limit=1000):
        params = {'themeID': 2, 'sortOrder': 0, 'dateRangeID': date,
                  'range.Limit': limit, 'range.Offset': offset}
        films_url = '{}/themeevents'.format(self.url)
        return self.session.get(films_url, params=params).json()

    def get_film_info(self, film_id=0):
        film_url = '{0}/creations/16-{1}'.format(self.url, film_id)
        return self.session.get(film_url).json()

    def search_film(self, name, offset=0, limit=1000):
        arg = {'searchString': name, 'searchThemeID': 2,
               'range.Offset': offset, 'range.Limit': limit}
        search_url = '{}/searchitems'.format(self.url)
        return self.session.get(search_url, params=arg).json()
