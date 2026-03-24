from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    APP_NAME: str = "fastapi-app"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str
    DB_ECHO: bool = False


settings = Settings()  # type: ignore[call-arg]
