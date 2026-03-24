from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "fastapi-app"
    DEBUG: bool = False
    DATABASE_URL: str
    TESTING: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    return Settings()
