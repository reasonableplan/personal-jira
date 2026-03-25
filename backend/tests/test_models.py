
from app.models.issue import (
    Base,
    BoardColumn,
    Epic,
    EpicStatus,
    Priority,
    Story,
    StoryStatus,
    Task,
    TaskStatus,
    task_labels,
)
from sqlalchemy import inspect


class TestEpicStatus:
    def test_values(self) -> None:
        assert EpicStatus.PLANNING == "planning"
        assert EpicStatus.ACTIVE == "active"
        assert EpicStatus.COMPLETED == "completed"
        assert EpicStatus.ARCHIVED == "archived"


class TestStoryStatus:
    def test_values(self) -> None:
        assert StoryStatus.TODO == "todo"
        assert StoryStatus.IN_PROGRESS == "in_progress"
        assert StoryStatus.DONE == "done"


class TestTaskStatus:
    def test_values(self) -> None:
        assert TaskStatus.OPEN == "open"
        assert TaskStatus.IN_PROGRESS == "in_progress"
        assert TaskStatus.REVIEW == "review"
        assert TaskStatus.DONE == "done"
        assert TaskStatus.BLOCKED == "blocked"


class TestBoardColumn:
    def test_values(self) -> None:
        assert BoardColumn.BACKLOG == "backlog"
        assert BoardColumn.READY == "ready"
        assert BoardColumn.IN_PROGRESS == "in_progress"
        assert BoardColumn.REVIEW == "review"
        assert BoardColumn.DONE == "done"


class TestPriority:
    def test_values(self) -> None:
        assert Priority.CRITICAL == "critical"
        assert Priority.HIGH == "high"
        assert Priority.MEDIUM == "medium"
        assert Priority.LOW == "low"


class TestEpicModel:
    def test_tablename(self) -> None:
        assert Epic.__tablename__ == "epics"

    def test_columns(self) -> None:
        cols = {c.name for c in Epic.__table__.columns}
        expected = {
            "id", "title", "description",
            "status", "created_at", "updated_at",
        }
        assert expected == cols

    def test_id_is_uuid_pk(self) -> None:
        col = Epic.__table__.c.id
        assert col.primary_key

    def test_title_not_nullable(self) -> None:
        col = Epic.__table__.c.title
        assert not col.nullable

    def test_status_default(self) -> None:
        col = Epic.__table__.c.status
        assert col.default.arg == EpicStatus.PLANNING

    def test_has_stories_relationship(self) -> None:
        assert "stories" in Epic.__mapper__.relationships

    def test_stories_cascade(self) -> None:
        rel = Epic.__mapper__.relationships["stories"]
        assert "delete-orphan" in rel.cascade


class TestStoryModel:
    def test_tablename(self) -> None:
        assert Story.__tablename__ == "stories"

    def test_columns(self) -> None:
        mapper = inspect(Story)
        col_names = {c.key for c in mapper.column_attrs}
        expected = {
            "id", "epic_id", "title", "description",
            "status", "sort_order",
            "created_at", "updated_at",
        }
        assert expected <= col_names

    def test_epic_id_foreign_key(self) -> None:
        col = Story.__table__.c.epic_id
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert fks[0].target_fullname == "epics.id"

    def test_cascade_delete(self) -> None:
        col = Story.__table__.c.epic_id
        fk = list(col.foreign_keys)[0]
        assert fk.ondelete == "CASCADE"

    def test_sort_order_default(self) -> None:
        col = Story.__table__.c.sort_order
        assert col.default.arg == 0

    def test_composite_index_exists(self) -> None:
        idx_names = {
            idx.name for idx in Story.__table__.indexes
        }
        assert "ix_stories_epic_id_sort_order" in idx_names

    def test_has_epic_relationship(self) -> None:
        assert "epic" in Story.__mapper__.relationships

    def test_has_tasks_relationship(self) -> None:
        assert "tasks" in Story.__mapper__.relationships


class TestTaskModel:
    def test_tablename(self) -> None:
        assert Task.__tablename__ == "tasks"

    def test_columns(self) -> None:
        cols = {c.name for c in Task.__table__.columns}
        expected = {
            "id", "story_id", "title", "description",
            "status", "board_column", "assigned_agent",
            "priority", "retry_count", "dependencies",
            "created_at", "started_at",
            "completed_at", "updated_at",
        }
        assert expected == cols

    def test_story_id_foreign_key(self) -> None:
        col = Task.__table__.c.story_id
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert fks[0].target_fullname == "stories.id"

    def test_cascade_delete(self) -> None:
        col = Task.__table__.c.story_id
        fk = list(col.foreign_keys)[0]
        assert fk.ondelete == "CASCADE"

    def test_status_default(self) -> None:
        col = Task.__table__.c.status
        assert col.default.arg == TaskStatus.OPEN

    def test_board_column_default(self) -> None:
        col = Task.__table__.c.board_column
        assert col.default.arg == BoardColumn.BACKLOG

    def test_priority_default(self) -> None:
        col = Task.__table__.c.priority
        assert col.default.arg == Priority.MEDIUM

    def test_retry_count_default(self) -> None:
        col = Task.__table__.c.retry_count
        assert col.default.arg == 0

    def test_assigned_agent_nullable(self) -> None:
        col = Task.__table__.c.assigned_agent
        assert col.nullable

    def test_started_at_nullable(self) -> None:
        col = Task.__table__.c.started_at
        assert col.nullable

    def test_completed_at_nullable(self) -> None:
        col = Task.__table__.c.completed_at
        assert col.nullable

    def test_indexes(self) -> None:
        idx_names = {
            idx.name for idx in Task.__table__.indexes
        }
        assert "ix_tasks_story_id" in idx_names
        assert "ix_tasks_board_column" in idx_names
        assert "ix_tasks_assigned_agent" in idx_names

    def test_has_story_relationship(self) -> None:
        assert "story" in Task.__mapper__.relationships

    def test_has_labels_relationship(self) -> None:
        assert "labels" in Task.__mapper__.relationships


class TestTaskLabelsTable:
    def test_table_name(self) -> None:
        assert task_labels.name == "task_labels"

    def test_columns(self) -> None:
        cols = {c.name for c in task_labels.columns}
        assert cols == {"task_id", "label_id"}

    def test_task_id_fk(self) -> None:
        col = task_labels.c.task_id
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert fks[0].target_fullname == "tasks.id"

    def test_label_id_fk(self) -> None:
        col = task_labels.c.label_id
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert fks[0].target_fullname == "labels.id"

    def test_composite_pk(self) -> None:
        pk_cols = {
            c.name for c in task_labels.primary_key.columns
        }
        assert pk_cols == {"task_id", "label_id"}


class TestBaseDeclarative:
    def test_base_has_metadata(self) -> None:
        assert Base.metadata is not None
