"""커스텀 예외 클래스.

서비스 레이어에서 raise하면 error_handlers.py가 일관된 HTTP 응답으로 변환한다.
"""


class AppError(Exception):
    """모든 커스텀 예외의 기본 클래스."""

    def __init__(self, detail: str, error_code: str) -> None:
        self.detail = detail
        self.error_code = error_code
        super().__init__(detail)


class NotFoundError(AppError):
    """리소스를 찾을 수 없을 때 발생. → HTTP 404"""

    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND") -> None:
        super().__init__(detail=detail, error_code=error_code)


class ConflictError(AppError):
    """리소스 충돌 시 발생 (예: 중복 이름). → HTTP 409"""

    def __init__(self, detail: str = "Resource conflict", error_code: str = "CONFLICT") -> None:
        super().__init__(detail=detail, error_code=error_code)


class ValidationError(AppError):
    """비즈니스 로직 유효성 검증 실패 시 발생. → HTTP 400"""

    def __init__(
        self, detail: str = "Validation failed", error_code: str = "VALIDATION_ERROR"
    ) -> None:
        super().__init__(detail=detail, error_code=error_code)
