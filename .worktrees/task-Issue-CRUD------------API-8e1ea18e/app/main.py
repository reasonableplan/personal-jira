from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.issues import router as issues_router
from app.core.config import get_settings
from app.core.database import engine
from app.core.exceptions import register_exception_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await engine.dispose()


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

register_exception_handlers(app)
app.include_router(issues_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
