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
    weaviate_model: str                 = "nomic-embed-text"
    weaviate_doc_limit: int             = 5

    llm_url: str                        = "http://ollama:11434"
    llm_model: str                      = "llama3"
    # llm_doc_limit: int                  = 5
    llm_prompt_template: str = (
        """Ответь строго по контексту:
        Контекст: {context}
        Вопрос: {question}
        Требования:
        1. Ответ до 3 предложений
        2. Ответ на русском языке
        3. Если ответа нет - скажи "Не знаю\""""
    )

    # Ability to read variables from .env
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )


settings = Settings()
