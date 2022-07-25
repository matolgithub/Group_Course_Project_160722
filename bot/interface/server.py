import random
import os

import vk_api.vk_api
from vk_api.bot_longpoll import VkBotEventType
from vk_api.bot_longpoll import VkBotLongPoll

from interface.commander import Commander
from interface.config import vk_group_id


class Server:
    """
    Обеспечивает обмен сообщениями между определенной группой ВК и пользователями ВК
    """

    def __init__(self, api_token: str, group_id: int, server_name: str = "Empty"):
        """
        Инициализация класса "Server"

        :param api_token: Токен сообщества, к которому подключается бот
        :param group_id: id сообщества, к которому подключается бот
        :param server_name: название данного подключения
        """

        # Даем серверу имя
        self.server_name = server_name

        # Передаем id сообщества
        self.group_id = group_id

        # Для Long Poll
        self.vk = vk_api.VkApi(token=api_token)

        # Для использоания Long Poll API
        self.long_poll = VkBotLongPoll(self.vk, group_id, wait=20)

        # Для вызова методов vk_api
        self.vk_api = self.vk.get_api()

        # Словарь для каждого отдельного пользователя
        self.users = {}

    def send_msg(self, send_id: int, message: str, path: str, attach=None):
        """
        Отправка сообщения через метод messages.send

        :param send_id: vk id пользователя, который получит сообщение
        :param message: содержимое отправляемого письма
        :param path: путь к файлу с кнопками
        :param attach: медиавложения к личному сообщению, перечисленные через запятую.
        :return: None
        """
        return self.vk_api.messages.send(peer_id=send_id,
                                         message=message,
                                         random_id=random.randint(0, 2048),
                                         keyboard=open(path, "r", encoding="UTF-8").read(),
                                         attachment=attach)

    def start(self):
        """
        Прием сообщений пользователя и отправка ему ответного сообщения

        Метод принимает как личные сообщения пользователя, так и сообщения в чате сообщества.
        Если у пользователя запрещен прием сообщений от сообщества, то в чат группы отправится сообщение с просьбой
        разрешить сообщения.
        """
        for event in self.long_poll.listen():  # Слушаем сервер
            if event.type == VkBotEventType.MESSAGE_NEW:

                if event.message.from_id not in self.users:
                    user_name = self.get_user_name(event.message.from_id)
                    self.users[event.message.from_id] = Commander(vk_id=event.message.from_id, user_name=user_name)

                # Пришло новое сообщение
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if self.vk_api.messages.isMessagesFromGroupAllowed(
                            group_id=vk_group_id, user_id=event.message.from_id)["is_allowed"] == 0:
                        path = os.path.join("interface", "keyboards", "none.json")
                        message = f"{self.users[event.message.from_id].user_name}, " \
                                  f"разрешите сообществу присылать Вам сообщения!"
                        self.send_msg(event.message.peer_id, message, path)
                    else:
                        result = self.users[event.message.from_id].input(event.message.text)
                        self.send_msg(event.message.from_id, result["message"], result["path"], result["attachment"])

    def get_user_name(self, user_id: int):
        """ 
        Получаем имя пользователя

        :param user_id: id пользователя ВК, имя которого хотим получить
        """
        return self.vk_api.users.get(user_id=user_id)[0]['first_name']
