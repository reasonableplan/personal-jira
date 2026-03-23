import os

DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/personal_jira")

DEFAULT_PAGE_LIMIT: int = 20
MAX_PAGE_LIMIT: int = 100
TITLE_MAX_LENGTH: int = 500
