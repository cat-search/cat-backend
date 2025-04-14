from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated
from asyncpg.pool import Pool

import httpx
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi_cache import FastAPICache
from fastapi_cache import caches, close_caches
from fastapi_cache.backends.redis import RedisCacheBackend
from sqlalchemy import create_engine
from starlette.requests import Request
from weaviate import Client

from src.core.log import logger
from src.core.settings import settings
from src.front.router import router as front_router
from src.core.db import init_pool
from src.core.util import CatState
from src.vectordb.weaviate_vdb import init_weaviate, init_weaviate_async

# привет
tags_metadata = [
    {
        "name": "front",
        "description": "User queries and responses",
    },
]



@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cat = CatState()
    cat_state: CatState = app.state.cat
    cat_state.ht_client = httpx.AsyncClient(timeout=settings.request_timeout)
    cat_state.db_pool = await init_pool()
    cat_state.wc = init_weaviate()

    
    redis_cache = RedisCacheBackend(settings.redis_url)
    await FastAPICache.init(redis_cache)

    yield

    await cat_state.ht_client.aclose()
    await cat_state.db_pool.close()
    cat_state.wc.close()
    await FastAPICache.clear()


app = FastAPI(
    lifespan=lifespan,
    title=settings.title,
    version=settings.app_version,
    openapi_tags=tags_metadata,
)
app.include_router(front_router)     # Front UI methods


@app.get('/health', include_in_schema=False)
async def health_check():
    checks = {
        "database": False,
        "weaviate": False,
        "redis": False,
    }

    # Проверка БД
    try:
        await app.state.cat.db_pool.fetch("SELECT 1")
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database healthcheck failed: {e}")

    # Проверка Weaviate
    try:
        app.state.cat.wc.is_ready()
        checks["weaviate"] = True
    except Exception as e:
        logger.error(f"Weaviate healthcheck failed: {e}")

    # Проверка Redis (если используется)
    try:
        await FastAPICache.get("health_test")  # Простой тестовый запрос
        checks["redis"] = True
    except Exception as e:
        logger.error(f"Redis healthcheck failed: {e}")

    if all(checks.values()):
        return HTMLResponse(status_code=status.HTTP_200_OK)
    else:
        return HTMLResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@app.get('/info', include_in_schema=False)
@app.api_route('/actuator/info', methods=['GET', 'OPTIONS'], include_in_schema=False)
def info_view():
    info_data = {
        "build":
            {
                "version": settings.app_version,
                "name": settings.app_name,
            }
    }
    return info_data
