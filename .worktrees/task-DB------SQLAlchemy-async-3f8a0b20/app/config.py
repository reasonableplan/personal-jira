from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Personal Jira"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str
    ECHO_SQL: bool = False

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()  # type: ignore[call-arg]
