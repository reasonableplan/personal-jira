import os

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./personal_jira.db")
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE_BYTES: int = int(os.getenv("MAX_FILE_SIZE_BYTES", str(10 * 1024 * 1024)))
WEBHOOK_TIMEOUT_SECONDS: int = int(os.getenv("WEBHOOK_TIMEOUT_SECONDS", "10"))
