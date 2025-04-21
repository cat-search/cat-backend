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
        collection_name: str = None,
):
    cat_state: CatState = request.app.state.cat
    collection_name = settings.weaviate_collection if collection_name is None else collection_name
    docs, vdb_latency = retrieve_docs('0', query_text, cat_state, collection_name)
    return docs


@logger.catch
@router.delete(
    "/vdb/collections/{name}",
    tags=['vdb'],
    summary="Delete collection",
    description=f"""
        Weaviate. Delete collection by name
        
        - Default collection: {settings.weaviate_collection}
    """,
)
async def delete_collection(
        request: Request,
        collection_name: str,
):
    wc: WeaviateClient = request.app.state.cat.wc
    wc.collections.delete(collection_name)
    return {'result': 'success'}


@logger.catch
@router.put(
    "/vdb/collections/{name}",
    tags=['vdb'],
    summary="Change collection",
    description="Weaviate. Change active collection",
)
async def set_collection(
        request: Request,
        collection_name: str,
):
    logger.info(msg := f"Setting active collection: {collection_name} ...")
    previous_collection: str = settings.weaviate_collection
    settings.weaviate_collection = collection_name

    result: dict = {
        'settings.weaviate_collection': settings.weaviate_collection,
        'previous_collection': previous_collection,
        'settings.weaviate_host': settings.weaviate_host,
        'settings.weaviate_port': settings.weaviate_port,
        'settings.weaviate_grpc_port': settings.weaviate_grpc_port,
    }
    logger.info(f"{msg} done")
    return result
