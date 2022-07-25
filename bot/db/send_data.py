"""
Модуль send_data разработан для передачи в бот данных пользователей из списка Избранных и
Черного списка по полученным запросам.
"""
from db.create_table import TableDb


# Класс Parcel создан для вывода и передачи в бот данных пользователей из списка Избранные и Черного списка.
class Parcel:
    """
    Класс Parcel сделан для выемки из БД и передачи в бот данных пользователей из списка Избранные и Черного списка.
    Атрибуты класса:
    ----------------
    data_base (str) - название базы данных,
    user (str) - название пользователя базы данных
    Методы класса:
    ---------------
    black_list_output
    Параметр: user_id (int) - id пользователя, для которого выводится и передаётся Черный список.
    Вывод из базы данных чёрного списка для пользователя user_id с проверкой на дублирование.
    return: result_bl_output_list (list) - результирующий список выполнения операции.
    elected_list_output
    Параметр: user_id (int) - id пользователя, для которого выводится и передаётся список Избранных.
    Вывод из базы данных чёрного списка для пользователя user_id с проверкой на дублирование.
    return: result_el_output_list (list) - результирующий список выполнения операции.
    """

    # Функция инициализации класса Parcel
    def __init__(self, data_base, user):
        """
        Функция инициализации класса Parcel.
        :param data_base: (str) - название базы данных
        :param user: (str) - название пользователя базы данных
        """
        self.data_base = data_base
        self. user = user

    # Функция вывода из базы данных чёрного списка для пользователя user_id с проверкой на дублирование.
    def black_list_output(self, user_id):
        """
        Функция black_list_output принимает на вход id пользователя и выводит список id всех пользователей,
        которых он вносил ранее в чёрный список. В случае, если в БД нет пользователя с переданным на вход id,
        то возвращается пустой список. Выведенный список исключает повторение записей в нём.
        Примечание: в списке тип данных - int.
        :return: result_bl_output_list (list)
        """

        result_bl_output_list = []
        table_db_obj = TableDb(self.data_base, self.user)
        connect = table_db_obj.db_connect()
        req_output = f'SELECT user_data_user_id FROM black_list WHERE bot_user_user_id={user_id};'
        output_list = connect.execute(req_output).fetchall()
        for item_list in output_list:
            clean_id = ''
            for symbol in str(item_list):
                if symbol.isdigit():
                    clean_id += symbol
            result_bl_output_list.append(int(clean_id))
        result_bl_output_list = list(set(result_bl_output_list))
        return result_bl_output_list

    # Функция вывода из базы данных списка Избранных для пользователя user_id с проверкой на дублирование.
    def elected_list_output(self, user_id):
        """
        Функция elected_list_output принимает на вход id пользователя и выводит список id всех пользователей,
        которых он вносил ранее в список Избранных. В случае, если в БД нет пользователя с переданным на вход id,
        то возвращается пустой список. Выведенный список исключает повторение записей в нём.
        Примечание: в списке тип данных - int.
        :return: result_el_output_list (list)
        """

        result_el_output_list = []
        table_db_obj = TableDb(self.data_base, self.user)
        connect = table_db_obj.db_connect()
        req_output = f'SELECT user_data_user_id FROM elected_list WHERE bot_user_user_id={user_id};'
        output_list = connect.execute(req_output).fetchall()
        for item_list in output_list:
            clean_id = ''
            for symbol in str(item_list):
                if symbol.isdigit():
                    clean_id += symbol
            result_el_output_list.append(int(clean_id))
        result_el_output_list = list(set(result_el_output_list))
        return result_el_output_list


# if __name__ == '__main__':
    # Parcel.black_list_output(Parcel('db_dating', 'user_dating'))
    # Parcel.elected_list_output(Parcel('db_dating', 'user_dating'))
