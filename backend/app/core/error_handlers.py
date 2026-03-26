"""FastAPI exception handler 등록.

모든 커스텀 예외를 일관된 JSON 형식으로 변환한다:
  {"detail": str, "error_code": str}
"""

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import ConflictError, NotFoundError, ValidationError


async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": exc.detail, "error_code": exc.error_code},
    )


async def conflict_handler(_request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": exc.detail, "error_code": exc.error_code},
    )


async def validation_error_handler(_request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": exc.detail, "error_code": exc.error_code},
    )


def register_error_handlers(app: FastAPI) -> None:
    """FastAPI 앱에 커스텀 예외 핸들러를 등록한다."""
    app.add_exception_handler(NotFoundError, not_found_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ConflictError, conflict_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationError, validation_error_handler)  # type: ignore[arg-type]
