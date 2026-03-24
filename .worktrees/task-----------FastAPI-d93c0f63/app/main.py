from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.database import close_db, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    if not settings.TESTING:
        init_db(settings.DATABASE_URL)
    yield
    await close_db()


app = FastAPI(title="fastapi-app", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "app": settings.APP_NAME}
