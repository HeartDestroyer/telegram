# src/main.py

import sys
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from .config import BOT_TOKEN
from .db import init_pool

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", encoding="utf-8")
logger.add(sys.stdout, format="{time} {level} {message}", level="DEBUG")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=MemoryStorage())

logger.info("Бот и диспетчер инициализированы")

async def init_db_pool():
    await init_pool()
