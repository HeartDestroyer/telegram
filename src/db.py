# src/db.py

import aiomysql
from loguru import logger

from .config import DB_PASSWORD, DB_NAME, IP

pool = None

async def init_pool():
    global pool
    if pool is None:
        logger.info("Инициализация пула соединений")
        pool = await aiomysql.create_pool(host=IP, user=DB_NAME, password=DB_PASSWORD, db=DB_NAME, minsize=1, maxsize=5, autocommit=True)
    return pool

async def get_pool():
    global pool
    if pool is None:
        await init_pool()
    return pool

async def close_pool():
    global pool
    if pool:
        logger.info("Закрытие пула соединений")
        pool.close()
        await pool.wait_closed()
        pool = None
