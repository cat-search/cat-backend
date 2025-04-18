from fastapi import APIRouter
from starlette.requests import Request
from weaviate import WeaviateClient

from src.core.log import logger

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
