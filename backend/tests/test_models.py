
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


class TestBase:
    def test_base_is_declarative(self) -> None:
        assert hasattr(Base, "metadata")
        assert hasattr(Base, "registry")


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

    def test_columns_exist(self) -> None:
        cols = {c.name for c in Epic.__table__.columns}
        assert cols == {"id", "title", "description", "status", "created_at", "updated_at"}

    def test_pk_is_uuid(self) -> None:
        col = Epic.__table__.c.id
        assert col.primary_key

    def test_title_not_nullable(self) -> None:
        assert Epic.__table__.c.title.nullable is False

    def test_description_nullable(self) -> None:
        assert Epic.__table__.c.description.nullable is True

    def test_status_default(self) -> None:
        assert Epic.__table__.c.status.default.arg == EpicStatus.PLANNING

    def test_stories_relationship(self) -> None:
        rel = Epic.__mapper__.relationships["stories"]
        assert rel.cascade.delete is True
        assert rel.cascade.delete_orphan is True


class TestStoryModel:
    def test_tablename(self) -> None:
        assert Story.__tablename__ == "stories"

    def test_columns_exist(self) -> None:
        cols = {c.name for c in Story.__table__.columns}
        assert cols == {
            "id", "epic_id", "title", "description",
            "status", "sort_order", "created_at", "updated_at",
        }

    def test_epic_id_fk(self) -> None:
        col = Story.__table__.c.epic_id
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "epics.id"
        assert fk.ondelete == "CASCADE"

    def test_sort_order_default(self) -> None:
        assert Story.__table__.c.sort_order.default.arg == 0

    def test_composite_index(self) -> None:
        idx_names = {idx.name for idx in Story.__table__.indexes}
        assert "ix_stories_epic_id_sort_order" in idx_names

    def test_tasks_relationship(self) -> None:
        rel = Story.__mapper__.relationships["tasks"]
        assert rel.cascade.delete is True
        assert rel.cascade.delete_orphan is True


class TestTaskModel:
    def test_tablename(self) -> None:
        assert Task.__tablename__ == "tasks"

    def test_columns_exist(self) -> None:
        cols = {c.name for c in Task.__table__.columns}
        expected = {
            "id", "story_id", "title", "description", "status",
            "board_column", "assigned_agent", "priority",
            "retry_count", "dependencies", "created_at",
            "started_at", "completed_at", "updated_at",
        }
        assert cols == expected

    def test_story_id_fk(self) -> None:
        col = Task.__table__.c.story_id
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "stories.id"
        assert fk.ondelete == "CASCADE"

    def test_board_column_default(self) -> None:
        assert Task.__table__.c.board_column.default.arg == BoardColumn.BACKLOG

    def test_priority_default(self) -> None:
        assert Task.__table__.c.priority.default.arg == Priority.MEDIUM

    def test_retry_count_default(self) -> None:
        assert Task.__table__.c.retry_count.default.arg == 0

    def test_assigned_agent_nullable(self) -> None:
        assert Task.__table__.c.assigned_agent.nullable is True

    def test_started_at_nullable(self) -> None:
        assert Task.__table__.c.started_at.nullable is True

    def test_completed_at_nullable(self) -> None:
        assert Task.__table__.c.completed_at.nullable is True

    def test_indexes(self) -> None:
        idx_names = {idx.name for idx in Task.__table__.indexes}
        assert "ix_tasks_story_id" in idx_names
        assert "ix_tasks_board_column" in idx_names
        assert "ix_tasks_assigned_agent" in idx_names

    def test_labels_relationship(self) -> None:
        rel = Task.__mapper__.relationships["labels"]
        assert rel.secondary is task_labels


class TestLabelModel:
    def test_tablename(self) -> None:
        assert Label.__tablename__ == "labels"

    def test_columns_exist(self) -> None:
        cols = {c.name for c in Label.__table__.columns}
        assert cols == {"id", "name", "color"}

    def test_name_not_nullable(self) -> None:
        assert Label.__table__.c.name.nullable is False

    def test_name_unique(self) -> None:
        assert Label.__table__.c.name.unique is True

    def test_color_not_nullable(self) -> None:
        assert Label.__table__.c.color.nullable is False


class TestTaskLabelsTable:
    def test_tablename(self) -> None:
        assert task_labels.name == "task_labels"

    def test_columns(self) -> None:
        cols = {c.name for c in task_labels.columns}
        assert cols == {"task_id", "label_id"}

    def test_task_id_fk(self) -> None:
        fk = list(task_labels.c.task_id.foreign_keys)[0]
        assert fk.target_fullname == "tasks.id"
        assert fk.ondelete == "CASCADE"

    def test_label_id_fk(self) -> None:
        fk = list(task_labels.c.label_id.foreign_keys)[0]
        assert fk.target_fullname == "labels.id"
        assert fk.ondelete == "CASCADE"

    def test_composite_pk(self) -> None:
        pk_cols = {c.name for c in task_labels.primary_key.columns}
        assert pk_cols == {"task_id", "label_id"}
