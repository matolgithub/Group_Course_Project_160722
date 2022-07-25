import requests
import os
import json
from datetime import datetime
from datetime import date
import time

import db.send_data
import db.insert_data
import db.insert_photo
import db.delete_photo


class VKApiRequests:
    URL = 'https://api.vk.com/method/'

    def __init__(self, vk_user_id, vk_user_token):
        """Принимает id и токен пользователя, общающегося с ботом и либо собирает данные через API,
        либо подгружает и файла сохранённой сессии, при наличии
        """
        self.db_insert_photo_object = db.insert_photo.Photo('db_dating', 'user_dating')
        self.db_insert_data_object = db.insert_data.DataIn('Script_Insert_SQL_table_data.sql',
                                                           'db_dating', 'user_dating')
        self.db_send_data_object = db.send_data.Parcel('db_dating', 'user_dating')
        self.db_delete_photo_object = db.delete_photo.DelPhoto('db_dating', 'user_dating')
        self.user_token = vk_user_token
        self.user_id = vk_user_id
        self.requests_count = 0
        self.timestart = time.time()
        path_session = os.path.join("Integration", "Saved_sessions", f"Session_{self.user_id}.json")
        if os.path.exists(path_session):
            with open(path_session, 'r', encoding='utf-8') as f:
                self.user_info = json.load(f)
                self.first_name = self.user_info['first_name']
                self.second_name = self.user_info['second_name']
                self.age = self.user_info['age']
                self.sex = self.user_info['sex']
                self.partner_sex = self.user_info['partner_sex']
                self.city_name = self.user_info['city_name']
                self.city_id = self.user_info['city_id']
                self.groups = self.user_info['groups']
                self.interests = self.user_info['interests']
                self.music = self.user_info['music']
                self.books = self.user_info['books']
                self.offset = self.user_info['offset']
                self.match_users = self.user_info['match_users']
        else:
            self._get_init_user_info()

    def _get_init_user_info(self):
        """Внутренний метод получения данных пользователя, общающегося с ботом
        Берёт id пользователя и его токен из init класса и получается остальные атрибуты
        """
        method = 'users.get'
        params = {
            'user_ids': self.user_id,
            'fields': 'bdate, sex, city, music, interests, books',
            'access_token': self.user_token,
            'v': '5.131'
        }
        giui_user_info = requests.get(VKApiRequests.URL + method, params=params).json()
        check_errors(giui_user_info, self.user_id, '_get_init_user_info')
        self.match_users = {}
        self.first_name = giui_user_info['response'][0]['first_name']
        self.second_name = giui_user_info['response'][0]['last_name']
        self.sex = giui_user_info['response'][0]['sex']
        if len(giui_user_info['response'][0]['bdate'].split('.')) == 3:
            birth_year = giui_user_info['response'][0]['bdate'][-4:]
        else:
            birth_year = None
        if birth_year:
            self.age = int(date.today().strftime('%Y')) - int(birth_year)
        else:
            self.age = None
        if giui_user_info['response'][0]['city']['title'] == '' \
                or giui_user_info['response'][0]['city']['title'] is None:
            self.city_name = None
        else:
            self.city_name = giui_user_info['response'][0]['city']['title']
        if giui_user_info['response'][0]['city']['id'] == '' or giui_user_info['response'][0]['city']['id'] is None:
            city_id = None
        else:
            city_id = giui_user_info['response'][0]['city']['id']
        self.city_id = city_id
        if giui_user_info['response'][0]['interests'] is None or giui_user_info['response'][0]['interests'] == '':
            interests = None
        else:
            interests = giui_user_info['response'][0]['interests']
        self.interests = interests
        if giui_user_info['response'][0]['music'] is None or giui_user_info['response'][0]['music'] == '':
            music = None
        else:
            music = giui_user_info['response'][0]['music']
        self.music = music
        if giui_user_info['response'][0]['books'] is None or giui_user_info['response'][0]['books'] == '':
            books = None
        else:
            books = giui_user_info['response'][0]['books']
        self.books = books
        self.groups = self._get_user_groups(self.user_id)
        self.offset = 0
        if self.sex == 1:
            self.partner_sex = self.sex + 1
        elif self.sex == 2:
            self.partner_sex = self.sex - 1

    def is_city_age_exists(self):
        """Метод проверяет наличие данных о городе и возрасте.
        Выводит - int
        1 - Надо получить и возраст, и город
        2 - Надо получить только возраст
        3 - Надо получить только город
        0 - Всё есть, ничего не надо
        """
        if self.age is None and self.city_id is None:
            result = 1
        elif self.age is None and self.city_id:
            result = 2
        elif self.age and self.city_id is None:
            result = 3
        else:
            result = 0
        return result

    def give_me_city_age(self, city_name=None, age=None):
        """Метод, который принимает от пользователя название города для поиска кандидатов и(или) свой возраст
        и вносит в атрибуты.
        """
        if city_name:
            self.city_name = city_name
            self.city_id = self._get_city_id(city_name)
        if age:
            self.age = age

    def _get_city_id(self, name):
        """Внутренний метод получения id города по названию
        Принимает название города в формате str
        Выводит id в формате int
        """
        method = 'database.getCities'
        params = {
            'country_id': 1,
            'q': name,
            'count': 1,
            'access_token': self.user_token,
            'v': '5.131'
        }
        resp = requests.get(VKApiRequests.URL + method, params=params).json()
        check_errors(resp, self.user_id, '_get_city_id')
        result = resp['response']['items']['id']
        return result

    def _get_user_groups(self, id_):
        """Внутренний метод получения групп пользователя, общающегося с ботом
        Принимает id пользователя
        Выводит список id группу
        """
        method = 'groups.get'
        params = {
            'user_id': id_,
            'count': 1000,
            'access_token': self.user_token,
            'v': '5.131'
        }
        resp = requests.get(VKApiRequests.URL + method, params=params).json()
        check_result = check_errors(resp, self.user_id, '_get_user_groups')
        if check_result:
            result = None
        else:
            result = resp['response']['items']
        return result

    def give_me_candidates(self):
        """Метод запроса кандидатов.
        Отправляет данные пользователя в БД
        Выводит словарь в формате
            {
             user_id(int): {
                        'first_name': str,
                        'last_name': str,
                        'photo_links': [str,str,str...]
             }
        }
        """
        self.db_insert_data_object.get_data(self.user_id, f'https://vk.com/id{self.user_id}', self.age,
                                            self.first_name, self.second_name, self.sex, self.city_name,
                                            self.user_token, self.groups, self.interests, self.music, self.books)
        if self.match_users:
            return self.match_users
        else:
            self._get_candidates()
            return self.match_users

    def save_session(self, candidate_id):
        """Метод удаляет из списка кандидатов последнего просмотренного
        и сохраняет текущие данные пользователя и его списка кандидатов в файл сессии
        Принимает id кандидата
        Ничего не выводит
        """
        self.match_users.pop(candidate_id)
        dict_for_save = {
            'first_name': self.first_name,
            'second_name': self.second_name,
            'age': self.age,
            'sex': self.sex,
            'partner_sex': self.partner_sex,
            'city_name': self.city_name,
            'city_id': self.city_id,
            'groups': self.groups,
            'interests': self.interests,
            'music': self.music,
            'books': self.books,
            'offset': self.offset,
            'match_users': self.match_users,
        }
        path_sessions = os.path.join("Integration", "Saved_sessions")
        if os.path.exists(path_sessions) is False:
            os.mkdir(path_sessions)
        path_session = os.path.join(path_sessions, f"Session_{self.user_id}.json")
        with open(path_session, 'w', encoding='utf-8') as f:
            json.dump(dict_for_save, f)

    def _get_candidates(self):
        """Метод собирает перечень из 1000 пользователей из указанного города, сортирует их по совпдаению на
        возрастной диапазон, интересы, музыку, книги, группы, проверяет id кандидатов на предмет дубля выдачи
        и формирует итоговый перечень кандидатов
        Данные добавляются в атрибут класса match_users в формате:
        {
            user_id(int):{
                'first_name': str,
                'last_name': str,
                'photo_links': {
                    'photo_id(int)':{
                        'likes': int,
                        'photo_link': str
                    }
                }
            }
        }
        """
        method = 'users.search'
        params = {
            'offset': self.offset,
            'count': 50,
            'status': 6,
            'fields': 'bdate, music, interests, books',
            'city': self.city_id,
            'country': 1,
            'sex': self.partner_sex,
            'has_photo': 1,
            'access_token': self.user_token,
            'v': '5.131'
        }
        match_users_raw = requests.get(VKApiRequests.URL + method, params=params).json()
        check_errors(match_users_raw, self.user_id, '_get_candidates')
        if not match_users_raw['response']['items']:
            self.match_users = None
            return
        for users in match_users_raw['response']['items']:
            m_user_id = users['id']
            blacklist = self.db_send_data_object.black_list_output(self.user_id)
            if m_user_id in blacklist:
                continue
            m_first_name = users['first_name']
            m_last_name = users['last_name']
            m_age = 0
            try:
                if len(users['bdate'].split('.')) == 3:
                    m_birth_year = users['bdate'][-4:]
                    m_age = int(date.today().strftime('%Y')) - int(m_birth_year)
            except KeyError:
                continue
            try:
                m_interests = users['interests']
            except KeyError:
                m_interests = None
            try:
                m_books = users['books']
            except KeyError:
                m_books = None
            try:
                m_music = users['music']
            except KeyError:
                m_music = None
            m_groups = self._get_user_groups(m_user_id)
            self.requests_limit_control()
            photo_inf = self._get_photo_links(users['id'])
            self.requests_limit_control()
            if photo_inf is None:
                continue
            m_photo_links = {}
            for item, value in photo_inf.items():
                m_photo_links[item] = value['photo_link']
            match_users_dict = {
                'first_name': m_first_name,
                'last_name': m_last_name,
                'photo_links': m_photo_links
            }
            if m_age == self.age:
                self.match_users[m_user_id] = match_users_dict
                continue
            elif (self.age - 10 <= m_age <= self.age - 1 or self.age + 1 <= m_age <= self.age + 10) and m_age > 18:
                if m_interests:
                    try:
                        for inter in m_interests.split(','):
                            if inter in self.interests.split(','):
                                self.match_users[m_user_id] = match_users_dict
                    except Exception:
                        continue
                elif m_books:
                    try:
                        for book in m_books.split(','):
                            if book in self.books.split(','):
                                self.match_users[m_user_id] = match_users_dict
                    except Exception:
                        continue
                elif m_music:
                    try:
                        for music in m_music.split(','):
                            if music in self.music.split(','):
                                self.match_users[m_user_id] = match_users_dict
                    except Exception:
                        continue
                elif m_groups:
                    try:
                        for group in m_groups:
                            if group in self.groups:
                                self.match_users[m_user_id] = match_users_dict
                    except Exception:
                        continue
        self.offset += 50

    def _get_photo_links(self, owner_id):
        """Внутренний метод получения ссылок на фотографии с самым большим кол-вом лайков
        Принимает id кандидата
        Выводит ссыкли на фото в формате:
        {
        photo_id(int): {
                        'likes': int,
                        'photo_link': str
                        }
        }
        """
        method = 'photos.get'
        params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'extended': 1,
            'access_token': self.user_token,
            'v': '5.131'
        }
        photo_info = requests.get(VKApiRequests.URL + method, params=params).json()
        check_result = check_errors(photo_info, self.user_id, '_get_photo_links')
        if check_result:
            return None
        else:
            photo_dict = self._raw_photo_dict(photo_info)
            return photo_dict

    def _raw_photo_dict(self, api_response):
        """Внутренняя функция сортировки изображений по кол-ву лайков и получение 3 топовых"""
        result_dict = {}
        unsort_dict = {}
        for photo in api_response['response']['items']:
            likes = photo['likes']['count']
            photo_id = photo['id']
            photo_link = photo['sizes'][-1]['url']
            result_dict[photo_id] = {
                'likes': likes,
                'photo_link': photo_link
            }
            unsort_dict[photo_id] = likes
        if len(unsort_dict.items()) > 3:
            sort_dict = sorted(unsort_dict.items(), key=lambda x: x[1])
            for item in [id_ for id_ in dict(sort_dict)][:-3]:
                result_dict.pop(item)

        return result_dict

    def smash_like(self, candidate_id, photo_id, photo_link):
        """Получает id кандидата и id фото на которую ставить лайк.
        Ставит лайк, отправляет данные в БД словарём в формате:
            {
             user_id(int): {
                        'candidate_id': int,
                        'photo_id': int
             }
         }
        """
        self.db_insert_photo_object.in_likeslist_table(self.user_id, candidate_id, photo_link, photo_id)
        method = 'likes.add'
        params = {
            'type': 'photo',
            'owner_id': candidate_id,
            'item_id': photo_id,
            'access_token': self.user_token,
            'v': '5.131'
        }
        resp = requests.post(VKApiRequests.URL + method, params=params).json()
        check_errors(resp, self.user_id, 'smash_like')
        result = 'Поставили лайк'
        return result

    def delete_like(self, candidate_id, photo_id):
        """Получает id кандидата и id фото на которую удалить лайк.
        Удаляет лайк, отправляет данные в БД словарём в формате:
        {user_id: photo_id}
        """
        self.db_delete_photo_object.del_id_photolist(self.user_id, candidate_id, photo_id)
        method = 'likes.delete'
        params = {
            'type': 'photo',
            'owner_id': candidate_id,
            'item_id': photo_id,
            'access_token': self.user_token,
            'v': '5.131'
        }
        resp = requests.post(VKApiRequests.URL + method, params=params).json()
        check_errors(resp, self.user_id, 'delete_like')
        result = 'Удалили лайк'
        return result

    def requests_limit_control(self):
        """Метод контролирует лимит запросов к VK API в секунду"""
        self.requests_count += 1
        if self.requests_count > 4 and time.time() - self.timestart < 1:
            time.sleep(0.7)
            self.timestart = time.time()
        elif self.requests_count > 4 and time.time() - self.timestart > 1:
            self.timestart = time.time()


def check_errors(response, user_id, func_name):
    """Функция проверяет наличие ошибки в ответе на АПИ запрос, заносит ошибку в лог и выводит строку об ошибке
    Ответ от API находится в response.json()
    """
    try:
        resp_error = str(response['error']['error_code'])
    except Exception:
        result = None
        return result
    path_errors = os.path.join("Integration", "Errors", "vk_errors.json")
    with open(path_errors, 'r', encoding='utf-8') as f:
        errors = json.load(f)
        if resp_error in errors.keys():
            if os.path.exists("Logs") is False:
                os.mkdir("Logs")
            path_logs = os.path.join("Logs", f"log_{user_id}.txt")
            with open(path_logs, 'a', encoding='utf-8') as file:
                file.write(f'{datetime.now().strftime("%d.%m.%Y - %H:%M")}\nИмя функции/метода: {func_name}\n'
                           f'Ошибка: {resp_error}\n{errors[resp_error]}\n-------\n')
            result = 'Произошла непредвиденная ошибка! Пожалуйста, обратитесь к администратору или попробуйте позже.'
            return result
