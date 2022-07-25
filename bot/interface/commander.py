import os
import re
import json

from interface import commander_config
from Integration.api_vk import VKApiRequests
from db.insert_data import DataIn
from db.send_data import Parcel
from db.delete_data import Disposal


class Commander:
    """
    Обеспечивает логику общения с пользователем
    """

    def __init__(self, vk_id: int, user_name: str):
        """
        Инициализация класса "Commander"

        Если существует файл с параметрами для данного пользователя ВК, то self-переменные загружаются из него.
        Если файл отсутствует, то self-переменные принимают значения по умолчанию

        :param vk_id: id пользователя ВК
        :param user_name: Имя пользователя ВК
        """

        self.id = vk_id
        self.user_name = user_name
        path_file = os.path.join("interface", "options", f"options_{self.id}.txt")
        if os.path.exists(path_file):
            self.reading_parameters()
            if self.token is not None:
                self.obj_vk_api_requests = VKApiRequests(self.id, self.token)
        else:
            self.token = None
            self.obj_vk_api_requests = None
            self.mode = "default"
            self.path = os.path.join("interface", "keyboards", "default.json")
            self.candidate = {}
            self.list_elected = []
            self.elected_id = None
            self.list_blacklist = []
            self.blacklist_id = None
            self.counter = 0

    def input(self, msg: str) -> dict:
        """
        Метод принимающий сообщения/команды и отвечающий за логику ответов

        :param msg: Входящее сообщение
        :return: Ответ в виде словаря, сформированный методом
        """

        if self.mode == "default":
            return self.processing_mode_default(msg)

        if self.mode == "token":
            return self.processing_mode_token(msg)

        if self.mode == "favorites":
            return self.processing_mode_favorites(msg)

        if self.mode == "blacklist":
            return self.processing_mode_blacklist(msg)

        if self.mode == "search":
            return self.processing_mode_search(msg)

        if self.mode == "photo_1" or self.mode == "photo_2" or self.mode == "photo_3":
            return self.processing_mode_photo(msg)

        if self.mode == "age":
            return self.processing_mode_age(msg)

        if self.mode == "city":
            return self.processing_mode_city(msg)

    def processing_mode_token(self, msg: str) -> dict:
        """
        Получение токена от пользователя

        Если во входящем сообщении обнаружен токен, то он сохраняется и проводится проверка
        есть ли в ВК данные о возрасте и городе проживания пользователя.
        Если токен не обнаружен, предлагается попробовать указать его заново.

        :param msg: Входящее сообщение
        """

        request_token = commander_config.request_token
        pattern = "access_token=([^&]*)"
        if re.search(pattern, msg):
            self.token = re.search(pattern, msg).group(1)
            self.obj_vk_api_requests = VKApiRequests(self.id, self.token)
            return self.age_city_check()
        else:
            answer = f"Ошибка! Попробуйте еще раз!\n\n" + request_token
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

    def processing_mode_default(self, msg: str) -> dict:
        """
        Первоначальный контакт с пользователем

        Если приходит команда start = "Начать поиск", режим меняется на "token",
        в ответ возвращается инструкция по получению токена от пользователя.
        Если приходит что-то иное - инструкция, как начать поиск.

        :param msg: Входящее сообщение
        """
        start = commander_config.start
        request_token = commander_config.request_token
        if start in msg:
            self.mode = "token"
            answer = request_token
            self.path = os.path.join("interface", "keyboards", "none.json")
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result
        else:
            answer = f"Привет, {self.user_name}!\n" \
                     f"Для того чтобы начать поиск партнера нажмите 'Начать поиск'. Удачи, {self.user_name}!"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

    def processing_mode_favorites(self, msg: str) -> dict:
        """
        Логика работы бота в подменю "Список избранных"

        Если приходит команда next_contender = "Следующий/ая" - выводится ссылка на следующего
        кандидата из списка избранных. Если список избранных пуст или дошли до конца списка -
        выводится соответствующее сообщение.
        Если приходит команда remove = "Удалить из избранного" - текущий кандидат из избранного удаляется.
        Если приходит команда continue_searching = "Продолжить поиск" - происходит возврат к меню
        поиска кандидатов и выводится тот кандидат, на котором перешли в другое меню.

        :param msg: Входящее сообщение
        """

        next_contender = commander_config.next_contender
        remove = commander_config.remove
        continue_searching = commander_config.continue_searching

        if next_contender in msg:
            if self.list_elected == []:
                answer = f"{self.user_name}, это невозможно! Ваш список избранных кандидатов пуст!"
                self.elected_id = None
            else:
                if self.counter == (len(self.list_elected) - 1):
                    answer = f"{self.user_name}, Вы дошли до конца списка избранных кандидатов!"
                else:
                    self.counter += 1
                    self.elected_id = self.list_elected[self.counter]
                    answer = f"https://vk.com/id{self.elected_id}"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

        if remove in msg:
            db = Disposal('db_dating', 'user_dating')
            db.del_id_electlist(user_id=self.id, del_user_id=self.elected_id)
            answer = f"Пользователь https://vk.com/id{self.elected_id} удален из списка избранных кандидатов!"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

        if continue_searching in msg:
            self.mode = "search"
            self.path = os.path.join("interface", "keyboards", "search.json")
            answer = self.candidate_data_output()
            result = {"message": answer["message"], "path": self.path, "attachment": answer["attachment"]}
            self.counter = 0
            self.saving_parameters()
            return result

        else:
            answer = "Команда не распознана!"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

    def processing_mode_blacklist(self, msg: str) -> dict:
        """
        Логика работы бота в подменю "Черный список"

        Если приходит команда next_contender = "Следующий/ая" - выводится ссылка на следующего
        кандидата из черного списка. Если черный список пуст или дошли до конца списка -
        выводится соответствующее сообщение.
        Если приходит команда remove_blacklist = "Удалить из ЧС" - текущий кандидат из избранного удаляется.
        Если приходит команда continue_searching = "Продолжить поиск" - происходит возврат к меню
        поиска кандидатов и выводится тот кандидат, на котором перешли в другое меню.

        :param msg: Входящее сообщение
        """

        next_contender = commander_config.next_contender
        remove_blacklist = commander_config.remove_blacklist
        continue_searching = commander_config.continue_searching

        if next_contender in msg:
            if self.list_blacklist == []:
                answer = f"{self.user_name}, это невозможно! Ваш черный список пуст!"
                self.blacklist_id = None
            else:
                if self.counter == (len(self.list_blacklist) - 1):
                    answer = f"{self.user_name}, Вы дошли до конца черного списка!"
                else:
                    self.counter += 1
                    self.blacklist_id = self.list_blacklist[self.counter]
                    answer = f"https://vk.com/id{self.blacklist_id}"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

        if remove_blacklist in msg:
            db = Disposal('db_dating', 'user_dating')
            db.del_id_blacklist(user_id=self.id, del_user_id=self.blacklist_id)
            answer = f"Пользователь https://vk.com/id{self.blacklist_id} удален из черного списка!"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

        if continue_searching in msg:
            self.mode = "search"
            self.path = os.path.join("interface", "keyboards", "search.json")
            answer = self.candidate_data_output()
            result = {"message": answer["message"], "path": self.path, "attachment": answer["attachment"]}
            self.counter = 0
            self.saving_parameters()
            return result

        else:
            answer = "Команда не распознана!"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

    def processing_mode_search(self, msg: str) -> dict:
        """
        Логика работы бота в меню поиска кандидатов

        Если приходит команда next_contender = "Следующий/ая" - выводится следующий кандидат в формате:
        Имя Фамилия
        ссылка на профиль
        три(доступное количество) фотографии в виде attachment(https://dev.vk.com/method/messages.send).
        Если поиск завершен - выводится предупреждение о начале поиска заново.
        Если приходит команда favorites = "В избранное" - текущий кандидат добавляется в список избранных.
        Если приходит команда add_blacklist = "В черный список" - текущий кандидат добавляется в ЧС.
        Если приходит команда favorites_list = "Список избранных" - происходит переход в подменю "Список избранных"
        и выводится первый кандидат из этого списка. Если список избранных пуст - выводится соответствующее сообщение.
        Если приходит команда blacklist = "Черный список" - происходит переход в подменю "Черный список"
        и выводится первый кандидат из этого списка. Если ЧС пуст - выводится соответствующее сообщение.
        Если приходит команда photo_1, photo_2, photo_3 = "Фото 1", "Фото 2", "Фото 3" - происходит проверка:
         есть ли у кандидата такое фото, и если есть происходит переход в подменю "Фото"

        :param msg: Входящее сообщение
        """

        next_contender = commander_config.next_contender
        favorites = commander_config.favorites
        add_blacklist = commander_config.add_blacklist
        favorites_list = commander_config.favorites_list
        blacklist = commander_config.blacklist
        photo_1 = commander_config.photo_1
        photo_2 = commander_config.photo_2
        photo_3 = commander_config.photo_3

        if next_contender in msg:
            result = self.obtaining_candidate()
            return result

        if favorites in msg:
            db = DataIn("Script_Insert_SQL_table_data.sql", 'db_dating', 'user_dating')
            db.in_elected_table(user_bot=self.id, elected_user=self.candidate["id"])
            answer = f"{self.candidate['first_name']} {self.candidate['last_name']} внесен/а в список избранного"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

        if add_blacklist in msg:
            db = DataIn("Script_Insert_SQL_table_data.sql", 'db_dating', 'user_dating')
            db.in_blacklist_table(user_bot=self.id, blacklist_user=self.candidate["id"])
            answer = f"{self.candidate['first_name']} {self.candidate['last_name']} внесен/а в чёрный список " \
                     f"и больше не будет отображаться при поиске кандидатов!"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

        if favorites_list in msg:
            db = Parcel('db_dating', 'user_dating')
            self.list_elected = db.elected_list_output(user_id=self.id)
            if self.list_elected == []:
                answer = f"{self.user_name}, Ваш список избранных кандидатов пуст!"
                self.elected_id = None
            else:
                self.counter = 0
                self.elected_id = self.list_elected[self.counter]
                answer = f"{self.user_name}, Ваш список избранных кандидатов:\n" \
                         f"https://vk.com/id{self.elected_id}"
                self.path = os.path.join("interface", "keyboards", "favorites.json")
                self.mode = "favorites"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

        if blacklist in msg:
            db = Parcel('db_dating', 'user_dating')
            self.list_blacklist = db.black_list_output(user_id=self.id)
            if self.list_blacklist == []:
                answer = f"{self.user_name}, Ваш черный список пуст!"
                self.blacklist_id = None
            else:
                self.counter = 0
                self.blacklist_id = self.list_blacklist[self.counter]
                answer = f"{self.user_name}, Ваш черный список:\n" \
                         f"https://vk.com/id{self.blacklist_id}"
                self.path = os.path.join("interface", "keyboards", "blacklist.json")
                self.mode = "blacklist"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

        if photo_1 in msg:
            result = self.choose_photo(photo="photo_1")
            return result

        if photo_2 in msg:
            result = self.choose_photo(photo="photo_2")
            return result

        if photo_3 in msg:
            result = self.choose_photo(photo="photo_3")
            return result

        else:
            answer = "Команда не распознана!"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

    def processing_mode_photo(self, msg: str) -> dict:
        """
        Логика работы бота в подменю "Фото"

        Если приходит команда like = "Поставить лайк" - исходя из режима, ставит лайк на выбранное фото.
        Если приходит команда revoke_like = "Убрать лайк" - исходя из режима, убирает лайк с выбранного фото.
        Если приходит команда continue_searching = "Продолжить поиск" - происходит возврат к меню
        поиска кандидатов и выводится тот кандидат, на котором перешли в другое меню.

        :param msg: Входящее сообщение
        """

        like = commander_config.like
        revoke_like = commander_config.revoke_like
        continue_searching = commander_config.continue_searching

        if like in msg:
            photo_id = None
            photo_link = None
            if self.mode == "photo_1":
                photo_id = self.candidate['photo_1']['id_photo']
                photo_link = self.candidate['photo_1']['link_photo']
            elif self.mode == "photo_2":
                photo_id = self.candidate['photo_2']['id_photo']
                photo_link = self.candidate['photo_2']['link_photo']
            elif self.mode == "photo_3":
                photo_id = self.candidate['photo_3']['id_photo']
                photo_link = self.candidate['photo_3']['link_photo']
            if photo_id:
                answer = self.obj_vk_api_requests.smash_like(candidate_id=self.candidate['id'],
                                                             photo_id=photo_id, photo_link=photo_link)
            else:
                answer = "Неизвестная ошибка: режим photo, команда: Поставить лайк"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

        if revoke_like in msg:
            photo_id = None
            if self.mode == "photo_1":
                photo_id = self.candidate['photo_1']['id_photo']
            elif self.mode == "photo_2":
                photo_id = self.candidate['photo_2']['id_photo']
            elif self.mode == "photo_3":
                photo_id = self.candidate['photo_3']['id_photo']
            if photo_id:
                answer = self.obj_vk_api_requests.delete_like(candidate_id=self.candidate['id'], photo_id=photo_id)
            else:
                answer = "Неизвестная ошибка: режим photo, команда: Убрать лайк"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

        if continue_searching in msg:
            self.mode = "search"
            self.path = os.path.join("interface", "keyboards", "search.json")
            answer = self.candidate_data_output()
            result = {"message": answer["message"], "path": self.path, "attachment": answer["attachment"]}
            self.saving_parameters()
            return result

        else:
            answer = "Команда не распознана!"
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

    def age_city_check(self) -> dict:
        """
        Метод проверки наличия данных в ВК о возрасте и городе проживания пользователя.

        Если все данные есть, то переходим к поиску кандидатов.
        Если не хватает возраста, то переходим к режиму и методу ввода возраста пользователем.
        Если не хватает данных о городе проживания, то переходим к режиму и методу ввода города пользователем.
        """

        if self.obj_vk_api_requests.is_city_age_exists() == 0:
            self.mode = "search"
            self.path = os.path.join("interface", "keyboards", "search.json")
            result = self.obtaining_candidate()
            return result
        if self.obj_vk_api_requests.is_city_age_exists() == 1 or self.obj_vk_api_requests.is_city_age_exists() == 2:
            self.mode = "age"
            self.path = os.path.join("interface", "keyboards", "none.json")
            answer = f"{self.user_name}, пришлите Ваш возраст, в виде числа, в ответном сообщении."
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result
        elif self.obj_vk_api_requests.is_city_age_exists() == 3:
            self.mode = "city"
            self.path = os.path.join("interface", "keyboards", "none.json")
            answer = f"{self.user_name}, укажите название города, в котором Вы проживаете, в ответном сообщении."
            result = {"message": answer, "path": self.path, "attachment": None}
            self.saving_parameters()
            return result

    def processing_mode_age(self, msg: str) -> dict:
        """
        Сохраняет данные о возрасте, полученные в сообщении.

        Если в сообщении найдено число от 0 до 150, то оно сохраняется как возраст пользователя.
        Затем, в любом случае производит повторную проверку на наличие данных о возрасте
        и городе проживания пользователя.

        :param msg: Входящее сообщение
        """

        pattern_age = "[1-9][0-9]{0,2}"
        if re.search(pattern_age, msg):
            age = re.search(pattern_age, msg).group(0)
            if 0 < int(age) < 150:
                self.obj_vk_api_requests.give_me_city_age(age=age)
        return self.age_city_check()

    def processing_mode_city(self, msg: str) -> dict:
        """
        Сохраняет данные о городе, полученные в сообщении.

        Если в сообщении найдено название города, то оно сохраняется.
        Затем, в любом случае производит повторную проверку на наличие данных о возрасте
        и городе проживания пользователя.

        :param msg: Входящее сообщение
        """

        pattern_city = "[А-Я][а-я]+-*[А-Я]*[а-я]*[0-9]*"
        if re.search(pattern_city, msg):
            city = re.search(pattern_city, msg).group(0)
            self.obj_vk_api_requests.give_me_city_age(city_name=city)
        return self.age_city_check()

    def saving_parameters(self):
        """
        Сохраняет self-параметры в виде словаря в файл "options_{id пользователя},
        находящийся в директории: interface -> options.

        Если каталога "options" не существует, то создает его.
        """

        path_options = os.path.join("interface", "options")
        if os.path.exists(path_options) is False:
            os.mkdir(path_options)
        path_file = os.path.join(path_options, f"options_{self.id}.txt")
        dict_options = {
            "self.token": self.token,
            "self.mode": self.mode,
            "self.path": self.path,
            "self.candidate": self.candidate,
            "self.list_elected": self.list_elected,
            "self.elected_id": self.elected_id,
            "self.counter": self.counter,
            "self.list_blacklist": self.list_blacklist,
            "self.blacklist_id": self.blacklist_id
        }
        with open(path_file, 'w', encoding='utf-8') as file:
            json.dump(dict_options, file)

    def reading_parameters(self):
        """
        Считывает self-параметры в виде словаря из файла "options_{id пользователя},
        находящегося в директории: interface -> options.
        """

        path_file = os.path.join("interface", "options", f"options_{self.id}.txt")
        with open(path_file, 'r', encoding='utf-8') as file:
            dict_options = json.load(file)
            self.token = dict_options["self.token"]
            self.mode = dict_options["self.mode"]
            self.path = dict_options["self.path"]
            self.candidate = dict_options["self.candidate"]
            self.list_elected = dict_options["self.list_elected"]
            self.elected_id = dict_options["self.elected_id"]
            self.counter = dict_options["self.counter"]
            self.list_blacklist = dict_options["self.list_blacklist"]
            self.blacklist_id = dict_options["self.blacklist_id"]

    def obtaining_candidate(self) -> dict:
        """
        Вызывает метод класса VKApiRequests, осуществляющий выдачу кандидатов в пару к пользователю и
        возвращает одного из кандидатов в формате:
        Имя Фамилия
        ссылка на профиль
        три(доступное количество) фотографии в виде attachment(https://dev.vk.com/method/messages.send)

        Обеспечивает, чтобы словарь с кандидатами не был пустым.
        Если метод obj_vk_api_requests.give_me_candidates() класса VKApiRequests возвращает None, то начинает поиск
        заново, предупредив об этом пользователя.
        """

        dict_candidates = self.obj_vk_api_requests.give_me_candidates()
        while dict_candidates == {}:
            dict_candidates = self.obj_vk_api_requests.give_me_candidates()
        if dict_candidates is None:
            answer = f"{self.user_name}, Вы просмотрели всех подходящих Вам кандидатов! " \
                     f"Нажмите 'Следующий/ая', чтобы начать поиск заново!"
            self.obj_vk_api_requests.offset = 0
            result = {"message": answer, "path": self.path, "attachment": None}
        else:
            dict_photo = dict_candidates[list(dict_candidates.keys())[0]]["photo_links"]
            dict_candidate = {
                "id": list(dict_candidates.keys())[0],
                "first_name": dict_candidates[list(dict_candidates.keys())[0]]["first_name"],
                "last_name": dict_candidates[list(dict_candidates.keys())[0]]["last_name"],
                "link_to_profile": f"https://vk.com/id{list(dict_candidates.keys())[0]}"
            }
            for count, photo_key in enumerate(dict_photo):
                dict_candidate[f"photo_{count + 1}"] = {
                    "id_photo": photo_key,
                    "link_photo": dict_photo[photo_key]
                }
            self.candidate = dict_candidate
            self.obj_vk_api_requests.save_session(self.candidate["id"])
            answer = self.candidate_data_output()
            result = {"message": answer["message"], "path": self.path, "attachment": answer["attachment"]}
        self.saving_parameters()
        return result

    def candidate_data_output(self) -> dict:
        """
        Проводит проверку на количество фотографий у кандидата и
        осуществляет преобразование данных о кандидате к формату:
        Имя Фамилия
        ссылка на профиль
        три(доступное количество) фотографии в виде attachment(https://dev.vk.com/method/messages.send)
        """

        message = f"{self.candidate['first_name']} {self.candidate['last_name']}\n{self.candidate['link_to_profile']}"
        owner_id = self.candidate['id']
        if self.candidate.get("photo_3"):
            photo_id_1 = self.candidate['photo_1']['id_photo']
            photo_id_2 = self.candidate['photo_2']['id_photo']
            photo_id_3 = self.candidate['photo_3']['id_photo']
            attachment = f"photo{owner_id}_{photo_id_1},photo{owner_id}_{photo_id_2},photo{owner_id}_{photo_id_3}"
            return {"message": message, "attachment": attachment}
        elif self.candidate.get("photo_2"):
            photo_id_1 = self.candidate['photo_1']['id_photo']
            photo_id_2 = self.candidate['photo_2']['id_photo']
            attachment = f"photo{owner_id}_{photo_id_1},photo{owner_id}_{photo_id_2}"
            message += "\nЕсть только две фотографии:"
            return {"message": message, "attachment": attachment}
        elif self.candidate.get("photo_1"):
            photo_id_1 = self.candidate['photo_1']['id_photo']
            attachment = f"photo{owner_id}_{photo_id_1}"
            message += "\nЕсть только одна фотография:"
            return {"message": message, "attachment": attachment}
        else:
            message += "\nФотографий нет!"
            return {"message": message, "attachment": None}

    def choose_photo(self, photo: str) -> dict:
        """
        Определяет с какой фотографией предстоит работать (№ 1, № 2 или № 3) и
        проверяет наличие данной фотографии у кандидата.

        :param photo: Определяет с какой фотографией предстоит работать "photo_1", "photo_2" или "photo_3"
        """
        if self.candidate.get(photo):
            self.mode = photo
            answer = "Выбранная фотография:\n"
            photo_id = self.candidate[photo]['id_photo']
            attachment = f"photo{self.candidate['id']}_{photo_id}"
            self.path = os.path.join("interface", "keyboards", "photo.json")
            result = {"message": answer, "path": self.path, "attachment": attachment}
        else:
            answer = f"У {self.candidate['first_name']} {self.candidate['last_name']} нет такой фотографии!"
            result = {"message": answer, "path": self.path, "attachment": None}
        self.saving_parameters()
        return result
