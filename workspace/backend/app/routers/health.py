import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import get_engine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Docker healthcheck 및 모니터링용 엔드포인트.

    DB 연결 상태를 확인하여 응답에 포함한다.
    """
    engine = get_engine()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception:
        logger.exception("Database health check failed")
        database_status = "disconnected"

    return {"status": "ok", "database": database_status}
