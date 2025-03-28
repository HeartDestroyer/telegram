# run.py

import asyncio
import signal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from aiohttp import web

from src.main import dp, bot, init_db_pool
from src.membership import check_group_memberships
from src.handlers import setup_all_handlers
from src.web import init_group_web_app
from src.mtproto_client import start_telethon

async def shutdown_bot(scheduler):
    logger.info("Останавливаем APScheduler")
    scheduler.shutdown(wait=False)
    logger.info("Останавливаем пулл aiogram")
    await dp.stop_polling()
    logger.info("Закрываем бот-сессию")
    await bot.session.close()
    logger.info("Бот успешно остановлен")

def handle_exit(loop, scheduler):
    """
    Функция вызываемая при получении сигнала
    Отменяет все активные задачи и планирует завершения бота
    """
    for task in asyncio.all_tasks(loop=loop):
        task.cancel()
    loop.create_task(shutdown_bot(scheduler))

async def main():
    await init_db_pool()

    setup_all_handlers(dp)

    await start_telethon()
    logger.info("Telethon клиент запущен")

    # Инициализируем планировщик
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_group_memberships, 'cron', hour='7', minute=0)
    scheduler.start()
    logger.info("Планировщик задач запущен")

    # Инициализируем веб-сервер
    web_app = init_group_web_app()
    web_runner = web.AppRunner(web_app)
    await web_runner.setup()
    web_site = web.TCPSite(web_runner, host="0.0.0.0", port=5041)
    await web_site.start()
    logger.info("Веб-сервер для групповых эндпоинтов запущен на порту 5041")

    await dp.start_polling(bot)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    scheduler = AsyncIOScheduler()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: handle_exit(loop, scheduler))

    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
