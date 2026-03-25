from pydantic import BaseModel

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20
MIN_PAGE = 1
MIN_PER_PAGE = 1
MAX_PER_PAGE = 100


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int = DEFAULT_PAGE
    per_page: int = DEFAULT_PER_PAGE


class ErrorResponse(BaseModel):
    detail: str


class PaginationParams:
    def __init__(
        self,
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> None:
        self.page = max(MIN_PAGE, page)
        self.per_page = max(
            MIN_PER_PAGE, min(MAX_PER_PAGE, per_page)
        )

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
