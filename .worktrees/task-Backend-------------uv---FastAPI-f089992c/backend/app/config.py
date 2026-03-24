import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "postgresql://{user}:{password}@{host}:{port}/{db}".format(
            user=os.getenv("POSTGRES_USER", "personal_jira"),
            password=os.getenv("POSTGRES_PASSWORD", "personal_jira"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5434"),
            db=os.getenv("POSTGRES_DB", "personal_jira"),
        )
    )
    app_name: str = "Personal Jira"
    debug: bool = False

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
