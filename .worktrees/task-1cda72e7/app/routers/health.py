from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

HTTP_STATUS_OK = 200
HTTP_STATUS_SERVICE_UNAVAILABLE = 503

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        await db.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=HTTP_STATUS_OK,
            content={"status": "healthy", "database": "connected"},
        )
    except Exception as exc:
        return JSONResponse(
            status_code=HTTP_STATUS_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "disconnected", "detail": str(exc)},
        )
