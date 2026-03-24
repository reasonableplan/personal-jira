from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "", "case_sensitive": False}

    database_url: str = "postgresql+asyncpg://personal_jira:personal_jira@localhost:5434/personal_jira"
    cors_origins: list[str] = ["http://localhost:5173"]
    debug: bool = False


settings = Settings()
