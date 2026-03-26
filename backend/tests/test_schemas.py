"""Tests for Pydantic schemas."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from app.models.task import TaskStatus
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.epic import EpicCreate, EpicDetailResponse, EpicResponse, EpicUpdate
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate
from app.schemas.story import (
    StoryCreate,
    StoryDetailResponse,
    StoryResponse,
    StoryUpdate,
)
from app.schemas.task import TaskCreate, TaskResponse, TaskStatusUpdate, TaskUpdate
from pydantic import ValidationError


class TestPaginationParams:
    def test_defaults(self) -> None:
        p = PaginationParams()
        assert p.offset == 0
        assert p.limit == 20

    def test_custom_values(self) -> None:
        p = PaginationParams(offset=10, limit=50)
        assert p.offset == 10
        assert p.limit == 50

    def test_negative_offset_rejected(self) -> None:
        with pytest.raises(ValidationError):
            PaginationParams(offset=-1)

    def test_limit_too_large_rejected(self) -> None:
        with pytest.raises(ValidationError):
            PaginationParams(limit=101)

    def test_limit_zero_rejected(self) -> None:
        with pytest.raises(ValidationError):
            PaginationParams(limit=0)


class TestPaginatedResponse:
    def test_generic_response(self) -> None:
        resp = PaginatedResponse[int](items=[1, 2, 3], total=10, offset=0, limit=20)
        assert resp.items == [1, 2, 3]
        assert resp.total == 10


class TestLabelSchemas:
    def test_label_create(self) -> None:
        lc = LabelCreate(name="bug", color="#ff0000")
        assert lc.name == "bug"
        assert lc.color == "#ff0000"

    def test_label_create_invalid_color(self) -> None:
        with pytest.raises(ValidationError):
            LabelCreate(name="bug", color="red")

    def test_label_update_partial(self) -> None:
        lu = LabelUpdate(name="feature")
        assert lu.name == "feature"
        assert lu.color is None

    def test_label_response(self) -> None:
        lr = LabelResponse(
            id=uuid4(),
            name="bug",
            color="#ff0000",
            created_at=datetime.now(UTC),
        )
        assert lr.name == "bug"


class TestEpicSchemas:
    def test_epic_create_minimal(self) -> None:
        ec = EpicCreate(title="Epic 1")
        assert ec.title == "Epic 1"
        assert ec.description is None

    def test_epic_create_full(self) -> None:
        ec = EpicCreate(title="Epic 1", description="desc")
        assert ec.description == "desc"

    def test_epic_update_partial(self) -> None:
        eu = EpicUpdate(description="new desc")
        assert eu.title is None
        assert eu.description == "new desc"

    def test_epic_response(self) -> None:
        er = EpicResponse(
            id=uuid4(),
            title="Epic 1",
            description=None,
            story_count=3,
            completion_rate=0.5,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        assert er.story_count == 3

    def test_epic_detail_response(self) -> None:
        edr = EpicDetailResponse(
            id=uuid4(),
            title="Epic 1",
            description=None,
            story_count=0,
            completion_rate=0.0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            stories=[],
        )
        assert edr.stories == []


class TestStorySchemas:
    def test_story_create(self) -> None:
        sc = StoryCreate(title="Story 1", epic_id=uuid4())
        assert sc.description is None

    def test_story_update_partial(self) -> None:
        su = StoryUpdate(title="Updated")
        assert su.epic_id is None

    def test_story_response(self) -> None:
        sr = StoryResponse(
            id=uuid4(),
            title="Story 1",
            description=None,
            epic_id=uuid4(),
            task_count=5,
            completion_rate=0.8,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        assert sr.task_count == 5

    def test_story_detail_response(self) -> None:
        sdr = StoryDetailResponse(
            id=uuid4(),
            title="Story 1",
            description=None,
            epic_id=uuid4(),
            task_count=0,
            completion_rate=0.0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            tasks=[],
        )
        assert sdr.tasks == []


class TestTaskSchemas:
    def test_task_create_minimal(self) -> None:
        tc = TaskCreate(title="Task 1", story_id=uuid4())
        assert tc.status == TaskStatus.BACKLOG
        assert tc.priority == 3
        assert tc.label_ids is None

    def test_task_create_with_labels(self) -> None:
        lid = uuid4()
        tc = TaskCreate(title="Task 1", story_id=uuid4(), label_ids=[lid])
        assert tc.label_ids == [lid]

    def test_task_create_invalid_priority(self) -> None:
        with pytest.raises(ValidationError):
            TaskCreate(title="Task 1", story_id=uuid4(), priority=6)

    def test_task_update_partial(self) -> None:
        tu = TaskUpdate(title="Updated")
        assert tu.description is None
        assert tu.priority is None

    def test_task_status_update(self) -> None:
        tsu = TaskStatusUpdate(status=TaskStatus.IN_PROGRESS)
        assert tsu.status == TaskStatus.IN_PROGRESS

    def test_task_status_update_invalid(self) -> None:
        with pytest.raises(ValidationError):
            TaskStatusUpdate(status="invalid")

    def test_task_response(self) -> None:
        now = datetime.now(UTC)
        tr = TaskResponse(
            id=uuid4(),
            title="Task 1",
            description="desc",
            status=TaskStatus.BACKLOG,
            priority=3,
            story_id=uuid4(),
            labels=[],
            created_at=now,
            updated_at=now,
        )
        assert tr.labels == []

    def test_task_response_with_labels(self) -> None:
        now = datetime.now(UTC)
        label = LabelResponse(
            id=uuid4(),
            name="bug",
            color="#ff0000",
            created_at=now,
        )
        tr = TaskResponse(
            id=uuid4(),
            title="Task 1",
            description=None,
            status=TaskStatus.DONE,
            priority=1,
            story_id=uuid4(),
            labels=[label],
            created_at=now,
            updated_at=now,
        )
        assert len(tr.labels) == 1
        assert tr.labels[0].name == "bug"


class TestFromAttributes:
    """Verify model_config = ConfigDict(from_attributes=True) is set."""

    def test_label_response_from_attributes(self) -> None:
        assert LabelResponse.model_config.get("from_attributes") is True

    def test_epic_response_from_attributes(self) -> None:
        assert EpicResponse.model_config.get("from_attributes") is True

    def test_story_response_from_attributes(self) -> None:
        assert StoryResponse.model_config.get("from_attributes") is True

    def test_task_response_from_attributes(self) -> None:
        assert TaskResponse.model_config.get("from_attributes") is True


class TestImportFromInit:
    """Verify all schemas are importable from app.schemas."""

    def test_all_imports(self) -> None:
        from app.schemas import (  # noqa: F401
            EpicCreate,
            EpicDetailResponse,
            EpicResponse,
            EpicUpdate,
            LabelCreate,
            LabelResponse,
            LabelUpdate,
            PaginatedResponse,
            PaginationParams,
            StoryCreate,
            StoryDetailResponse,
            StoryResponse,
            StoryUpdate,
            TaskCreate,
            TaskResponse,
            TaskStatusUpdate,
            TaskUpdate,
        )
