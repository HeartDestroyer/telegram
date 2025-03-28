# src/handlers/group.py

from aiogram import Router, F
from aiogram.types import Message, ContentType, ChatJoinRequest
from loguru import logger

from src.membership import check_user_allowed
from src.main import bot
from src.config import CONTROLLED_CHAT_IDS

router = Router()

# + Проверка разрешения при входе в группу
@router.chat_join_request()
async def handle_join_request(join_request: ChatJoinRequest):
    chat_id = join_request.chat.id
    if chat_id not in CONTROLLED_CHAT_IDS:
        return
    
    user_id = join_request.from_user.id

    allowed = await check_user_allowed(chat_id, user_id)
    logger.info(f"Запрос на вступление от пользователя {user_id} в чат {chat_id}. Статус={allowed}")

    if allowed:
        try:
            await bot.approve_chat_join_request(chat_id, user_id)
            logger.info(f"Запрос на вступление от {user_id} одобрен")
        except Exception as e:
            logger.error(f"Ошибка при одобрении запроса: {e}")
    else:
        try:
            await bot.decline_chat_join_request(chat_id, user_id)
            logger.info(f"Запрос на вступление от {user_id} отклонён")
        except Exception as e:
            logger.error(f"Ошибка при отклонении запроса: {e}")

# + Проверка разрешения при входе в группу
@router.message(F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def new_member_handler(message: Message):
    chat_id = message.chat.id
    if chat_id not in CONTROLLED_CHAT_IDS:
        return
    
    for new_member in message.new_chat_members:
        user_id = new_member.id
        allowed = await check_user_allowed(chat_id, user_id)
        logger.info(f"Новый участник {user_id} в чате {chat_id}. Статус={allowed}")

        if not allowed:
            try:
                await bot.ban_chat_member(chat_id, user_id)
                await bot.unban_chat_member(chat_id, user_id)
                logger.info(f"Неразрешённый пользователь {user_id} удалён из чата {chat_id}")
            except Exception as e:
                logger.error(f"Ошибка при удалении пользователя {user_id} из {chat_id}: {e}")
        else:
            logger.info(f"Пользователь {user_id} допущен в чат {chat_id}")
