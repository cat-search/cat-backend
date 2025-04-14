from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, EnvSettingsSource


class Settings(BaseSettings):
    app_name: str        = 'cat-backend'
    app_port: int        = 80
    app_version: str     = '0.0.0'
    title: str           = 'CatSearch API backend'
    log_level: str       = 'INFO'

    # db_conn_str: str     = 'postgresql://postgres:Oue$8AriEOdN@cat-vm2.v6.rocks:65432/catsearch'
    db_conn_str: str     = 'postgresql://postgres:postgres@localhost:5433/catsearch'
    alembic_db_name: str = 'catbackend'

    request_timeout: int = 30

    vdb_type: str        = 'weaviate'

    # Vector DB. weaviate
    weaviate_host: str                  = "cat-vm2.v6.rocks"
    weaviate_port: int                  = 8080
    weaviate_grpc_port: int             = 50051
    weaviate_api_key: str               = "Hack_the_VK"
    weaviate_collection: str            = "index_20250413"
    weaviate_api_endpoint: str          = "http://ollama:11434"
    # Model name. If it's `None`, uses the server-defined default
    weaviate_model: str                 = "nomic-embed-text"
    weaviate_doc_limit: int   = 5


settings = Settings()
