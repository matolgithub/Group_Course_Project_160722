"""
Модуль insert_photo предназначен для выполнения операций над фотографиями пользователей.
Принимает в качестве параметров данные о фото, а также о пользователях и вносит данные в соответствующие таблицы БД:
photo_list, likes_list.
"""
from db.create_table import TableDb

# Класс для работы с фотографиями пользователей.
class Photo:
    """
    Класс Photo разработан для работы с фотографиями пользователей.
    Атрибуты класса:
    ----------------
    data_base (str) - название базы данных,
    user (str) - название пользователя базы данных
    Методы класса:
    ---------------
    in_photolist_table
    параметры метода:
    bot_user_user_id (int) - id пользователя бота, user_id (int) - id пользователя кандидата,
    photo_link (str) - ссылка на фото, photo_id (id) - id фото.

    in_likeslist_table
    параметры метода:
    bot_user_user_id (int) - id пользователя бота, user_id (int) - id пользователя кандидата,
    photo_link (str) - ссылка на фото, photo_id (id) - id фото.
    """

    # Функция инициализации класса Photo
    def __init__(self, data_base, user):
        """
        Функция инициализации класса DataIn.
        :param data_base: (str) - название базы данных
        :param user: (str) - название пользователя базы данных
        """
        self.data_base = data_base
        self.user = user

    # Функция заносит данные по фотографиям в таблицу photo_list.
    def in_photolist_table(self, bot_user_user_id, user_id, photo_link, photo_id):
        """
        Функция внесения в таблицу photo_list данных о фотографиях: ссылка, ID фотографии, ID пользователя кандидата.
        Если такие данные уже есть в таблице, то ничего не заносится. На вход функции поступают 4 параметра:
        bot_user_user_id, user_id, photo_link, photo_id. На выходе возвращается результат выполнения insert_status.
        Если запись в таблицу сделана, то True, если нет, то False.
        :return: insert_status (bool)
        """

        dict_photo = {
            bot_user_user_id: [user_id, photo_link, photo_id]
        }
        new_photo_link = ''
        new_dict_photo = {}
        insert_status = True

        # Поиск спецсимвола % в ссылках и замена на %%, в противном случае данные не записываются в таблицы БД.
        for key, value in dict_photo.items():
            link = value[1]
            for symbol in link:
                if symbol == '%':
                    new_symbol = symbol.replace('%', '%%')
                    new_photo_link += new_symbol
                else:
                    new_photo_link += symbol
            new_dict_photo[key] = [value[0], new_photo_link, value[2]]

        table_db_obj = TableDb(self.data_base, self.user)
        connect = table_db_obj.db_connect()

        # Проверка наличия пользователей в таблице user_data.
        for key, value in dict_photo.items():
            req_check_user_bot = f'SELECT user_id FROM user_data WHERE user_id={key};'
            is_exist_user_bot = connect.execute(req_check_user_bot).fetchall()
            if is_exist_user_bot == []:
                connect.execute(f'INSERT INTO user_data(user_id) VALUES({key});')
            req_check_elect_user = f'SELECT user_id FROM user_data WHERE user_id={value[0]};'
            is_exist_elect_user = connect.execute(req_check_elect_user).fetchall()
            if is_exist_elect_user == []:
                connect.execute(f'INSERT INTO user_data(user_id) VALUES({value[0]});')

            # Внесение данных о пользователях в таблицу photo_list.
            req_sql = f"INSERT INTO photo_list(photo_link, photo_id, user_data_user_id) VALUES('{value[1]}'," \
                      f" {value[2]}, {value[0]});"
            req_check_sql = f'SELECT user_data_user_id, photo_id FROM photo_list' \
                            f' WHERE user_data_user_id={value[0]} AND photo_id={value[2]};'
            is_exist = connect.execute(req_check_sql).fetchall()

            # Проверка и установление конечного статуса выполнения функции.
            if is_exist != []:
                insert_status = False
            else:
                connect.execute(req_sql)
        return insert_status

    # Функция заносит данные по "лайкнутым" фотографиям в таблицы likes_list и photo_list.
    def in_likeslist_table(self, bot_user_user_id, user_id, photo_link, photo_id):
        """
        Функция внесения в БД данных о фотографиях, на которые поставили "лайк". На вход принимаются четыре
        параметра, bot_user_user_id, user_id, photo_link, photo_id. На выходе функции - статус выполнения операции.
        Если запись в таблицу likes_list сделана - True, если нет - False.
        :return: insert_status (bool)
        """

        dict_photo = {
            bot_user_user_id: [user_id, photo_link, photo_id]
        }
        id_list = []
        check_insert_list = []
        insert_status = True

        # Занесение данных о фото в таблицу photo-list.
        photo_list_obj = Photo(self.data_base, self.user)
        photo_list_obj.in_photolist_table(bot_user_user_id, user_id, photo_link, photo_id)

        table_db_obj = TableDb(self.data_base, self.user)
        connect = table_db_obj.db_connect()

        # Занесение данных о фото в таблицу likes-list.
        for key, value in dict_photo.items():
            req_search_id = f'SELECT id FROM photo_list WHERE photo_id={value[2]};'
            list_photo_list_id = connect.execute(req_search_id).fetchall()
            for item in list_photo_list_id:
                for id_value in item:
                    id_list.append(id_value)
                    req_sql = f"INSERT INTO likes_list(bot_user_user_id, photo_list_id) VALUES({key}, {id_value});"
                    connect.execute(req_sql)
                    # Проверка внесения данных о лайкнутых фото в таблицу likes_list базы данных.
                    req_check_ll_insert = f'SELECT bot_user_user_id FROM likes_list WHERE ' \
                                          f'bot_user_user_id={key} AND photo_list_id={id_value};'
                    list_check_ll_insert = connect.execute(req_check_ll_insert).fetchall()
                    check_insert_list.append(list_check_ll_insert)

        # Проверка и установление конечного статуса выполнения функции.
        if check_insert_list == []:
            insert_status = False
        return insert_status


# if __name__ == '__main__':
    # Photo.in_photolist_table(Photo('db_dating', 'user_dating'))
    # Photo.in_likeslist_table(Photo('db_dating', 'user_dating'))
