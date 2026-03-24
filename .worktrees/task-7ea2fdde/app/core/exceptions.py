import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, detail: str, status_code: int = 400) -> None:
        self.detail = detail
        self.status_code = status_code


class IssueNotFoundException(AppException):
    def __init__(self, issue_id: int) -> None:
        super().__init__(detail=f"Issue {issue_id} not found", status_code=404)


def _error_response(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "status_code": status_code},
    )


async def handle_app_exception(_request: Request, exc: AppException) -> JSONResponse:
    return _error_response(exc.status_code, exc.detail)


async def handle_validation_exception(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    messages = "; ".join(f"{e['loc']}: {e['msg']}" for e in errors)
    return _error_response(422, messages)


async def handle_generic_exception(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return _error_response(500, "Internal server error")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, handle_app_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(Exception, handle_generic_exception)
