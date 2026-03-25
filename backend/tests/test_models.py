from app.models.issue import (
    Base,
    BoardColumn,
    Epic,
    EpicStatus,
    Label,
    Priority,
    Story,
    StoryStatus,
    Task,
    TaskStatus,
    task_labels,
)
from sqlalchemy import inspect


class TestEpicStatus:
    def test_planning(self) -> None:
        assert EpicStatus.PLANNING == "planning"

    def test_active(self) -> None:
        assert EpicStatus.ACTIVE == "active"

    def test_completed(self) -> None:
        assert EpicStatus.COMPLETED == "completed"

    def test_archived(self) -> None:
        assert EpicStatus.ARCHIVED == "archived"


class TestStoryStatus:
    def test_todo(self) -> None:
        assert StoryStatus.TODO == "todo"

    def test_in_progress(self) -> None:
        assert StoryStatus.IN_PROGRESS == "in_progress"

    def test_done(self) -> None:
        assert StoryStatus.DONE == "done"


class TestTaskStatus:
    def test_open(self) -> None:
        assert TaskStatus.OPEN == "open"

    def test_in_progress(self) -> None:
        assert TaskStatus.IN_PROGRESS == "in_progress"

    def test_review(self) -> None:
        assert TaskStatus.REVIEW == "review"

    def test_done(self) -> None:
        assert TaskStatus.DONE == "done"

    def test_blocked(self) -> None:
        assert TaskStatus.BLOCKED == "blocked"


class TestBoardColumn:
    def test_backlog(self) -> None:
        assert BoardColumn.BACKLOG == "backlog"

    def test_ready(self) -> None:
        assert BoardColumn.READY == "ready"

    def test_in_progress(self) -> None:
        assert BoardColumn.IN_PROGRESS == "in_progress"

    def test_review(self) -> None:
        assert BoardColumn.REVIEW == "review"

    def test_done(self) -> None:
        assert BoardColumn.DONE == "done"


class TestPriority:
    def test_critical(self) -> None:
        assert Priority.CRITICAL == "critical"

    def test_high(self) -> None:
        assert Priority.HIGH == "high"

    def test_medium(self) -> None:
        assert Priority.MEDIUM == "medium"

    def test_low(self) -> None:
        assert Priority.LOW == "low"


class TestEpicModel:
    def test_tablename(self) -> None:
        assert Epic.__tablename__ == "epics"

    def test_columns(self) -> None:
        mapper = inspect(Epic)
        col_names = {c.key for c in mapper.column_attrs}
        expected = {
            "id", "title", "description",
            "status", "created_at", "updated_at",
        }
        assert expected <= col_names

    def test_title_not_nullable(self) -> None:
        col = Epic.__table__.c.title
        assert col.nullable is False

    def test_title_max_length(self) -> None:
        col = Epic.__table__.c.title
        assert col.type.length == 200

    def test_status_default(self) -> None:
        col = Epic.__table__.c.status
        assert col.default.arg == EpicStatus.PLANNING

    def test_description_nullable(self) -> None:
        col = Epic.__table__.c.description
        assert col.nullable is True

    def test_has_stories_relationship(self) -> None:
        assert "stories" in Epic.__mapper__.relationships

    def test_stories_cascade(self) -> None:
        rel = Epic.__mapper__.relationships["stories"]
        assert "delete" in rel.cascade


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
        mapper = inspect(Task)
        col_names = {c.key for c in mapper.column_attrs}
        expected = {
            "id", "story_id", "title", "description",
            "status", "board_column", "assigned_agent",
            "priority", "retry_count", "dependencies",
            "created_at", "started_at", "completed_at",
            "updated_at",
        }
        assert expected <= col_names

    def test_story_id_foreign_key(self) -> None:
        col = Task.__table__.c.story_id
        fks = list(col.foreign_keys)
        assert len(fks) == 1
        assert fks[0].target_fullname == "stories.id"

    def test_story_cascade_delete(self) -> None:
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
        assert col.nullable is True

    def test_started_at_nullable(self) -> None:
        col = Task.__table__.c.started_at
        assert col.nullable is True

    def test_completed_at_nullable(self) -> None:
        col = Task.__table__.c.completed_at
        assert col.nullable is True

    def test_index_story_id(self) -> None:
        idx_names = {
            idx.name for idx in Task.__table__.indexes
        }
        assert "ix_tasks_story_id" in idx_names

    def test_index_board_column(self) -> None:
        idx_names = {
            idx.name for idx in Task.__table__.indexes
        }
        assert "ix_tasks_board_column" in idx_names

    def test_index_assigned_agent(self) -> None:
        idx_names = {
            idx.name for idx in Task.__table__.indexes
        }
        assert "ix_tasks_assigned_agent" in idx_names

    def test_has_story_relationship(self) -> None:
        assert "story" in Task.__mapper__.relationships

    def test_has_labels_relationship(self) -> None:
        assert "labels" in Task.__mapper__.relationships


class TestLabelModel:
    def test_tablename(self) -> None:
        assert Label.__tablename__ == "labels"

    def test_columns(self) -> None:
        mapper = inspect(Label)
        col_names = {c.key for c in mapper.column_attrs}
        expected = {"id", "name", "color"}
        assert expected <= col_names

    def test_name_not_nullable(self) -> None:
        col = Label.__table__.c.name
        assert col.nullable is False

    def test_name_unique(self) -> None:
        col = Label.__table__.c.name
        assert col.unique is True

    def test_has_tasks_relationship(self) -> None:
        assert "tasks" in Label.__mapper__.relationships


class TestTaskLabelsTable:
    def test_table_name(self) -> None:
        assert task_labels.name == "task_labels"

    def test_columns(self) -> None:
        col_names = {c.name for c in task_labels.columns}
        assert col_names == {"task_id", "label_id"}

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

    def test_composite_primary_key(self) -> None:
        pk_cols = {c.name for c in task_labels.primary_key.columns}
        assert pk_cols == {"task_id", "label_id"}


class TestBaseDeclarative:
    def test_base_is_declarative(self) -> None:
        assert hasattr(Base, "metadata")
        assert hasattr(Base, "registry")
