import asyncio
from datetime import datetime, UTC, timedelta
from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, Request, Depends, HTTPException
from fastapi_cache.decorator import cache
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
from pydantic import BaseModel, constr

from src.core.db import register_query, update_query_detail
from src.core.util import CatState
from src.models.cat_public import Status
from src.vectordb.weaviate_vdb import retrieve_docs

router = APIRouter()

# --- Pydantic модели для валидации ---
class QueryRequest(BaseModel):
    query_text: constr(min_length=3, max_length=500)

# --- Настройки retry ---
RETRY_SETTINGS = {
    "stop": stop_after_attempt(3),
    "wait": wait_exponential(multiplier=1, min=2, max=10),
    "before_sleep": lambda _: logger.warning("Retrying after error..."),
}

# --- Асинхронный pipeline ---
@retry(**RETRY_SETTINGS)
@cache(expire=300)
@router.get(
    "/front/query",
    tags=['front'],
    summary="Пользовательский запрос",
    responses={
        200: {"description": "Успешный ответ"},
        500: {"description": "Ошибка сервера"},
        429: {"description": "Слишком много запросов"}
    }
)
async def user_query(
    request: Request,
    background_tasks: BackgroundTasks,
    query: QueryRequest = Depends(),
):
    """Обработчик запроса с RAG-конвейером (Weaviate + LLM)."""
    # 1. Инициализация
    query_id = str(uuid4())
    query_timestamp = datetime.now(UTC)
    cat_state: CatState = request.app.state.cat

    logger.info(f"Начало обработки запроса {query_id}: {query.query_text[:50]}...")

    # 2. Параллельные задачи: Weaviate + логирование в БД
    try:
        # Создаём задачу для поиска документов в Weaviate (не блокируя основной поток)
        weaviate_task = asyncio.create_task(
        retrieve_docs(query_id, query.query_text, cat_state)  # Функция должна быть async!
        )
        db_task = asyncio.create_task(
        register_query({  # Функция должна быть async!
         "query_id": query_id,
        "query_text": query.query_text,
        "timestamp": query_timestamp
         }, cat_state)
        )
        # Ожидаем завершения ОБЕИХ задач (но они работают конкурентно)
        docs, vdb_latency = await weaviate_task
        await db_task  # Если результат не нужен, можно просто "отпустить" задачу


        
        # 3. Подготовка контекста для LLM
        context = "\n\n".join(doc.get("text", "")[:2000] for doc in docs[:3])
        llm_prompt = f"""
        Вопрос: {query.query_text}
        Контекст: {context}
        """

        # 4. Запрос к LLM (с таймаутом)
        llm_response = await asyncio.wait_for(
            cat_state.llm_client.generate(llm_prompt),
            timeout=30.0
        )
        logger.success(f"LLM ответ сгенерирован для {query_id}")

        # 5. Фоновое обновление статуса в БД
        background_tasks.add_task(
            update_query_detail,
            params={
                'query_id': query_id,
                'status': Status.llm_done,
                'vdb_latency': vdb_latency,
                'llm_response': llm_response
            },
            cat_state=cat_state
        )

        # 6. Формирование ответа
        latency = (datetime.now(UTC) - query_timestamp).total_seconds()
        logger.info(f"Запрос {query_id} выполнен за {latency:.2f} сек")

        return {
            "query_id": query_id,
            "response_text": llm_response,
            "latency": latency,
            "docs_used": len(docs)
        }

    except asyncio.TimeoutError:
        logger.error(f"Таймаут LLM для запроса {query_id}")
        raise HTTPException(504, "LLM timeout")
    except Exception as e:
        logger.critical(f"Ошибка в запросе {query_id}: {str(e)}")
        raise HTTPException(500, "Internal Server Error")


