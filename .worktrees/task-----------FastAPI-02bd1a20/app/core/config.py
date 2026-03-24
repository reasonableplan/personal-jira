from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "fastapi-app"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
