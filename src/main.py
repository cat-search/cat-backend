from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from src.core.db import init_pool
from src.core.settings import settings
from src.core.util import CatState
from src.front.router import router as front_router
from src.llm.ollama_util import init_ollama_llm
from src.vectordb.router import router as vdb_router
from src.vectordb.weaviate_vdb import init_weaviate
from src.llm.router import router as llm_router


tags_metadata = [
    {
        "name": "front",
        "description": "User queries and responses",
    },
    {
        "name": "vdb",
        "description": "Vector DB",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application launcher
    """
    # Shared application variables
    app.state.cat        = CatState()
    cat_state: CatState  = app.state.cat
    cat_state.ht_client  = httpx.AsyncClient(timeout=settings.request_timeout)
    cat_state.db_pool    = await init_pool()
    # cat_state.wc         = await init_weaviate_async()
    cat_state.wc         = init_weaviate()
    cat_state.llm_client = init_ollama_llm()

    FastAPICache.init(InMemoryBackend())

    yield

    # Application shutdown
    await cat_state.ht_client.aclose()
    await cat_state.db_pool.close()
    # await cat_state.wc.close()
    cat_state.wc.close()
    await FastAPICache.clear()


app = FastAPI(
    lifespan=lifespan,
    title=settings.title,
    version=settings.app_version,
    openapi_tags=tags_metadata,
)
app.include_router(front_router)     # Front UI methods
app.include_router(vdb_router)       # Vector DB methods
app.include_router(llm_router)       # Vector DB methods


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
