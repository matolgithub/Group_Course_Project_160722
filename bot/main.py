"""
Программа чат-бот для знакомств в социальной сети Вконтакте
"""

from interface.config import vk_api_token, vk_group_id
from interface.server import Server
from db.create_user_db import DatingDb
from db.create_table import TableDb


if __name__ == "__main__":

    # Создание базы данных и пользователя
    db_user_obj = DatingDb('db_dating', 'user_dating')
    db_user_obj.db_user_create()

    # Создание всех таблиц в соответствии с заданием
    table_db_obj = TableDb('db_dating', 'user_dating')
    table_db_obj.create_tables()

    # Подключение к чату и сообщениям сообщества
    dating = Server(api_token=vk_api_token, group_id=vk_group_id, server_name="dating")
    dating.start()
