"""
Модуль delete_data.py разработан для удаления, в случае необходимости, записей из 3-х таблиц:
user_data, black_list, elected_list.
"""
from db.create_table import TableDb


# Класс для операций удаления ненужных записей из таблиц базы данных.
class Disposal:
    """
    Класс Disposal создан для операций удаления из таблиц базы данных: user_data, black_list, elected_list.
    Атрибуты класса:
    ----------------
    data_base (str) - название базы данных,
    user (str) - название пользователя базы данных
    Методы класса:
    --------------
    del_null_user
    Параметр: user: (int) id пользователя, нулевая запись которого подлежит проверке и удалению.
    Метод возвращает: clean_status (Bool), check_id_list (list).
    del_id_blacklist
    Параметры: user_id (int) - id пользователя бота, del_user_id (int) - id пользователя, внесённого в черный список.
    Метод возвращает после операции удаления список after_del_list (list).
    del_id_electlist
    Параметры: user_id (int) - id пользователя бота, del_user_id (int) - id пользователя, внесённого в список Избранных.
    Метод возвращает после операции удаления список after_del_list (list).
    """

    # Функция инициализации класса Disposal
    def __init__(self, data_base, user):
        """
        Функция инициализации класса Disposal.
        :param data_base: (str) - название базы данных
        :param user: (str) - название пользователя базы данных
        """
        self.data_base = data_base
        self.user = user

    # Функция удаления "пустых" несвязанных данных пользователей из таблицы user_data по id пользователя.
    def del_null_user(self, user):
        """
        Функция осуществляет проверку и чистку в таблице user_data базы данных. Если в таблице в поле есть пользователь
        user_id со всеми другими пустыми полями и при условии, что user_id отсутствует во всех остальных связанных
        таблицах, то эта запись удаляется из таблицы, и, соответственно, из базы. Начальный статус операции: False.
        Если запись удалена, то статус меняется на True. После успешного удаления записи также возвращается пустой
        список check_id_list.
        :return: clean_status, check_id_list
        """

        clean_status = False
        main_check_list = []

        table_db_obj = TableDb(self.data_base, self.user)
        connect = table_db_obj.db_connect()

        # Формирование SQL-запроса
        req_id_check = f'SELECT user_id FROM user_data WHERE user_id={user};'
        check_list_1 = connect.execute(req_id_check).fetchall()

        # Проверка наличия записей пользователя с таким же id в других таблицах.
        req_id_tables_check = f'SELECT bot_user_user_id FROM likes_list WHERE bot_user_user_id={user};'
        check_list_2 = connect.execute(req_id_tables_check).fetchall()
        if check_list_2 != []:
            main_check_list.append(check_list_2)
        req_id_el_check = f'SELECT user_data_user_id, bot_user_user_id FROM elected_list WHERE ' \
                          f'user_data_user_id={user} or bot_user_user_id={user};'
        check_list_3 = connect.execute(req_id_el_check).fetchall()
        if check_list_3 != []:
            main_check_list.append(check_list_3)
        req_id_bl_check = f'SELECT user_data_user_id, bot_user_user_id FROM black_list WHERE ' \
                          f'user_data_user_id={user} or bot_user_user_id={user};'
        check_list_4 = connect.execute(req_id_bl_check).fetchall()
        if check_list_4 != []:
            main_check_list.append(check_list_4)
        req_id_pl_check = f'SELECT user_data_user_id FROM photo_list WHERE ' \
                          f'user_data_user_id={user};'
        check_list_5 = connect.execute(req_id_pl_check).fetchall()
        if check_list_5 != []:
            main_check_list.append(check_list_5)

        # Удаление записи по пользователю user из основной таблицы при условии, что в других таблицах данных не нашлось.
        if check_list_1 != []:
            if main_check_list == []:
                req_del_user_id = f'DELETE FROM user_data WHERE user_id={user};'
                connect.execute(req_del_user_id)
                clean_status = True
        req_del_check = f'SELECT user_id FROM user_data WHERE user_id={user};'
        check_id_list = connect.execute(req_del_check).fetchall()
        return clean_status, check_id_list

    # Функция удаления из чёрного списка базы данных ID пользователя (del_user_id) для пользователя user_id.
    def del_id_blacklist(self, user_id, del_user_id):
        """
        Функция del_id_blacklist принимает на вход id двоих пользователей и удаляет id нужного пользователя,
        который ранее был внесён в чёрный список. В случае, если в БД нет пользователя, для которого выполняется
        удаление, то возвращается пустой список. Если в БД нет пользователя, которого нужно удалить, то возвращается
        черный список. В нём, в качестве подтверждения, не будет пользователя на удаление которого поступил запрос.
        Если чёрный список пуст, то он и будет возвращён.
        :return: after_del_list
        """
        after_del_list = []
        table_db_obj = TableDb(self.data_base, self.user)
        connect = table_db_obj.db_connect()

        # Формирование и исполнение SQL-запроса на удаление записи из черного списка.
        req_del_id_bl = f'DELETE FROM black_list WHERE bot_user_user_id={user_id} AND user_data_user_id={del_user_id};'
        connect.execute(req_del_id_bl)

        # Проверка результата операции удаления.
        req_del_check = f'SELECT user_data_user_id FROM black_list WHERE bot_user_user_id={user_id};'
        check_list = connect.execute(req_del_check).fetchall()
        for item_list in check_list:
            clean_id = ''
            for symbol in str(item_list):
                if symbol.isdigit():
                    clean_id += symbol
            after_del_list.append(int(clean_id))
        after_del_list = list(set(after_del_list))

        # Проверка и удаление пустых записей из основной таблицы базы данных user_data.
        del_user_obj = Disposal(self.data_base, self.user)
        del_user_obj.del_null_user(user_id)
        del_user_obj.del_null_user(del_user_id)
        return after_del_list

    # Функция удаления из списка Избранных базы данных ID пользователя (del_user_id) для пользователя user_id.
    def del_id_electlist(self, user_id, del_user_id):
        """
        Функция del_id_electlist принимает на вход id двоих пользователей и удаляет id нужного пользователя,
        который ранее был внесён в список Избранных. В случае, если в БД нет пользователя, для которого выполняется
        удаление, то возвращается пустой список. Если в БД нет пользователя, которого нужно удалить, то возвращается
        список Избранных. В нём, в качестве подтверждения, не будет пользователя на удаление которого поступил запрос.
        Если список Избранных пуст, то он и будет возвращён.
        :return: after_del_list
        """
        after_del_list = []
        table_db_obj = TableDb(self.data_base, self.user)
        connect = table_db_obj.db_connect()

        # Формирование и исполнение SQL-запроса на удаление записи из списка Избранных.
        req_del_id_el = f'DELETE FROM elected_list WHERE bot_user_user_id={user_id} AND ' \
                        f'user_data_user_id={del_user_id};'
        connect.execute(req_del_id_el)

        # Проверка результата операции удаления.
        req_del_check = f'SELECT user_data_user_id FROM elected_list WHERE bot_user_user_id={user_id};'
        check_list = connect.execute(req_del_check).fetchall()
        for item_list in check_list:
            clean_id = ''
            for symbol in str(item_list):
                if symbol.isdigit():
                    clean_id += symbol
            after_del_list.append(int(clean_id))
        after_del_list = list(set(after_del_list))

        # Проверка и удаление пустых записей из основной таблицы базы данных user_data.
        del_user_obj = Disposal(self.data_base, self.user)
        del_user_obj.del_null_user(user_id)
        del_user_obj.del_null_user(del_user_id)
        return after_del_list


# if __name__ == '__main__':
    # Disposal.del_id_blacklist(Disposal('db_dating', 'user_dating'))
    # Disposal.del_id_electlist(Disposal('db_dating', 'user_dating'))
    # Disposal.del_null_user(Disposal('db_dating', 'user_dating'))
