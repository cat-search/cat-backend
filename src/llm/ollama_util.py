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
    # 'type':       'file',
    # 'updated_at': datetime.datetime(2025, 3, 28, 11, 7, 48, 983443, tzinfo=datetime.timezone.utc),
    # 'name':       '02_Великие_музеи_мира_Прадо_Мадрид_2011.pdf',
    # 'site_name':  'Музеи',
    # 'size':       173441090,
    # 'link':       'https://hackaton.hb.ru-msk.vkcloud-storage...
    # context = "\n\n".join(
    #     doc.properties.get('content')
    #     for doc in docs.objects
    # )
    context = "\n\n".join(
        f"{{site_name}}: {doc.properties.get('site_name')}, "
        f"{{doc_type}}: {doc.properties.get('type')}, "
        f"{{doc_name}}: {doc.properties.get('name')}, "
        f"{{doc_size}}: {doc.properties.get('size')}, "
        f"{{doc_url}}: {doc.properties.get('link')}, "
        f"\n{doc.properties.get('content')}"
        for doc in docs.objects
    )
    # context = "\n\n".join(
    #     f"Сайт: {doc.properties.get('site_name')}, "
    #     f"Тип документа: {doc.properties.get('type')}, "
    #     f"Название документа: {doc.properties.get('name')}, "
    #     f"Размер_документа_в_байтах: {doc.properties.get('size')}, "
    #     f"Ссылка_на_документ: {doc.properties.get('link')}, "
    #     f"\n{doc.properties.get('content')}"
    #     for doc in docs.objects
    # )
    logger.info(f"Context size: {len(context)}, from {len(docs.objects)} docs")
    llm_prompt: str = settings.llm_prompt_template.format(
        context=context,
        question=query_text,
    )
    logger.info(f"LLM prompt size: {len(llm_prompt)}")

    # 2. Запрос к LLM
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
