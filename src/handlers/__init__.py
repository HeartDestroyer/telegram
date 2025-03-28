# src/handlers/__init__.py

from aiogram import Dispatcher

from .start import router as start_router
from .portal import router as portal_router
from .group import router as group_router
from .cleaner import router as cleaner_router
from .log import router as log_router

# Функция регистрации всех роутеров
def setup_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(portal_router)
    dp.include_router(group_router)
    dp.include_router(cleaner_router)
    dp.include_router(log_router)
