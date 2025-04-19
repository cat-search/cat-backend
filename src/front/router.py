from datetime import datetime, UTC, timedelta
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks
from starlette.requests import Request
from weaviate.collections.classes.internal import QueryReturn

from src.core.db import (
    register_query,
)
from src.core.log import logger
from src.core.util import CatState
from src.llm.ollama_util import llm_make_query
from src.vectordb.weaviate_vdb import retrieve_docs

router = APIRouter()


@logger.catch
@router.get(
    "/front/query",
    tags=['front'],
    summary="Пользовательский запрос",
    description="""Направить поисковый запрос""",
)
async def user_query(
        request: Request,
        background_tasks: BackgroundTasks,
        query_text: str,
):
    """
    Response for user query:

    - 1. Log
    - 2. Save query into db
    - 3. Embed query
    - 4. Query vectordb
    - 5. Rerank documents
    - 6. Query llm
    - 7. Response to user

    Args:
        request:            Received request object
        background_tasks:   Background tasks fixture object
        query_text:         Text query

    Returns:
        Search response to user query (query_text)
    """
    # 1. Log
    query_timestamp: datetime = datetime.now(UTC)     # Time request received
    query_id: str = str(uuid4())                        # Request (query) unique id
    logger.info(f"User query: {query_id}: {query_text}, {query_timestamp}")
    result: dict = {
        "query_id": query_id,
        "query_text": query_text,
        "timestamp": query_timestamp,
    }
    # cat_state: Our shared vars
    cat_state: CatState = request.app.state.cat

    # 2. Save query into db
    background_tasks.add_task(register_query, params=result, cat_state=cat_state)

    # 3. Embed query (Inside weaviate. No need to implement)
    # 4. Query vectordb
    # docs, vdb_latency = await retrieve_docs_async(query_id, query_text, cat_state)
    docs: QueryReturn
    vdb_latency: float
    docs, vdb_latency = retrieve_docs(query_id, query_text, cat_state)
    result.update({"vectordb_doc_count": len(docs.objects)})
    # result.update({"docs": docs})
    # params = {'query_id': query_id, 'status': Status.vdb_done, 'vdb_latency': vdb_latency}
    # background_tasks.add_task(
    #     update_query_detail, params=params, cat_state=cat_state,
    # )
    ...

    # 5. Rerank documents
    ...

    # 6. Query llm
    llm_response: str
    llm_latency: float
    llm_response, llm_latency = llm_make_query(query_id, query_text, docs, cat_state)
    logger.info(f"LLM latency: {llm_latency}")

    # 7. Response to user
    response_timestamp: datetime = datetime.now(UTC)
    latency: timedelta = response_timestamp - query_timestamp
    result.update(
        {
            "vdb_latency"        : vdb_latency,
            "llm_latency"        : llm_latency,
            "latency"            : latency.total_seconds(),
            "response_text"      : llm_response,
        }
    )
    return result
