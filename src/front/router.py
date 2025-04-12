from datetime import datetime, UTC, timedelta
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks
from loguru import logger
from starlette.requests import Request  # TODO: check type(request)

from src.core.db import (
    register_query,
    update_query_detail,
)
from src.models.cat_public import Status
from src.vectordb.weaviate import retrieve_docs

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
    # 1. Log
    query_timestamp: datetime = datetime.now(UTC)     # Time request received
    query_id: str = str(uuid4())                        # Request (query) unique id
    logger.info(f"User query: {query_id}: {query_text}, {query_timestamp}")
    result: dict = {
        "query_id": query_id,
        "query_text": query_text,
        "timestamp": query_timestamp,
    }

    # 2. Save query into db
    background_tasks.add_task(register_query, params=result, request=request)

    # 3. Embed query
    ...
    # Inside weaviate. No need to implement

    # 4. Query vectordb
    docs, vdb_latency = await retrieve_docs(query_id)
    params = {'query_id': query_id, 'status': Status.vdb_done, 'vdb_latency': vdb_latency}
    background_tasks.add_task(
        update_query_detail, params=params, request=request
    )
    ...

    # 5. Rerank documents
    ...

    # 6. Query llm
    ...

    # 7. Response to user
    response_text: str = "Text of response"
    response_timestamp: datetime = datetime.now(UTC)
    latency: timedelta = response_timestamp - query_timestamp
    result.update(
        {
            "response_text"      : response_text,
            "latency"            : latency.total_seconds(),
        }
    )
    return result
