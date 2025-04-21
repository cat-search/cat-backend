from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str        = 'cat-backend'
    app_version: str     = '0.0.0'
    title: str           = 'CatSearch API backend'
    log_level: str       = 'INFO'

    db_conn_str: str     = 'postgresql://postgres:Oue$8AriEOdN@pg:5432/catsearch'
    alembic_db_name: str = 'catbackend'

    request_timeout: int = 30

    vdb_type: str        = 'weaviate'

    # Vector DB. weaviate
    weaviate_host: str                  = "weaviate"
    weaviate_port: int                  = 8080
    weaviate_grpc_port: int             = 50051
    weaviate_api_key: str               = "Search_the_VK"
    weaviate_collection: str            = "catsearch"
    weaviate_api_endpoint: str          = "http://ollama:11434"
    # Model name. If it's `None`, uses the server-defined default
    weaviate_doc_limit: int             = 6

    llm_url: str                        = "http://ollama:11434"
    llm_model: str                      = "llama3"
    llm_temperature: float              = 0.3
    llm_top_p: float                    = 0.9
    llm_top_k: float                    = 40
    llm_num_ctx: float                  = 8192  # 8K context
    llm_repeat_penalty: float           = 1.15
    # 'updated_at': datetime.datetime(2025, 3, 28, 11, 7, 48, 983443, tzinfo=datetime.timezone.utc),
    # 'name': '02_Великие_музеи_мира_Прадо_Мадрид_2011.pdf',
    # 'site_name': 'Музеи',
    # 'size': 173441090,
    # 'link': 'https://hackaton.hb.ru-msk.vkcloud-storage
    llm_prompt_template: str = (
        """Вы — эксперт‑ассистент. На основании нижеприведённого контекста ответьте на вопрос:
        {question}
        
        Контекст:
        {context}
        
        Формат ответа:
        - Кратко, по пунктам.
        - Каждый пункт должен быть в Markdown‑буллете.
        Название_сайта
        - В конце каждого пункта добавьте ссылку на источник 
          в формате [сайт: {{site_name}}, документ: {{doc_name}}]({{doc_url}}) Размер {{doc_size}} байт.
        - Ответь на русском языке.
        - Ответ не более 3 пунктов.
        - Если ответа нет - скажите "Не знаю\""""
    )
    # llm_prompt_template: str = (
    #     """Вы — эксперт‑ассистент. На основании нижеприведённого контекста ответьте на вопрос:
    #     {question}
    #
    #     Контекст (название и ссылка указаны в скобках):
    #     {context}
    #
    #     Формат ответа:
    #     - Кратко, по пунктам.
    #     - Каждый пункт должен быть в Markdown‑буллете.
    #     Название_сайта
    #     - В конце каждого пункта добавьте ссылку на источник в формате [сайт: Название_сайта, Тип_документа, Название_документа](Ссылка_на_документ) Размер_документа_в_байтах.
    #     - Ответь на русском языке.
    #     - Если ответа нет - скажите "Не знаю\""""
    # )
    # llm_prompt_template: str = (
    #     """Вы — эксперт‑ассистент. На основании нижеприведённого контекста ответьте на вопрос:
    #     {question}
    #
    #     Контекст (название и ссылка указаны в скобках):
    #     {context}
    #
    #     Формат ответа:
    #     - Кратко, по пунктам.
    #     - Каждый пункт должен быть в Markdown‑буллете.
    #     - В конце каждого пункта добавьте ссылку на источник в формате [source_type, source_name, source_update_time](source_url).
    #     - Ответь на русском языке.
    #     - Если ответа нет - скажите "Не знаю\""""
    # )
    # llm_prompt_template: str = (
    #     """Ответь строго по контексту:
    #     Контекст: {context}
    #     Вопрос: {question}
    #     Требования:
    #     1. Ответ до 3 предложений
    #     2. Ответ на русском языке
    #     3. Если ответа нет - скажи "Не знаю\""""
    # )

    # Ability to read variables from .env
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )


settings = Settings()
