import requests
import random
import string
import pyDes as coding


class afisha:
    def schedule_cinema(self, film_start=0):
        self.action = 'theme_schedule'
        query = {'action': self.action, 'cityId': self.city_id, 'themeid': 2,
                 'start': film_start, 'count': self.count,
                 'sortOrder': self.sort}
        return self.request(query)


    def film_review(self, film_id):
        self.action = 'review_list'
        query = {'action': self.action, 'clsId': self.cls_id, 'id': film_id,
                 'count': self.count, 'start': self.start}
        return self.request(query)


    def film_photos(self, film_id):
        self.action = 'image_list'
        query = {'action': self.action, 'clsId': self.cls_id,
                 'count': self.count, 'start': self.start,
                 'iscrop': 0, 'id': film_id}
        return self.request(query)


    def film_info(self, film_id):
        self.action = 'product'
        query = {'action': self.action, 'clsId': self.cls_id,
                 'cityId': self.city_id, 'id': film_id}
        return self.request(query)[0]


    def film_schedule(self, film_id):
        self.action = 'schedule'
        query = {'action': self.action, 'clsId': self.cls_id, 'id': film_id,
                 'cityId': self.city_id, 'scheduleFormat': 1,
                 'sortOrder': self.sort}
        return self.request(query)


    def request(self, query):
        return requests.post(self.api_url, params=self.session_payload,
                             data=query).json()


    def __init__(self):
        SECRET = bytes([45, 56, 38, 71, 42, 105, 50, 77])
        INT_2_POW_64 = 18446744073709551616
        self.api_url = 'http://api.afisha.ru/mobile/Service.aspx'
        self.city_id = 2
        self.cls_id = 16
        self.sort = 5
        self.start = 0
        self.count = 9
        self.phone_id = ''.join(random.sample(string.ascii_lowercase, 12))
        self.phone_name = random.choice(('JiaYu', 'Acer', 'Samsung', 'Fly',))
        self.phone_resolution = random.choice(('480x800', '720x1280',))
        self.platform_ver = random.choice(('4.2.2', '4.4', '5.0', '5.1',))
        self.session = '-1'
        self.user_info = {'X-Afisha-Phone-Platform': 'Android',
                          'X-Afisha-Session-Id': self.session,
                          'X-Afisha-App-Name': 'Android-Afisha',
                          'X-Afisha-App-Ver': '2.3.13',
                          'X-Afisha-Protocol-Ver': '1.3',
                          'X-Afisha-Phone-Id': self.phone_id,
                          'X-Afisha-Phone-Name': self.phone_name,
                          'X-Afisha-Phone-Resolution': self.phone_resolution,
                          'X-Afisha-Phone-Platform-Version': self.platform_ver}
        responce = requests.post(self.api_url, headers=self.user_info)
        session_request = responce.headers['X-Afisha-Session-Request']
        req_bytes = int(session_request).to_bytes(8, byteorder='little')
        cipher = coding.des(SECRET, coding.ECB, pad=None,
                            padmode=coding.PAD_NORMAL)
        byte_array = cipher.encrypt(req_bytes)
        session = int.from_bytes(byte_array, byteorder='little', signed=True)
        if session < 0:
            session += INT_2_POW_64
        self.session_payload = {'X-Afisha-Phone-Id': self.phone_id,
                                'X-Afisha-Session-Id': session}
