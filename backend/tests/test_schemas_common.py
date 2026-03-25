from pydantic import BaseModel

from app.schemas.common import PaginatedResponse, PaginationParams


class ItemSchema(BaseModel):
    id: int
    name: str


class TestPaginatedResponse:
    def test_basic_fields(self) -> None:
        resp = PaginatedResponse[ItemSchema](
            items=[ItemSchema(id=1, name="a")],
            total=1,
            page=1,
            per_page=20,
        )
        assert resp.total == 1
        assert resp.page == 1
        assert resp.per_page == 20
        assert len(resp.items) == 1

    def test_items_typed(self) -> None:
        resp = PaginatedResponse[ItemSchema](
            items=[ItemSchema(id=1, name="a"), ItemSchema(id=2, name="b")],
            total=2,
            page=1,
            per_page=20,
        )
        assert resp.items[0].id == 1
        assert resp.items[1].name == "b"

    def test_empty_items(self) -> None:
        resp = PaginatedResponse[ItemSchema](
            items=[], total=0, page=1, per_page=20
        )
        assert resp.items == []
        assert resp.total == 0

    def test_serialization(self) -> None:
        resp = PaginatedResponse[ItemSchema](
            items=[ItemSchema(id=1, name="a")],
            total=1,
            page=1,
            per_page=20,
        )
        data = resp.model_dump()
        assert data == {
            "items": [{"id": 1, "name": "a"}],
            "total": 1,
            "page": 1,
            "per_page": 20,
        }


class TestPaginationParams:
    def test_defaults(self) -> None:
        params = PaginationParams()
        assert params.page == 1
        assert params.per_page == 20

    def test_custom_values(self) -> None:
        params = PaginationParams(page=3, per_page=50)
        assert params.page == 3
        assert params.per_page == 50

    def test_offset_page_1(self) -> None:
        params = PaginationParams(page=1, per_page=20)
        assert params.offset == 0

    def test_offset_page_3(self) -> None:
        params = PaginationParams(page=3, per_page=10)
        assert params.offset == 20

    def test_page_min_1(self) -> None:
        params = PaginationParams(page=0, per_page=20)
        assert params.page == 1

    def test_per_page_min_1(self) -> None:
        params = PaginationParams(page=1, per_page=0)
        assert params.per_page == 1

    def test_per_page_max_100(self) -> None:
        params = PaginationParams(page=1, per_page=200)
        assert params.per_page == 100
