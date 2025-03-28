# src/web.py
# TODO mtproto_remove_user Не удаляет с каналов

import aiohttp
from aiohttp import web
from loguru import logger

from src.main import bot
from src.mtproto_client import mtproto_remove_user

def init_group_web_app():
    """
    Создает и возвращает экземпляр aiohttp-приложения с маршрутом
    """
    app = web.Application()
    app.router.add_post("/group/delete", delete_user_from_controlled_chats)
    return app

# + HTTP-эндпоинт для удаления пользователя из контролируемых чатов
async def delete_user_from_controlled_chats(request: web.Request):
    """
    HTTP-эндпоинт, который принимает POST-запрос по пути /group/delete/{user_id}
    """
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Aiohttp-приложения: Ошибка чтения JSON: {e}")
        return web.json_response({"message": "Неверный формат JSON от HR-портала"}, status=400)

    user_channels_delete = data.get("user_channels_delete")
    if not user_channels_delete:
        return web.json_response({"message": "Нет каналов для удаления пользователя"}, status=400)
    
    # Обрабатываем каждый ключ в словаре (обычно один пользователь)
    for user_id, chat_ids in user_channels_delete.items():
        try:
            telegram_id = int(user_id)
        except Exception as e:
            logger.error(f"Некорректный телеграм ID: {telegram_id} - {e}")
            continue

        for chat_id in chat_ids:
            try:
                # TODO Не удаляет с каналов
                # await mtproto_remove_user(chat_id, telegram_id) 
                await bot.ban_chat_member(chat_id, telegram_id)
                await bot.unban_chat_member(chat_id, telegram_id)
                logger.info(f"Пользователь {telegram_id} удалён из чата {chat_id}")
            except Exception as e:
                logger.error(f"Ошибка при удалении пользователя {telegram_id} из чата {chat_id}: {e}")

    return web.json_response({"message": "Пользователь удалён из указанных чатов"}, status=200)
