# src/mtproto_client.py

import os
import time
from loguru import logger
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, InputPeerChannel, InputUser, PeerUser, ChannelParticipantsSearch

from .config import TELEGRAM_API_ID, TELEGRAM_API_HASH

# Файл для хранения строки сессии
SESSION_FILE = 'bot_mtproto.session'

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except UnicodeDecodeError as e:
            logger.error(f"Ошибка декодирования сессии: {e}. Файл, возможно, поврежден. Удаляем его и создаем новый")
            os.remove(SESSION_FILE)
            return ""
    return ""

def save_session(session_str):
    with open(SESSION_FILE, 'w') as f:
        f.write(session_str)

# Инициализируем Telethon клиент
session_str = load_session()
telethon_client = TelegramClient(StringSession(session_str), TELEGRAM_API_ID, TELEGRAM_API_HASH)

# + Запускает Telethon клиент
async def start_telethon():
    await telethon_client.start()
    new_session = telethon_client.session.save()
    save_session(new_session)
    dialogs = await telethon_client.get_dialogs()
    logger.info(f"Получено {len(dialogs)} диалогов")

# + Получаем всех участников канала
async def get_all_participants(channel):
    participants = await telethon_client.get_participants(channel, filter=ChannelParticipantsSearch(''), limit=0)
    return participants

# + Использует MTProto API для удаления пользователя из чата
async def mtproto_remove_user(chat_id: int, user_id: int):
    """
    Использует MTProto API (channels.editBanned) для удаления пользователя из чата
    
    :param chat_id: Идентификатор чата (целое число)
    :param user_id: Telegram ID пользователя (целое число)
    :return: Результат запроса EditBannedRequest
    """
    # Получаем сущность чата и пользователя
    channel_entity = await telethon_client.get_entity(chat_id)
    logger.info(channel_entity)
    participants = await get_all_participants(channel_entity)
    for user in participants:
        logger.info(user.id, user.first_name, user.username)

    try:
        user_entity = await telethon_client.get_entity(PeerUser(user_id))
        logger.info(user_entity)
    except Exception as e:
        logger.error(f"Ошибка получения сущности для пользователя {user_id}: {e}")
        try:
            user_entity = await telethon_client.get_entity(user_id)
        except Exception as inner_e:
            logger.error(f"Не удалось получить сущность для пользователя {user_id}: {inner_e}")
            raise inner_e
    
    input_channel = InputPeerChannel(channel_id=channel_entity.id, access_hash=channel_entity.access_hash)
    input_user = InputUser(user_id=user_entity.id, access_hash=user_entity.access_hash)

    
    ban_duration = 2 * 24 * 3600
    until_date = int(time.time()) + ban_duration

    # Определяем правила бана
    banned_rights = ChatBannedRights(
        until_date=until_date,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True
    )
    
    result = await telethon_client(EditBannedRequest(
        channel=input_channel,
        participant=input_user,
        banned_rights=banned_rights
    ))

    return result
