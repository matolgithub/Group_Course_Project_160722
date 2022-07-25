from interface.config import id_applications, version_vk_api

# Команды, привязанные к кнопкам
start = "Начать поиск"
next_contender = "Следующий/ая"
favorites = "В избранное"
add_blacklist = "В черный список"
blacklist = "Черный список"
remove_blacklist = "Удалить из ЧС"
favorites_list = "Список избранных"
continue_searching = "Продолжить поиск"
remove = "Удалить из избранного"
photo_1, photo_2, photo_3 = "Фото 1", "Фото 2", "Фото 3"
like = "Поставить лайк"
revoke_like = "Убрать лайк"
request_token = f"Для корректной работы бота пройдите по ссылке\n" \
                     f" https://oauth.vk.com/authorize?client_id={id_applications}&display=popup&" \
                     f"redirect_uri=https://oauth.vk.com/blank.html&" \
                     f"scope=photos,audio,offline,groups,wall&" \
                     f"response_type=token&v={version_vk_api}\n" \
                     f"Затем скопируйте весь текст из адресной строки, " \
                     f"появившейся новой вкладки и пришлите его в ответном сообщении."
