"""
Модуль create_user_db.py разработан для создания БД и пользователя базы данных.
"""
import sqlalchemy
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import exc


# Класс DatingDb для базы данных к чат-боту Dating на VK.
class DatingDb:
    """
    Данный класс DatingDb спрограммирован для базы данных к чат-боту Dating на VK.
    Атрибуты класса:
    ----------------
    data_base (str) - название базы данных,
    user (str) - название пользователя базы данных
    Методы класса:
    --------------
    sql_psw
    Без параметров. Записывает в файл 'sqlpsw.txt' пароль пользователя БД. Возвращает пароль в переменной psw.
    db_user_create
    Без параметров. Создаёт БД и пользоваетля БД. Их названия вносятся в результирующий список list_db_user_names.
    В этот же список вносятся результаты создания БД и пользователя. Метод после выполнения кода возвращает
    список list_db_user_names.
    """

    # Функция инициализации класса DatingDb
    def __init__(self, data_base, user):
        """
        Функция инициализации класса DatingDb.
        :param data_base: (str) - название базы данных
        :param user: (str) - название пользователя базы данных
        """
        self.data_base = data_base
        self.user = user

    @staticmethod
    # Функция чтения и возврата пароля из файла sqlpsw.txt.
    def sql_psw():
        """
        Функция sql_psw предназначена для чтения и возврата пароля
        из файла sqlpsw.txt
        :return: psw (str)
        """
        with open('sqlpsw.txt', 'r', encoding='utf-8') as file:
            psw = file.read().strip()
        return psw

    # Функция создания базы данных и пользователя.
    def db_user_create(self):
        """
        Функция db_user_create создаёт базу данных 'db_dating' и пользователя 'user_dating'.
        Их названия вносятся в результирующий список list_db_user_names.
        :return: list_db_user_names (тип данных - list)
        """

        list_db_user_names = []
        pswd = DatingDb.sql_psw()

        # Создание базы данных
        db = f'postgresql://postgres:{pswd}@localhost:5432/{self.data_base}'
        engine = sqlalchemy.create_engine(db)

        # Проверка по названию, создана БД ранее или нет.
        if not database_exists(engine.url):
            create_database(engine.url)
        result_db = database_exists(engine.url)

        # Создание пользователя БД.
        connection = engine.connect()
        try:
            connection.execute(f"CREATE USER {self.user} WITH PASSWORD '{pswd}';")
            result_user = f'User "{self.user}" exist.'
        except sqlalchemy.exc.ProgrammingError:
            result_user = f'User "{self.user}" already exist.'

        # Назначение созданного пользователя ранее созданной БД.
        connection.execute(f"ALTER DATABASE {self.data_base} OWNER TO {self.user};")

        # Формирование результирующего списка.
        list_db_user_names.append(self.data_base)
        list_db_user_names.append(self.user)
        list_db_user_names.append(result_db)
        list_db_user_names.append(result_user)
        return list_db_user_names
