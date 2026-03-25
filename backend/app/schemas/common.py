from pydantic import BaseModel

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int = DEFAULT_PAGE
    per_page: int = DEFAULT_PER_PAGE


class ErrorResponse(BaseModel):
    detail: str
