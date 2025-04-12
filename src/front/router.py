from datetime import datetime, UTC, timedelta
from urllib import response
from uuid import uuid4, UUID

from fastapi import Depends, APIRouter, BackgroundTasks
from loguru import logger
from starlette.requests import Request  # TODO: check type(request)


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
    request_timestamp: datetime = datetime.now(UTC)     # Time request received
    query_id: str = str(uuid4())                        # Request (query) unique id
    logger.info(f"User query: {query_id}: {query_text}, {request_timestamp}")

    # 2. Save query into db
    ...

    # 3. Embed query
    ...
    # Inside weaviate. No need to implement

    # 4. Query vectordb
    ...

    # 5. Rerank documents
    ...

    # 6. Query llm
    ...

    # 7. Response to user
    response_text: str = "Text of response"
    response_timestamp: datetime = datetime.now(UTC)
    duration: timedelta = response_timestamp - request_timestamp
    result = {
        "query_id"           : query_id,
        "query_text"         : query_text,
        "response_text"      : response_text,
        "duration"           : duration.total_seconds(),
        "request_timestamp"  : request_timestamp,
        "response_timestamp" : response_timestamp,
    }
    return result
