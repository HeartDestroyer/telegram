# src/handlers/portal.py

import time
import aiohttp
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from src.config import PORTAL_BASE_URL
from src.main import bot

router = Router()

# Состояния для ввода логина
class PortalState(StatesGroup):
    waiting_for_login = State()

# + Обработчик команды /portal — просим у пользователя ввести логин
@router.message(Command("portal"))
async def portal_cmd(message: types.Message, state: FSMContext):
    await message.answer("Введите ваш логин на HR-портале:")
    await state.set_state(PortalState.waiting_for_login)

@router.message(PortalState.waiting_for_login)
async def process_portal_login(message: types.Message, state: FSMContext):
    """
    Обрабатывает введённый логин:
        Вызывает API портала для авторизации (login)
        Если авторизация успешна – получает данные пользователя (каналы) через API
        Генерирует ссылки приглашения для каждого канала и отправляет пользователю
    """
    logger.info(f"Получен логин от пользователя {message.from_user.id}: {message.text}")
    login = message.text.strip()
    telegram_id = str(message.from_user.id)

    login_url = f"{PORTAL_BASE_URL}/login"
    params = {"login": login, "telegramID": telegram_id}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(login_url, params=params, timeout=10) as response:
                login_data = await response.json()
                status_code = response.status
    except Exception as e:
        await message.answer(f"Ошибка подключения к HR-порталу: {e}")
        await state.clear()
        return
    
    # Если авторизация прошла
    if status_code in (200, 201):
        await message.answer(f"Авторизация для логина «{login}» прошла успешно")

        # Запрашиваем список каналов
        channels_url = f"{PORTAL_BASE_URL}/employees"
        params = {"telegramID": telegram_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(channels_url, params=params, timeout=10) as response:
                    channels_data = await response.json()
                    channels_status = response.status
        except Exception as e:
            await message.answer(f"Ошибка получения данных каналов: {e}")
            await state.clear()
            return
        
        if channels_status == 200:
            channels = channels_data.get("Information")
            if channels:
                
                for channel in channels:
                    channel_id = channel["channel_id"]
                    channel_name = channel["channel_name"]
                    channel_url = channel["channel_url"]

                    if channel_url:
                        await message.answer(f"Приглашение в канал «{channel_name}»:\n{channel_url}")
            else:
                await message.answer("Нет доступных каналов для приглашения")
        else:
            await message.answer(channels_data.get("message", "Ошибка получения каналов"))
    else:
        error_msg = login_data.get("message", "Ошибка авторизации - попробуйте снова")
        await message.answer(error_msg)
        await message.answer("Введите ваш логин на HR-портале:")
        return

    await state.clear()
