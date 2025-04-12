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
from src.core.log import logger
from src.core.settings import settings
from src.front.router import router as front_router
from src.core.db import init_pool


tags_metadata = [
    {
        "name": "front",
        "description": "User queries and responses",
    },
]


# Shared application variables class
@dataclass
class CatState:
    db_pool:   Pool = None                 # DB connection pool
    ht_client: httpx.AsyncClient = None    # Http client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application launcher
    """
    # Shared application variables
    app.state.cat        = CatState()
    app.state.cat.ht_client = httpx.AsyncClient(timeout=settings.request_timeout)
    app.state.cat.db_pool   = await init_pool()

    FastAPICache.init(InMemoryBackend())

    yield

    # Application shutdown
    await app.state.cat.ht_client.aclose()
    await app.state.cat.db_pool.close()
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
