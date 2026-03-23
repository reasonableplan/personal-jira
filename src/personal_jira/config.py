import os
from dataclasses import dataclass, field


DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./personal_jira.db")
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE_BYTES: int = int(os.getenv("MAX_FILE_SIZE_BYTES", str(10 * 1024 * 1024)))
WEBHOOK_TIMEOUT_SECONDS: int = int(os.getenv("WEBHOOK_TIMEOUT_SECONDS", "10"))


@dataclass
class Settings:
    database_url: str = field(default_factory=lambda: DATABASE_URL)
    upload_dir: str = field(default_factory=lambda: UPLOAD_DIR)
    max_file_size_bytes: int = field(default_factory=lambda: MAX_FILE_SIZE_BYTES)
    webhook_timeout_seconds: int = field(default_factory=lambda: WEBHOOK_TIMEOUT_SECONDS)


settings = Settings()
