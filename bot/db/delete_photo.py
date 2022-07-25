"""
Модуль delete_photo разработан для проведения операций удаления из 2-х таблиц БД: photo_list, likes_list.
"""
from db.create_table import TableDb
from db.delete_data import Disposal


# Класс для удаления фотографий пользователей.
class DelPhoto:
    """
    Класс DelPhoto предназначен для выполнения удаления фото из таблиц photo_list, likes_list.
    Атрибуты класса:
    ----------------
    data_base (str) - название базы данных,
    user (str) - название пользователя базы данных
    Методы класса:
    --------------
    del_id_photolist
    Параметры: bot_user_id (int) - id бот пользоваетля, user_id (int) - id пользователя кандидата,
    del_photo_id (int) - id фотографии, подлежащей удалению.
    """

    # Функция инициализации класса DelPhoto.
    def __init__(self, data_base, user):
        """
        Функция инициализации класса DelPhoto.
        :param data_base: (str) - название базы данных
        :param user: (str) - название пользователя базы данных
        """
        self.data_base = data_base
        self. user = user

    # Функция удаления лайкнутых фото из двух списков: photo_list, likes_list.
    def del_id_photolist(self, bot_user_id, user_id, del_photo_id):
        """
        Функция del_id_photolist принимает на вход три параметра: id пользователя бота, id пользователя,
        фотографию которого нужно удалить и id самой фотографии.
        Удаляет данные о фото в списках photo_list, likes_list. В результате выполнения возвращает
        пустой список after_del_list.
        :return: after_del_list
        """

        clean_id_list = []
        table_db_obj = TableDb(self.data_base, self.user)
        connect = table_db_obj.db_connect()

        # Формирование и исполнение SQL-запроса на поиск в таблице photo_list нужных фото.
        req_search_id = f'SELECT id FROM photo_list WHERE photo_id={del_photo_id} AND user_data_user_id={user_id};'
        list_photo_list_id = connect.execute(req_search_id).fetchall()
        for item_list in list_photo_list_id:
            for id_value in item_list:
                clean_id_list.append(id_value)

        # Формирование и исполнение SQL-запроса на удаление записей в таблице likes_list выбранных фото.
        for ids in clean_id_list:
            req_del_id_ll = f'DELETE FROM likes_list WHERE bot_user_user_id={bot_user_id} AND ' \
                            f'photo_list_id={ids};'
            connect.execute(req_del_id_ll)

        # Формирование и исполнение SQL-запроса на удаление записей в таблице photo_list.
        req_del_id_pl = f'DELETE FROM photo_list WHERE user_data_user_id={user_id} AND photo_id={del_photo_id};'
        connect.execute(req_del_id_pl)

        # Проверка результата операции удаления.
        req_search_id = f'SELECT id FROM photo_list WHERE photo_id={del_photo_id} AND user_data_user_id={user_id};'
        after_del_list = connect.execute(req_search_id).fetchall()

        # Проверка и удаление пустых записей из основной таблицы базы данных user_data.
        del_user_obj = Disposal(self.data_base, self.user)
        del_user_obj.del_null_user(user_id)
        del_user_obj.del_null_user(bot_user_id)
        return after_del_list


if __name__ == '__main__':
    DelPhoto.del_id_photolist(DelPhoto('db_dating', 'user_dating'))
