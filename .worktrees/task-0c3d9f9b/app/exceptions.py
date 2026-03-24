from starlette.exceptions import HTTPException as StarletteHTTPException

HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_INTERNAL = 500


class AppException(Exception):
    def __init__(self, detail: str, status_code: int = HTTP_STATUS_INTERNAL) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class IssueNotFoundException(AppException):
    def __init__(self, issue_id: int) -> None:
        super().__init__(
            detail=f"Issue with id {issue_id} not found",
            status_code=HTTP_STATUS_NOT_FOUND,
        )
