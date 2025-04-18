from weaviate import WeaviateClient, WeaviateAsyncClient
from weaviate import connect_to_local as weaviate_connect_to_local
from weaviate.auth import AuthApiKey
from weaviate.classes.init import Auth
from weaviate.classes.query import MetadataQuery
from weaviate.collections.classes.internal import QueryReturn
from weaviate.collections.collection.sync import Collection as SyncCollection
from weaviate.config import AdditionalConfig
from weaviate.connect import ConnectionParams

from src.core.log import logger
from src.core.settings import settings
from src.core.util import measure_latency_async, CatState, measure_latency


def init_weaviate() -> WeaviateClient:
    """ Инициализация подключения """
    client: WeaviateClient = weaviate_connect_to_local(
        host=settings.weaviate_host,  # Use a string to specify the host
        port=settings.weaviate_port,
        auth_credentials=Auth.api_key(settings.weaviate_api_key),
        # additional_headers={"X-Ollama-Api-Key": "ollama"}
        skip_init_checks=True,
    )
    if not client.is_ready():
        logger.error(msg := f"Weaviate client initialization failed")
        raise AssertionError(msg)

    return client


async def init_weaviate_async() -> WeaviateAsyncClient:
    """ Инициализация подключения """
    client: WeaviateAsyncClient = WeaviateAsyncClient(
        connection_params=ConnectionParams.from_params(
            http_host=settings.weaviate_host,  # Use a string to specify the host
            http_port=settings.weaviate_port,
            http_secure=False,
            grpc_host=settings.weaviate_host,
            grpc_port=settings.weaviate_grpc_port,
            grpc_secure=False,
        ),
        auth_client_secret=AuthApiKey(settings.weaviate_api_key),
        # additional_headers={"X-Ollama-Api-Key": "ollama"}
        additional_config=AdditionalConfig(
            timeout=(10, 60),   # (connect timeout, read timeout)
        ),
        skip_init_checks=True,  # What's this???
    )
    await client.connect()
    # if not client.is_ready():
    #     logger.error(msg := f"Weaviate client initialization failed")
    #     raise AssertionError(msg)
    return client


@measure_latency
def retrieve_docs(
        query_id: str, query_text: str, cat_state: CatState
) -> QueryReturn:
    logger.info(msg := f"VectorDB retrieving: {query_id} ...")

    wc: WeaviateClient = cat_state.wc
    coll: SyncCollection = wc.collections.get(settings.weaviate_collection)
    result: QueryReturn = coll.query.near_text(
        query=query_text,
        limit=settings.weaviate_doc_limit,
        return_metadata=MetadataQuery(distance=True),
    )

    logger.info(f"{msg} done")
    return result


@measure_latency_async
async def retrieve_docs_async(
        query_id: str, query_text: str, cat_state: CatState
) -> list[dict]:
    logger.info(msg := f"VectorDB retrieving: {query_id} ...")

    wc: WeaviateAsyncClient = cat_state.wc

    coll = wc.collections.get(settings.vdb_type)
    # result = await coll.query.near_text(
    #     query=query_text,
    #     limit=settings.vdb_doc_limit,
    #     return_metadata=MetadataQuery(distance=True),
    # )
    # result = await wc.client.get(
    #     class_name=settings.vdb_name,
    #     properties=["context", 'name'],
    # ).with_near_text(
    #     near_text=NearText(
    #         concepts=[query_text],
    #         distance=0.7
    #     ),
    # ).with_limit(settings.vdb_doc_limit).do()

    logger.info(f"{msg} done")
    return result
