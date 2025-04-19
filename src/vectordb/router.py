from fastapi import APIRouter
from starlette.requests import Request
from weaviate import WeaviateClient

from src.core.log import logger
from src.core.settings import settings
from src.core.util import CatState
from src.vectordb.weaviate_vdb import retrieve_docs

router = APIRouter()


@logger.catch
@router.get(
    "/vdb/collections",
    tags=['vdb'],
    summary="List collections",
    description="Weaviate. List collection names",
)
async def get_collections(
        request: Request,
):
    wc: WeaviateClient = request.app.state.cat.wc
    result: dict = wc.collections.list_all()
    result: list = [k for k in result]
    return result


@logger.catch
@router.get(
    "/vdb/collections/{name}",
    tags=['vdb'],
    summary="Get collection by name",
    description="Weaviate. Get collection config by name",
)
async def get_collections(
        request: Request,
        name: str,
):
    wc: WeaviateClient = request.app.state.cat.wc
    coll = wc.collections.get(name)
    result = coll.config.get(simple=False)
    return result


@logger.catch
@router.get(
    "/vdb/collections_full",
    tags=['vdb'],
    summary="List collections",
    description="Weaviate. List collections with full config",
)
async def get_collections_full(
        request: Request,
):
    wc: WeaviateClient = request.app.state.cat.wc
    result = wc.collections.list_all()
    return result


@logger.catch
@router.get(
    "/vdb/collections/{name}/count",
    tags=['vdb'],
    summary="Count documents",
    description="Weaviate. Count documents in collection",
)
async def get_collection_count(
        request: Request,
        name: str,
):
    wc: WeaviateClient = request.app.state.cat.wc
    coll = wc.collections.get(name)
    result = coll.aggregate.over_all(total_count=True)
    return result


@logger.catch
@router.get(
    "/vdb/docs",
    tags=['vdb'],
    summary="Get documents",
    description=f"""
        Weaviate. Retrieve documents by query from collection
        
        - Default collection: {settings.weaviate_collection}
    """,
)
async def get_docs(
        request: Request,
        query_text: str,
        collection_name: str,
):
    cat_state: CatState = request.app.state.cat
    docs, vdb_latency = retrieve_docs('0', query_text, cat_state, collection_name)
    return docs
