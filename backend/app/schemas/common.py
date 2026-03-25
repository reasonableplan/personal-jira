from typing import Self

from pydantic import BaseModel, model_validator


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    per_page: int


class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 20

    @model_validator(mode="after")
    def clamp_values(self) -> Self:
        if self.page < 1:
            self.page = 1
        if self.per_page < 1:
            self.per_page = 1
        elif self.per_page > 100:
            self.per_page = 100
        return self

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
