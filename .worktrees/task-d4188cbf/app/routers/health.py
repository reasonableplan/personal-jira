import logging

from app.core.database import async_session_factory
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

logger = logging.getLogger(__name__)

router = APIRouter()

STATUS_OK = "ok"
STATUS_DEGRADED = "degraded"
DB_CONNECTED = "connected"
DB_DISCONNECTED = "disconnected"
HTTP_OK = 200
HTTP_SERVICE_UNAVAILABLE = 503


@router.get("/health")
async def health() -> JSONResponse:
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=HTTP_OK,
            content={"status": STATUS_OK, "database": DB_CONNECTED},
        )
    except Exception:
        logger.exception("Database health check failed")
        return JSONResponse(
            status_code=HTTP_SERVICE_UNAVAILABLE,
            content={"status": STATUS_DEGRADED, "database": DB_DISCONNECTED},
        )
