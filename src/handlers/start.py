# src/handlers/start.py

import os
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject
from loguru import logger
from aiogram import types
from aiomysql import OperationalError
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext

from src.db import get_pool
from src.main import bot
from src.handlers.portal import PortalState

router = Router()

# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.full_name} запустил бота")
    logger.info(f"command.args: {command.args}")

    args_text = command.args or ""
    args_list = args_text.split()
    utm = args_list[0] if args_list else 'tg_bot'

    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    await save_user_to_db(full_name, user_id, username, utm)

    # Если пользователь запустил /start portal
    if args_list and args_list[0] == "portal":
        await message.answer("Введите ваш логин на HR-портале:")
        await state.set_state(PortalState.waiting_for_login)
        return
    
    welcome_text = (
        f'Здравствуйте, {message.from_user.full_name}\n'
        'Рады приветствовать вас в нашем телеграм-боте.\n\n'
        'Мы ежедневно публикуем актуальные контракты госзаказчиков, корпораций и крупных компаний по вашей нише у себя в папке Телеграм:\n\n'
        '🔸 Удобная навигация ↕️\n'
        '🔸 Разделение по сферам деятельности и регионам России\n'
        '🔸 Настройка чатов за пару кликов 💬\n\n'
        'Получайте уведомления только по интересующей нише.\n\n'
        '➕Присоединяйтесь!\n\n'
        'Забирайте лучшие тендеры и зарабатывайте больше!\n'
        'https://t.me/addlist/Y4BKGeudpldlMTQy'
    )

    video_path = os.path.join(os.path.dirname(__file__), "video", "hi.mp4")
    try:
        video_input = FSInputFile(path=video_path)
        await bot.send_video(
            message.chat.id,
            video=video_input,
            caption=welcome_text,
            reply_markup=main_menu()
        )
    except Exception as e:
        logger.error(f"Ошибка отправки видео: {e}")
        # Если видео не получилось отправить — отправим просто текст
        await message.answer(welcome_text, reply_markup=main_menu())

# Асинхронное сохранение пользователя в БД
async def save_user_to_db(full_name, user_id, username, utm):
    sql = '''
        INSERT INTO telegram_bot (full_name, id_user, username, url, utm)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            full_name = VALUES(full_name),
            username = VALUES(username)
    '''
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(sql, (full_name, user_id, username or "", None, utm))
            except OperationalError as ex:
                logger.error(f"Ошибка БД при сохранении пользователя {username}: {ex}")
            except Exception as ex:
                logger.error(f"Ошибка при сохранении пользователя {username}: {ex}")

# Создаём инлайн-клавиатуру с кнопками
def main_menu() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Сайт компании",
            url="https://expertcentre.org?utm_source=tg_bot"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="Актуальные контракты",
            url="https://t.me/addlist/Y4BKGeudpldlMTQy"
        )
    )
    builder.adjust(1)
    return builder.as_markup()
