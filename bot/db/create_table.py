"""
Модуль create_table.py разработан для создания пяти таблиц базы данных, в соответствии с тех.заданием проекта.
"""
import sqlalchemy
from db.create_user_db import DatingDb


# Класс TableDb - для создания таблиц БД и подключения к ним.
class TableDb:
    """
    Класс TableDb разаработан для создания пяти таблиц БД и подключения к ним.
    Таблицы: user_data, black_list, elected_list, photo_list, likes_list.
    Атрибуты класса:
    -----------------
    data_base (str) - название базы данных,
    user (str) - название пользователя базы данных
    Методы класса:
    ---------------
    db_connect
    Без параметров, возвращает объект sqlalchemy - connect.
    Для работы необходим пароль, который хранится в файле sqlpsw.txt.
    create_tables
    Без параметров, возвращает список созданных в базе данных таблиц tables_list.
    """

    # Функция инициализации класса TableDb
    def __init__(self, data_base, user):
        """
        Функция инициализации класса TableDb
        :param data_base: (str) - название базы данных
        :param user: (str) - название пользователя базы данных
        """
        self.data_base = data_base
        self.user = user

    # Функция подключения
    def db_connect(self):
        """
        Функция db_connect. Без параметров, возвращает объект sqlalchemy - connect.
        Для работы необходим пароль, который хранится в файле sqlpsw.txt.
        :return: connect
        """
        pswd = DatingDb.sql_psw()
        user_db = f'postgresql://{self.user}:{pswd}@localhost:5432/{self.data_base}'
        engine = sqlalchemy.create_engine(user_db)
        connect = engine.connect()
        return connect

    # Функция создания таблиц в базе данных
    def create_tables(self):
        """
        Функция create_tables создаёт пять таблиц и в конце работы выводит их список.
        Перечень таблиц: user_data, black_list, elected_list, photo_list, likes_list.
        :return: tables_list (тип данных - list)
        """
        table_db_obj = TableDb(self.data_base, self.user)
        connect = table_db_obj.db_connect()
        # Изначально таблица tables_list - пустая.
        tables_list = []
        # Формируем первую часть SQL-запроса.
        sql_table = 'CREATE TABLE IF NOT EXISTS'
        # Передаём данные: названия таблиц, список полей, тип данных, ограничения, связи между полями таблиц
        # в виде словаря.
        dict_tables = {
            'user_data': ['user_id INTEGER NOT NULL PRIMARY KEY,', 'profile_link VARCHAR(60),',
                          'age INTEGER CHECK(age<150),', 'first_name VARCHAR(40),', 'last_name VARCHAR(40),',
                          'sex INTEGER,', 'city VARCHAR(60),', 'token VARCHAR(200),', 'groups INTEGER,',
                          'interests TEXT,', 'music TEXT,', 'books TEXT'],
            'elected_list': ['user_data_user_id INTEGER NOT NULL REFERENCES user_data(user_id),',
                             'bot_user_user_id INTEGER NOT NULL REFERENCES user_data(user_id),',
                             'CONSTRAINT pk_el PRIMARY KEY (user_data_user_id, bot_user_user_id)'],
            'black_list': ['user_data_user_id INTEGER NOT NULL REFERENCES user_data(user_id),',
                           'bot_user_user_id INTEGER NOT NULL REFERENCES user_data(user_id),',
                           'CONSTRAINT pk_bl PRIMARY KEY (user_data_user_id, bot_user_user_id)'],
            'photo_list': ['id SERIAL PRIMARY KEY,', 'photo_link VARCHAR(250),', 'photo_id INTEGER,',
                           'user_data_user_id INTEGER NOT NULL REFERENCES user_data(user_id)'],
            'likes_list': ['id SERIAL PRIMARY KEY,', 'bot_user_user_id INTEGER NOT '
                                                     'NULL REFERENCES user_data(user_id),',
                           'photo_list_id INTEGER NOT NULL '
                           'REFERENCES photo_list(id)']
        }
        # Формируем вторую часть SQL-запросов для каждой из таблиц.
        for tbl_name, tbl_col in dict_tables.items():
            if tbl_name == 'user_data':
                req = f"{sql_table} {tbl_name} ("
                for item in range(len(tbl_col)):
                    req += f"{tbl_col[item]} "
                req = req + ");"
            elif tbl_name == 'black_list' or tbl_name == 'elected_list':
                req = f"{sql_table} {tbl_name} ({tbl_col[0]} {tbl_col[1]} {tbl_col[2]});"
            elif tbl_name == 'photo_list':
                req = f"{sql_table} {tbl_name} ({tbl_col[0]} {tbl_col[1]} {tbl_col[2]} {tbl_col[3]});"
            elif tbl_name == 'likes_list':
                req = f"{sql_table} {tbl_name} ({tbl_col[0]} {tbl_col[1]} {tbl_col[2]});"
            # Исполняем сформированные SQL-запросы.
            connect.execute(req)
            tables_list.append(tbl_name)
        return tables_list


if __name__ == '__main__':
    TableDb.create_tables(TableDb('db_dating', 'user_dating'))
