import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///")
os.environ.setdefault("TESTING", "true")
