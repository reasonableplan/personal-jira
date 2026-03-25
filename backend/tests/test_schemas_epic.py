from datetime import UTC, datetime
from uuid import uuid4

import pytest
from app.schemas.epic import (
    EpicCreate,
    EpicDetailResponse,
    EpicResponse,
    EpicUpdate,
    StoryResponse,
)
from pydantic import ValidationError


class TestEpicCreate:
    def test_valid_title_only(self) -> None:
        schema = EpicCreate(title="My Epic")
        assert schema.title == "My Epic"
        assert schema.description is None

    def test_valid_with_description(self) -> None:
        schema = EpicCreate(title="E", description="Some desc")
        assert schema.description == "Some desc"

    def test_title_required(self) -> None:
        with pytest.raises(ValidationError):
            EpicCreate()  # type: ignore[call-arg]

    def test_serialization(self) -> None:
        data = EpicCreate(title="T", description="D").model_dump()
        assert data == {"title": "T", "description": "D"}


class TestEpicUpdate:
    def test_all_optional(self) -> None:
        schema = EpicUpdate()
        assert schema.title is None
        assert schema.description is None
        assert schema.status is None

    def test_partial_update(self) -> None:
        schema = EpicUpdate(title="New")
        dumped = schema.model_dump(exclude_unset=True)
        assert dumped == {"title": "New"}

    def test_status_update(self) -> None:
        schema = EpicUpdate(status="completed")
        assert schema.status == "completed"


class TestEpicResponse:
    def test_from_attributes_enabled(self) -> None:
        assert EpicResponse.model_config.get("from_attributes") is True

    def test_all_fields(self) -> None:
        now = datetime.now(UTC)
        uid = uuid4()
        resp = EpicResponse(
            id=uid,
            title="T",
            description=None,
            status="active",
            created_at=now,
            updated_at=now,
        )
        assert resp.id == uid
        assert resp.title == "T"
        assert resp.description is None
        assert resp.status == "active"
        assert resp.created_at == now
        assert resp.updated_at == now

    def test_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            EpicResponse(id=uuid4(), title="T")  # type: ignore[call-arg]


class TestStoryResponse:
    def test_from_attributes_enabled(self) -> None:
        assert StoryResponse.model_config.get("from_attributes") is True

    def test_all_fields(self) -> None:
        now = datetime.now(UTC)
        uid = uuid4()
        epic_id = uuid4()
        resp = StoryResponse(
            id=uid,
            epic_id=epic_id,
            title="Story",
            description="D",
            status="active",
            sort_order=1,
            created_at=now,
            updated_at=now,
        )
        assert resp.id == uid
        assert resp.epic_id == epic_id
        assert resp.sort_order == 1


class TestEpicDetailResponse:
    def test_inherits_epic_response(self) -> None:
        assert issubclass(EpicDetailResponse, EpicResponse)

    def test_stories_default_empty(self) -> None:
        now = datetime.now(UTC)
        resp = EpicDetailResponse(
            id=uuid4(),
            title="T",
            description=None,
            status="active",
            created_at=now,
            updated_at=now,
        )
        assert resp.stories == []

    def test_with_stories(self) -> None:
        now = datetime.now(UTC)
        story_data = StoryResponse(
            id=uuid4(),
            epic_id=uuid4(),
            title="S",
            description=None,
            status="active",
            sort_order=0,
            created_at=now,
            updated_at=now,
        )
        resp = EpicDetailResponse(
            id=uuid4(),
            title="T",
            description=None,
            status="active",
            created_at=now,
            updated_at=now,
            stories=[story_data],
        )
        assert len(resp.stories) == 1
        assert resp.stories[0].title == "S"
