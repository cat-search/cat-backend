from langchain_ollama import OllamaLLM
from weaviate.collections.classes.internal import QueryReturn, Object

from src.core.log import logger
from src.core.util import CatState, measure_latency
from src.core.settings import settings


def init_ollama_llm() -> OllamaLLM:
    llm_client: OllamaLLM = OllamaLLM(
        base_url=settings.llm_url,
        model=settings.llm_model,
        # If we'll need more arguments, add arguments into settings. See line above.
    )
    return llm_client


@measure_latency
def llm_make_query(
        query_id: str, query_text: str, docs: QueryReturn, cat_state: CatState,
) -> str:
    """
    Makes query to Ollama LLM

    - 1. Prepare context
    - 2. Query ollama
    """
    logger.info(msg := f"Querying LLM: {query_id} ...")

    # 1. Подготовка контекста для LLM
    doc: Object
    context = "\n\n".join(
        doc.properties.get('content')
        for doc in docs.objects
    )
    logger.info(f"Context size: {len(context)}, from {len(docs.objects)} docs")
    llm_prompt: str = settings.llm_prompt_template.format(
        context=context,
        question=query_text,
    )
    logger.info(f"LLM prompt size: {len(llm_prompt)}")

    # 2. Запрос к LLM (с таймаутом)
    try:
        llm_client: OllamaLLM = cat_state.llm_client
        llm_response: str = llm_client.invoke(llm_prompt)
    except Exception as e:
        logger.error(f"LLM query failed: {str(e)}")
        llm_response = f"error: LLM query failed: {e}"

    logger.info(f"{msg} done")
    # llm_response = await asyncio.wait_for(
    #     cat_state.llm_client.generate(llm_prompt),
    #     timeout=30.0
    # )
    # llm_response: LLMResult = cat_state.llm_client.generate([llm_prompt])
    return llm_response
