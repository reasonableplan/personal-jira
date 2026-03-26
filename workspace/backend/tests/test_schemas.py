"""Tests for Pydantic schema definitions."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from app.schemas import (
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
    TaskStatus,
    TaskStatusUpdate,
    TaskUpdate,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(tz=UTC)


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


# ---------------------------------------------------------------------------
# PaginationParams
# ---------------------------------------------------------------------------


class TestPaginationParams:
    def test_defaults(self) -> None:
        params = PaginationParams()
        assert params.offset == 0
        assert params.limit == 50

    def test_custom_values(self) -> None:
        params = PaginationParams(offset=10, limit=20)
        assert params.offset == 10
        assert params.limit == 20

    def test_offset_must_be_non_negative(self) -> None:
        with pytest.raises(ValueError):
            PaginationParams(offset=-1)

    def test_limit_must_be_at_least_one(self) -> None:
        with pytest.raises(ValueError):
            PaginationParams(limit=0)

    def test_limit_must_not_exceed_100(self) -> None:
        with pytest.raises(ValueError):
            PaginationParams(limit=101)


# ---------------------------------------------------------------------------
# PaginatedResponse
# ---------------------------------------------------------------------------


class TestPaginatedResponse:
    def test_generic_items(self) -> None:
        resp: PaginatedResponse[str] = PaginatedResponse(
            items=["a", "b"], total=2, offset=0, limit=50
        )
        assert resp.items == ["a", "b"]
        assert resp.total == 2


# ---------------------------------------------------------------------------
# LabelCreate / LabelUpdate / LabelResponse
# ---------------------------------------------------------------------------


class TestLabelSchemas:
    def test_label_create_requires_name_and_color(self) -> None:
        with pytest.raises(ValueError):
            LabelCreate(name="bug")  # type: ignore[call-arg]

    def test_label_create_valid(self) -> None:
        label = LabelCreate(name="bug", color="#ef4444")
        assert label.name == "bug"
        assert label.color == "#ef4444"

    def test_label_update_all_optional(self) -> None:
        update = LabelUpdate()
        assert update.name is None
        assert update.color is None

    def test_label_response_from_attributes(self) -> None:
        label_id = _uuid()
        now = _now()

        class FakeLabel:
            id = label_id
            name = "backend"
            color = "#3b82f6"
            created_at = now

        resp = LabelResponse.model_validate(FakeLabel())
        assert resp.id == label_id
        assert resp.name == "backend"
        assert resp.created_at == now


# ---------------------------------------------------------------------------
# TaskStatus
# ---------------------------------------------------------------------------


class TestTaskStatus:
    def test_all_values_defined(self) -> None:
        values = {s.value for s in TaskStatus}
        assert values == {"backlog", "todo", "in_progress", "in_review", "done"}

    def test_is_str(self) -> None:
        assert isinstance(TaskStatus.backlog, str)


# ---------------------------------------------------------------------------
# TaskCreate / TaskUpdate / TaskResponse / TaskStatusUpdate
# ---------------------------------------------------------------------------


class TestTaskSchemas:
    def test_task_create_defaults(self) -> None:
        story_id = _uuid()
        task = TaskCreate(title="Fix bug", story_id=story_id)
        assert task.status == TaskStatus.backlog
        assert task.priority == 3
        assert task.description is None
        assert task.label_ids is None

    def test_task_create_with_label_ids(self) -> None:
        story_id = _uuid()
        label_id = _uuid()
        task = TaskCreate(title="Fix bug", story_id=story_id, label_ids=[label_id])
        assert task.label_ids == [label_id]

    def test_task_update_all_optional(self) -> None:
        update = TaskUpdate()
        assert update.title is None
        assert update.description is None
        assert update.priority is None
        assert update.story_id is None

    def test_task_response_from_attributes(self) -> None:
        task_id = _uuid()
        sid = _uuid()
        now = _now()

        fake = SimpleNamespace(
            id=task_id,
            title="Implement login",
            description=None,
            status=TaskStatus.todo,
            priority=1,
            story_id=sid,
            labels=[],
            created_at=now,
            updated_at=now,
        )
        resp = TaskResponse.model_validate(fake)
        assert resp.id == task_id
        assert resp.status == TaskStatus.todo
        assert resp.labels == []

    def test_task_status_update_requires_status(self) -> None:
        with pytest.raises(ValueError):
            TaskStatusUpdate()  # type: ignore[call-arg]

    def test_task_status_update_valid(self) -> None:
        upd = TaskStatusUpdate(status=TaskStatus.in_review)
        assert upd.status == TaskStatus.in_review


# ---------------------------------------------------------------------------
# StoryCreate / StoryUpdate / StoryResponse / StoryDetailResponse
# ---------------------------------------------------------------------------


class TestStorySchemas:
    def test_story_create_requires_title_and_epic_id(self) -> None:
        with pytest.raises(ValueError):
            StoryCreate(title="Story A")  # type: ignore[call-arg]

    def test_story_create_valid(self) -> None:
        epic_id = _uuid()
        story = StoryCreate(title="Story A", epic_id=epic_id)
        assert story.epic_id == epic_id
        assert story.description is None

    def test_story_update_all_optional(self) -> None:
        update = StoryUpdate()
        assert update.title is None

    def test_story_response_from_attributes(self) -> None:
        sid = _uuid()
        eid = _uuid()
        now = _now()

        fake = SimpleNamespace(
            id=sid,
            title="User auth story",
            description=None,
            epic_id=eid,
            task_count=5,
            completion_rate=40.0,
            created_at=now,
            updated_at=now,
        )
        resp = StoryResponse.model_validate(fake)
        assert resp.task_count == 5
        assert resp.completion_rate == 40.0

    def test_story_detail_response_includes_tasks(self) -> None:
        sid = _uuid()
        eid = _uuid()
        now = _now()

        fake = SimpleNamespace(
            id=sid,
            title="User auth story",
            description=None,
            epic_id=eid,
            task_count=0,
            completion_rate=0.0,
            created_at=now,
            updated_at=now,
            tasks=[],
        )
        resp = StoryDetailResponse.model_validate(fake)
        assert resp.tasks == []


# ---------------------------------------------------------------------------
# EpicCreate / EpicUpdate / EpicResponse / EpicDetailResponse
# ---------------------------------------------------------------------------


class TestEpicSchemas:
    def test_epic_create_requires_title(self) -> None:
        with pytest.raises(ValueError):
            EpicCreate()  # type: ignore[call-arg]

    def test_epic_create_valid(self) -> None:
        epic = EpicCreate(title="Auth epic")
        assert epic.description is None

    def test_epic_update_all_optional(self) -> None:
        update = EpicUpdate()
        assert update.title is None

    def test_epic_response_from_attributes(self) -> None:
        epic_id = _uuid()
        now = _now()

        class FakeEpic:
            id = epic_id
            title = "Auth system"
            description = "JWT based auth"
            story_count = 3
            completion_rate = 33.3
            created_at = now
            updated_at = now

        resp = EpicResponse.model_validate(FakeEpic())
        assert resp.story_count == 3
        assert resp.completion_rate == 33.3

    def test_epic_detail_response_includes_stories(self) -> None:
        epic_id = _uuid()
        now = _now()

        class FakeEpic:
            id = epic_id
            title = "Auth system"
            description = None
            story_count = 0
            completion_rate = 0.0
            created_at = now
            updated_at = now
            stories: list = []

        resp = EpicDetailResponse.model_validate(FakeEpic())
        assert resp.stories == []
