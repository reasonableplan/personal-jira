import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import engine
from app.core.error_handlers import register_error_handlers
from app.routers import dashboard, epics, labels, stories, tasks

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Verify DB connectivity on startup, dispose engine on shutdown."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("Database connection verified")
    yield
    await engine.dispose()
    logger.info("Database engine disposed")


app = FastAPI(title="Personal Jira", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(epics.router)
app.include_router(stories.router)
app.include_router(tasks.router)
app.include_router(labels.router)
app.include_router(dashboard.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
