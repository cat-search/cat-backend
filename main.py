from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated
from asyncpg.pool import Pool

import httpx
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from sqlalchemy import create_engine
from starlette.requests import Request
from weaviate.client import WeaviateClient

from src.core.log import logger
from src.core.settings import settings
from src.front.router import router as front_router
from src.core.db import init_pool
from src.core.util import CatState
from src.vectordb.weaviate_vdb import init_weaviate, init_weaviate_async


tags_metadata = [
    {
        "name": "front",
        "description": "User queries and responses",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application launcher
    """
    # Shared application variables
    app.state.cat       = CatState()
    cat_state: CatState = app.state.cat
    cat_state.ht_client = httpx.AsyncClient(timeout=settings.request_timeout)
    cat_state.db_pool   = await init_pool()
    # cat_state.wc        = await init_weaviate_async()
    cat_state.wc        = init_weaviate()

    cat_state.llm_client = httpx.AsyncClient(
        base_url=settings.llm_base_url,  # настройки
        timeout=settings.llm_timeout,    # настройки
        headers={"Authorization": f"Bearer {settings.llm_api_key}"}  # Если нужно
    )
    
    FastAPICache.init(InMemoryBackend())

    yield

    # Application shutdown
    await cat_state.ht_client.aclose()
    await cat_state.db_pool.close()
    # await cat_state.wc.close()
    cat_state.wc.close()
    await cat_state.llm_client.aclose() #LLM-клиент закрывается

    await FastAPICache.clear()


app = FastAPI(
    lifespan=lifespan,
    title=settings.title,
    version=settings.app_version,
    openapi_tags=tags_metadata,
)
app.include_router(front_router)     # Front UI methods


@app.get('/health', include_in_schema=False)
def health_check():
    return HTMLResponse()


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
