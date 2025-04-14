import asyncpg
from sqlalchemy import insert, update
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import bindparam
from sqlalchemy.types import Interval

from src.core.log import logger
from src.core.settings import settings
from src.core.util import CatState
from src.models.cat_public import QueryStatus, QueryDetail, Status


async def init_pool():
    pool: asyncpg.Pool = await asyncpg.create_pool(
        settings.db_conn_str, min_size=1
    )
    return pool


def compile_query(stmt) -> str:
    result = stmt.compile(
        dialect=postgresql.dialect(),
        compile_kwargs={"literal_binds": True},
    ).string
    return result


async def register_query(params: dict, cat_state: CatState, **kwargs):
    """
    Register query in DB
    """
    # params = kwargs.get('params')
    # cat_state: CatState = kwargs.get('request').app.state.cat
    pool: asyncpg.Pool = cat_state.db_pool
    stmt = insert(QueryStatus).values(
        query_id=params.get('query_id'),
        status=Status.new,
        timestamp=params.get('timestamp'),
    )
    res = await pool.execute(compile_query(stmt))
    logger.debug(f"Registered query: {res}")


async def update_query_status():
    pass


async def get_query_status():
    pass


async def update_query_detail(**kwargs):
    params: dict = kwargs.get('params')
    cat_state: CatState = kwargs.get('request').app.state.cat
    pool: asyncpg.Pool = cat_state.db_pool
    stmt = update(QueryDetail).where(
        QueryDetail.query_id == params.get('query_id')
    ).values(
        # TODO: I'm here. It's failing with an error:
        #  sqlalchemy.exc.CompileError: Unconsumed column names: status
        status=params.get('status'),
        vdb=settings.vdb_type,
        vdb_index=settings.vdb_index,
        vdb_latency=bindparam("vdb_latency", type_=Interval),
    )
    # res = await pool.execute(compile_query(stmt))
    # logger.debug(f"Update result: {res}")
