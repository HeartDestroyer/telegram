# src/membership.py

import time
import aiohttp
from loguru import logger
from aiogram import exceptions

from .main import bot
from .config import PORTAL_BASE_URL

invite_link_cache = {}

# + Обращается к API портала возвращает True, если пользователь (user_id) должен находиться в группе (chat_id), иначе False
async def check_user_allowed(chat_id, user_id):
    """
    Обращается к API портала возвращает True, если пользователь (user_id) должен находиться в группе (chat_id), иначе False
    """
    url = f"{PORTAL_BASE_URL}/allowed/{chat_id}/{user_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                return data.get("allowed", False)
    except Exception as e:
        logger.error(f"Ошибка получения данных check_user_allowed: {e}")
        return False


# - Получает список групп ТГ с разрешёнными пользователями
async def get_group_memberships_json():
    """
    Получает список групп ТГ с разрешёнными пользователями
    """
    url = f"{PORTAL_BASE_URL}/allowed"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                return data.get("TelegramChats", {})
    except Exception as e:
        logger.error(f"Ошибка получения данных get_group_memberships_json: {e}")
        return {"message": f"Внутренняя ошибка сервера {e}"}

# - Функция, которая проверяет членство в группах раз в день
async def check_group_memberships():
    """
    Проверяет, должны ли пользователи находиться в группах, и выполняет действия:
        Если пользователь должен быть в группе, но отсутствует – отправляет ему сообщение с приглашением (Опционально)
        Если пользователь не должен находиться в группе, но присутствует – удаляет его
    """
    logger.info("Запущена плановая проверка членств в группах")
    allowed_data = await get_group_memberships_json()
    
    # for chat_id, allowed_users in allowed_data.items():
    #     for user_id in allowed_users:
    #         try:
    #             # Проверяем находится ли пользователь в группе
    #             member = await bot.get_chat_member(chat_id, user_id)
    #         except exceptions.TelegramBadRequest as e:
    #             # Если get_chat_member вызвал ошибку то пользователь отсутствует
    #             try:
    #                 now = int(time.time())
    #                 expire_timestamp = now + 86300  # ~24 часа
    #                 invite_link = get_cached_invite_link(chat_id)

    #                 if not invite_link:
    #                     invite_link_obj = await bot.create_chat_invite_link(
    #                         chat_id=chat_id,
    #                         name=f"Ссылка для {user_id}",
    #                         expire_date=expire_timestamp,
    #                         member_limit=0
    #                     )
    #                     invite_link = invite_link_obj.invite_link
    #                     cache_invite_link(chat_id, invite_link, expire_timestamp)

    #                 await bot.send_message(user_id, f"Вы должны быть участником. Пожалуйста, присоединяйтесь: {invite_link}")
    #                 logger.info(f"Приглашение отправлено пользователю {user_id} для группы {chat_id}")

    #             except Exception as inv_e:
    #                 logger.error(f"Ошибка отправки приглашения для пользователя {user_id} в группе {chat_id}: {inv_e}")

    #         except Exception as err:
    #                 logger.error(f"Ошибка проверки пользователя {user_id} в группе {chat_id}: {err}")
