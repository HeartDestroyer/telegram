# src/handlers/cleaner.py

from aiogram import Router, F
from aiogram.types import Message, ContentType
from loguru import logger
from src.main import bot

router = Router()

@router.message(F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def delete_add_message(message: Message):
    logger.info(f"Новый пользователь(и) присоединились к каналу {message.new_chat_members}")
    me = await bot.get_me()
    if all(member.id != me.id for member in message.new_chat_members):
        logger.info(f"Удалили системное сообщение о присоединении участника")
        try:
            await bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            logger.error(f"Ошибка при удалении системного сообщения о присоединении: {e}")

@router.message(F.content_type == ContentType.LEFT_CHAT_MEMBER)
async def delete_leave_message(message: Message):
    me = await bot.get_me()
    if message.left_chat_member.id != me.id:
        try:
            await bot.delete_message(message.chat.id, message.message_id)
            logger.info(f"Удалили системное сообщение о выходе участника {message.left_chat_member.id}")
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения о выходе: {e}")

@router.message(F.content_type.in_({
    ContentType.NEW_CHAT_TITLE,
    ContentType.NEW_CHAT_PHOTO,
    ContentType.DELETE_CHAT_PHOTO
}))
async def delete_group_change_message(message: Message):
    """
    Удаляем сообщения об изменении названия группы, фото и тд
    """
    try:
        await bot.delete_message(message.chat.id, message.message_id)
        if message.new_chat_title:
            logger.info(f"Удалили сообщение об изменении названия группы: {message.new_chat_title}")
        elif message.new_chat_photo:
            logger.info("Удалили сообщение об изменении фото группы")
        elif message.delete_chat_photo:
            logger.info("Удалили сообщение об удалении фото группы")
    except Exception as e:
        logger.error(f"Ошибка при удалении системного сообщения: {e}")

@router.message(F.content_type.in_({
    ContentType.FORUM_TOPIC_CREATED,
    ContentType.FORUM_TOPIC_CLOSED,
    ContentType.FORUM_TOPIC_REOPENED,
    ContentType.FORUM_TOPIC_EDITED,
    ContentType.GENERAL_FORUM_TOPIC_HIDDEN,
    ContentType.GENERAL_FORUM_TOPIC_UNHIDDEN
}))
async def handle_forum_events(message: Message):
    """
    Удаляем системные сообщения о событиях в форуме
    """
    try:
        await bot.delete_message(message.chat.id, message.message_id)
        logger.info(f"Удалено системное форумное событие: {message.content_type}")
    except Exception as e:
        logger.error(f"Ошибка при удалении форумного события: {e}")
