import asyncpg

from src.core.settings import settings


async def init_pool():
    pool: asyncpg.Pool = await asyncpg.create_pool(
        settings.db_conn_str, min_size=1
    )
    return pool
