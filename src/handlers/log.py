# src/handlers/log.py

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from loguru import logger

router = Router()

# + Обработчик команды /logging — вывод последних 30 строк debug.log
@router.message(Command("logging"))
async def log_handler(message: Message):
    log_file = "/var/www/TelegramBot/debug.log"
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        last_lines = lines[-30:]
        result = "".join(last_lines)
        await message.answer(f"```{result}```", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка при чтении файла лога: {e}")
        await message.answer(f"Ошибка при чтении файла лога: {e}")
