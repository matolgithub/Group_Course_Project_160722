"""
Модуль insert_data разработан для получения и записи данных о пользователях в таблицы базы данных: user_data,
black_list, elected_list.
"""
import sqlalchemy
from sqlalchemy import exc

from db.create_table import TableDb


# Класс DataIn создан для внесения данных о пользователях в таблицы БД.
class DataIn:
    """
    Класс DataIn выполнен для получения и записи данных о пользователях в таблицы базы данных: user_data,
    black_list, elected_list.
    Атрибуты класса:
    ----------------
    filename (str) - название файла, в который записывается SQL-запрос на внесение данных в БД.
    data_base (str) - название базы данных,
    user (str) - название пользователя базы данных
    Методы класса:
    --------------
    get_data
    Параметры: user_id (int) - id пользователя VK, profile_link (str) - ссылка на профиль, age (int) - возраст,
    first_name (str) - имя, last_name (str) - фамилия, sex (int) - пол, city (str) - название города,
    token (str) - токен пользователя, groups (int) - id группы, interests (str) - интересы пользователя,
    music (str) - музыкальные интересы, books (str) - книги, авторы, чтение.
    Return: dict_user (dict) - принятые данные в виде словаря.
    write_file
    Без входных параметров, записывает файл с данными пользователя, return: write_result (str).
    read_file
    Без входных параметров. Считывает данные в виде SQL-запроса с записанного ранее файла.
    return: read_list (list) - список SQL-запросов для занесения данных пользователей в БД.
    insert_user_table
    Без входных параметров. Считывает SQL-запросы с записанного файла и исполняет их, занося данные пользователей
    в таблицу user_data базы данных.
    return: insert_result (bool) - True, если запись внесена, comment_result (str) - комментарий о результате операции.
    in_elected_table
    Параметры: user_bot (int) - id бот пользователя, elected_user (int) - id выбранного кандидата.
    Метод вносит выбранного пользователя в список Избранных.
    return: list_insert_result (list) - список списков в котором есть статус операции (True, если выполнено) и
    комментарий о результате выполнения (str).
    in_blacklist_table
    Параметры: user_bot (int) - id бот пользователя, blacklist_user (int) - id пользователя, которого нужно внести
    в черный список.
    Метод вносит выбранного пользователя в черный список.
    return: list_insert_result (list) - список списков в котором есть статус операции (True, если выполнено) и
    комментарий о результате выполнения (str).
    """

    # Функция инициализации класса Data_In
    def __init__(self, filename, data_base, user):
        """
        Функция инициализации класса DataIn.
        :param filename: (str) - название файла, в который записываются SQL-запросы
        :param data_base: (str) - название базы данных
        :param user: (str) - название пользователя базы данных
        """
        self.filename = filename
        self.data_base = data_base
        self.user = user

    # Функция получения данных в виде словаря.
    def get_data(self, user_id, profile_link, age, first_name, last_name, sex, city, token, groups, interests,
                 music, books):
        """
        Функция получения данных о пользователях в виде словаря.
        Параметры: user_id (int) - id пользователя VK, profile_link (str) - ссылка на профиль, age (int) - возраст,
        first_name (str) - имя, last_name (str) - фамилия, sex (int) - пол, city (str) - название города,
        token (str) - токен пользователя, groups (int) - id группы, interests (str) - интересы пользователя,
        music (str) - музыкальные интересы, books (str) - книги, авторы, чтение.
        Return: dict_user (dict) - принятые данные в виде словаря.
        """
        dict_user = {
            user_id: [profile_link, age, first_name, last_name, sex, city, token, groups, interests,
                      music, books]
        }
        return dict_user

    # Функция зыписывает данные, полученные из функции get_data в файл Script_Insert_SQL_table_data.sql.
    def write_file(self):
        """
        Функция записи данных, полученных из функции get_data в файл Script_Insert_SQL_table_data.sql.
        :return: write_result (str)
        """
        write_obj = DataIn(self.filename, self.data_base, self.user)
        with open(self.filename, 'w', encoding='utf-8') as file:
            for keys, item in write_obj.get_data().items():
                insert_text = 'INSERT INTO user_data(user_id, profile_link, age, first_name, last_name, sex, city,' \
                              ' token, groups, interests, music, books)'
                values_text = f' VALUES({keys}'
                file.write(f'{insert_text}')
                for elem in item:
                    if type(elem) != str:
                        values_text += f', {str(elem)}'
                    elif type(elem) == str:
                        values_text += f""", '{elem}'"""
                values_text = values_text + ');'
                file.write(f'{values_text}\n')
        write_result = f'Файл {self.filename} записан.'
        return write_result

    # Функция считывания данных, полученных из файла Script_Insert_SQL_table_data.sql
    def read_file(self):
        """
        Функция считывания данных, полученных из файла Script_Insert_SQL_table_data.sql.
        :return: read_list (list)
        """

        with open(self.filename, 'r', encoding='utf-8') as file:
            read_data = file.readlines()
            read_list = list(item.strip() for item in read_data)
        return read_list

    # Функция заносит данные из файла Script_Insert_SQL_table_data.sql в базу данных в таблицу user_data.
    # Вносятся только новые данные, если какой-то пользователь в таблице есть, то не дублируется.
    def insert_user_table(self):
        """
        Функция insert_user_table даёт возможность записывать данные о пользователях VK в базу данных.
        Последовательность выполняемых операций: данные принимаются в функцию get_data в виде словаря, записываются
        в файл Script_Insert_SQL_table_data.sql в виде SQL-запроса при помощи функции write_file, далее SQL-запрос
        считывается функцией read_file и исполняется. Предусмотрено получение на вход данных в словаре с любым
        количеством ключей. Если словарь пустой, то ничего в базу не записывается. Функция способна записывать в файл
        и исполнять любое количество SQL-запросов.
        :return: insert_result (bool), comment_result (str)
        """

        table_db_obj = TableDb(self.data_base, self.user)
        connect = table_db_obj.db_connect()

        insert_user_obj = DataIn(self.filename, self.data_base, self.user)
        insert_user_obj.write_file()
        insert_list_data = insert_user_obj.read_file()
        insert_result = True
        comment_result = 'Запись успешно осуществлена!'

        for item in insert_list_data:
            try:
                connect.execute(item.strip())
            except sqlalchemy.exc.IntegrityError:
                comment_result = f'Запись: {item} в таблицу не сделана, т.к. пользователь уже существует!'
                insert_result = False
        return insert_result, comment_result

    # Функция заносит данные переданного пользователя в таблицу Избранных (elected_list),
    # пользователь вносится в поле user_data_user_id с проверкой дублирования.
    def in_elected_table(self, user_bot, elected_user):
        """
        Функция занесения пользователя в Избранные (таблица elected_list).
        ID выбранного пользователя помещается в поле user_data_user_id.
        Также осуществляется проверка на дублирование. В случае повторного внесения
        возвращается соответствующая информация.
        :return: list_insert_result (list)
        """

        list_insert_result = []
        dict_electlist_user = {user_bot: elected_user}
        table_db_obj = TableDb(self.data_base, self.user)
        connect = table_db_obj.db_connect()
        insert_result = True
        comment_result = f'Запись {elected_user} внесена в список Избранных!'
        for key, value in dict_electlist_user.items():
            # Проверка наличия пользователей в таблице user_data.
            req_check_user_bot = f'SELECT user_id FROM user_data WHERE user_id={key};'
            is_exist_user_bot = connect.execute(req_check_user_bot).fetchall()
            if is_exist_user_bot == []:
                connect.execute(f'INSERT INTO user_data(user_id) VALUES({key});')
            req_check_elect_user = f'SELECT user_id FROM user_data WHERE user_id={value};'
            is_exist_elect_user = connect.execute(req_check_elect_user).fetchall()
            if is_exist_elect_user == []:
                connect.execute(f'INSERT INTO user_data(user_id) VALUES({value});')

            # Внесение данных о пользователях в таблицу Избранных.
            req_sql = f'INSERT INTO elected_list(user_data_user_id, bot_user_user_id) VALUES({value}, {key});'
            user_elect_exist = f'SELECT user_data_user_id, bot_user_user_id FROM elected_list' \
                               f' WHERE user_data_user_id={elected_user} AND bot_user_user_id={user_bot};'
            is_exist = connect.execute(user_elect_exist).fetchall()

            # Проверка внесения данных о пользователях в таблицу Избранных.
            if is_exist != []:
                comment_result = f'Запись: {req_sql} в таблицу не сделана, т.к. пользователь {value} для пользователя' \
                                 f' {key} уже существует в списке Избранных!'
                insert_result = False
            else:
                connect.execute(req_sql)
            list_insert_result.append([insert_result, comment_result])
        return list_insert_result

    # Функция заносит данные переданного пользователя в Чёрный список (black_list).
    # Заблокированный пользователь вносится в поле user_data_user_id с проверкой дублирования.
    def in_blacklist_table(self, user_bot, blacklist_user):
        """
        Функция занесения пользователя в Чёрный список (таблица black_list).
        ID заблокированного пользователя помещается в поле user_data_user_id.
        Также осуществляется проверка на дублирование. В случае повторного внесения
        возвращается соответствующая информация.
        :return: list_insert_result (list)
        """

        list_insert_result = []
        dict_blacklist_user = {user_bot: blacklist_user}
        table_db_obj = TableDb(self.data_base, self.user)
        connect = table_db_obj.db_connect()
        insert_result = True
        comment_result = f'Запись {blacklist_user} внесена в черный список!'
        for key, value in dict_blacklist_user.items():
            # Проверка наличия пользователей в таблице user_data.
            req_check_user_bot = f'SELECT user_id FROM user_data WHERE user_id={key};'
            is_exist_user_bot = connect.execute(req_check_user_bot).fetchall()
            if is_exist_user_bot == []:
                connect.execute(f'INSERT INTO user_data(user_id) VALUES({key});')
            req_check_bl_user = f'SELECT user_id FROM user_data WHERE user_id={value};'
            is_exist_bl_user = connect.execute(req_check_bl_user).fetchall()
            if is_exist_bl_user == []:
                connect.execute(f'INSERT INTO user_data(user_id) VALUES({value});')

            # Внесение данных о пользователях в Черный список.
            req_sql = f'INSERT INTO black_list(user_data_user_id, bot_user_user_id) VALUES({value}, {key});'
            user_blacklist_exist = f'SELECT user_data_user_id, bot_user_user_id FROM black_list' \
                                   f' WHERE user_data_user_id={blacklist_user} AND bot_user_user_id={user_bot};'
            is_exist = connect.execute(user_blacklist_exist).fetchall()

            # Проверка внесения данных о пользователях в Чёрный список.
            if is_exist != []:
                comment_result = f'Запись: {req_sql} в таблицу не сделана, т.к. пользователь {value} для пользователя' \
                                 f' {key} уже существует в Чёрном списке!'
                insert_result = False
            else:
                connect.execute(req_sql)
            list_insert_result.append([insert_result, comment_result])
        return list_insert_result


# if __name__ == '__main__':
    # DataIn.insert_user_table(DataIn('Script_Insert_SQL_table_data.sql', 'db_dating', 'user_dating'))
    # DataIn.in_blacklist_table(DataIn('Script_Insert_SQL_table_data.sql', 'db_dating', 'user_dating'))
    # DataIn.in_elected_table(DataIn('Script_Insert_SQL_table_data.sql', 'db_dating', 'user_dating'))
