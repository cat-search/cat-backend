from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, EnvSettingsSource


class Settings(BaseSettings):
    app_name: str        = 'cat-backend'
    app_port: int        = 80
    app_version: str     = '0.0.0'
    title: str           = 'API CatSearch'
    log_level: str       = 'INFO'

    db_conn_str: str     = 'postgresql://postgres:postgres@localhost:5433/catsearch'
    alembic_db_name: str = 'catsearch'

    request_timeout: int = 30


settings = Settings()
