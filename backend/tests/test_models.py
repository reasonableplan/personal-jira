"""Tests for SQLAlchemy models: Epic, Story, Task, Label."""

import uuid

from app.models import Base, Epic, Label, Story, Task, TaskStatus
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///:memory:")


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-untyped-def]
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSession = sessionmaker(bind=engine)


def setup_function() -> None:
    Base.metadata.create_all(bind=engine)


def teardown_function() -> None:
    Base.metadata.drop_all(bind=engine)


# --- Import & Re-export ---


def test_import_from_app_models() -> None:
    from app.models import Epic, Story, Task

    assert Epic is not None
    assert Story is not None
    assert Task is not None


# --- TaskStatus Enum ---


def test_task_status_has_five_values() -> None:
    values = [s.value for s in TaskStatus]
    assert values == ["backlog", "ready", "in-progress", "review", "done"]


def test_task_status_default_is_backlog() -> None:
    assert TaskStatus.BACKLOG.value == "backlog"


# --- Table & Column Existence ---


def test_epics_table_exists() -> None:
    inspector = inspect(engine)
    assert "epics" in inspector.get_table_names()


def test_stories_table_exists() -> None:
    inspector = inspect(engine)
    assert "stories" in inspector.get_table_names()


def test_tasks_table_exists() -> None:
    inspector = inspect(engine)
    assert "tasks" in inspector.get_table_names()


def test_task_labels_table_exists() -> None:
    inspector = inspect(engine)
    assert "task_labels" in inspector.get_table_names()


def test_epic_columns() -> None:
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("epics")}
    assert {"id", "title", "description", "created_at", "updated_at"} <= cols


def test_story_columns() -> None:
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("stories")}
    assert {"id", "title", "description", "epic_id", "position", "created_at", "updated_at"} <= cols


def test_task_columns() -> None:
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("tasks")}
    assert {
        "id", "title", "description", "status", "priority",
        "story_id", "position", "created_at", "updated_at",
    } <= cols


# --- FK Relationships ---


def test_story_fk_to_epic() -> None:
    inspector = inspect(engine)
    fks = inspector.get_foreign_keys("stories")
    fk_cols = {fk["constrained_columns"][0] for fk in fks}
    assert "epic_id" in fk_cols


def test_task_fk_to_story() -> None:
    inspector = inspect(engine)
    fks = inspector.get_foreign_keys("tasks")
    fk_cols = {fk["constrained_columns"][0] for fk in fks}
    assert "story_id" in fk_cols


def test_task_labels_fks() -> None:
    inspector = inspect(engine)
    fks = inspector.get_foreign_keys("task_labels")
    fk_cols = {fk["constrained_columns"][0] for fk in fks}
    assert {"task_id", "label_id"} <= fk_cols


# --- CRUD & Relationship Smoke Tests ---


def test_create_epic() -> None:
    with TestSession() as db:
        epic = Epic(title="Test Epic")
        db.add(epic)
        db.commit()
        db.refresh(epic)

        assert isinstance(epic.id, uuid.UUID)
        assert epic.title == "Test Epic"
        assert epic.description is None
        assert epic.created_at is not None
        assert epic.updated_at is not None


def test_create_story_under_epic() -> None:
    with TestSession() as db:
        epic = Epic(title="Epic")
        db.add(epic)
        db.commit()
        db.refresh(epic)

        story = Story(title="Story", epic_id=epic.id, position=1)
        db.add(story)
        db.commit()
        db.refresh(story)

        assert story.epic_id == epic.id
        assert story.position == 1
        assert story.description is None


def test_create_task_under_story() -> None:
    with TestSession() as db:
        epic = Epic(title="E")
        db.add(epic)
        db.commit()
        db.refresh(epic)

        story = Story(title="S", epic_id=epic.id)
        db.add(story)
        db.commit()
        db.refresh(story)

        task = Task(title="T", story_id=story.id)
        db.add(task)
        db.commit()
        db.refresh(task)

        assert task.story_id == story.id
        assert task.status == TaskStatus.BACKLOG
        assert task.priority == 3
        assert task.position == 0


def test_epic_stories_relationship() -> None:
    with TestSession() as db:
        epic = Epic(title="Epic")
        db.add(epic)
        db.commit()
        db.refresh(epic)

        s1 = Story(title="S1", epic_id=epic.id, position=0)
        s2 = Story(title="S2", epic_id=epic.id, position=1)
        db.add_all([s1, s2])
        db.commit()
        db.refresh(epic)

        assert len(epic.stories) == 2


def test_story_tasks_relationship() -> None:
    with TestSession() as db:
        epic = Epic(title="E")
        db.add(epic)
        db.commit()
        db.refresh(epic)

        story = Story(title="S", epic_id=epic.id)
        db.add(story)
        db.commit()
        db.refresh(story)

        t1 = Task(title="T1", story_id=story.id)
        t2 = Task(title="T2", story_id=story.id)
        db.add_all([t1, t2])
        db.commit()
        db.refresh(story)

        assert len(story.tasks) == 2


def test_task_story_back_populates() -> None:
    with TestSession() as db:
        epic = Epic(title="E")
        db.add(epic)
        db.commit()
        db.refresh(epic)

        story = Story(title="S", epic_id=epic.id)
        db.add(story)
        db.commit()
        db.refresh(story)

        task = Task(title="T", story_id=story.id)
        db.add(task)
        db.commit()
        db.refresh(task)

        assert task.story.id == story.id


def test_story_epic_back_populates() -> None:
    with TestSession() as db:
        epic = Epic(title="E")
        db.add(epic)
        db.commit()
        db.refresh(epic)

        story = Story(title="S", epic_id=epic.id)
        db.add(story)
        db.commit()
        db.refresh(story)

        assert story.epic.id == epic.id


def test_cascade_delete_epic_removes_stories() -> None:
    with TestSession() as db:
        epic = Epic(title="E")
        db.add(epic)
        db.commit()
        db.refresh(epic)

        story = Story(title="S", epic_id=epic.id)
        db.add(story)
        db.commit()

        db.delete(epic)
        db.commit()

        remaining = db.query(Story).all()
        assert len(remaining) == 0


def test_cascade_delete_story_removes_tasks() -> None:
    with TestSession() as db:
        epic = Epic(title="E")
        db.add(epic)
        db.commit()
        db.refresh(epic)

        story = Story(title="S", epic_id=epic.id)
        db.add(story)
        db.commit()
        db.refresh(story)

        task = Task(title="T", story_id=story.id)
        db.add(task)
        db.commit()

        db.delete(story)
        db.commit()

        remaining = db.query(Task).all()
        assert len(remaining) == 0


def test_title_max_length_200() -> None:
    """Verify title column accepts up to 200 chars."""
    with TestSession() as db:
        epic = Epic(title="A" * 200)
        db.add(epic)
        db.commit()
        db.refresh(epic)
        assert len(epic.title) == 200


def test_mapped_column_style() -> None:
    """Verify models use SQLAlchemy 2.0 mapped_column (Mapped annotations)."""
    from sqlalchemy.orm import MappedColumn

    mapper = inspect(Epic)
    for attr in mapper.column_attrs:
        for col in attr.columns:
            assert isinstance(col, MappedColumn) or hasattr(col, "key")


# --- Label & TaskLabel ---


def test_import_label_from_app_models() -> None:
    from app.models import Label

    assert Label is not None


def test_labels_table_exists() -> None:
    inspector = inspect(engine)
    assert "labels" in inspector.get_table_names()


def test_label_columns() -> None:
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("labels")}
    assert {"id", "name", "color", "created_at", "updated_at"} <= cols


def test_label_name_max_length_50() -> None:
    inspector = inspect(engine)
    for col in inspector.get_columns("labels"):
        if col["name"] == "name":
            assert col["type"].length == 50


def test_label_color_max_length_7() -> None:
    inspector = inspect(engine)
    for col in inspector.get_columns("labels"):
        if col["name"] == "color":
            assert col["type"].length == 7


def test_label_name_unique() -> None:
    inspector = inspect(engine)
    unique_constraints = inspector.get_unique_constraints("labels")
    unique_cols = set()
    for uc in unique_constraints:
        for col in uc["column_names"]:
            unique_cols.add(col)
    # Also check indexes for unique=True on column
    indexes = inspector.get_indexes("labels")
    for idx in indexes:
        if idx.get("unique"):
            for col in idx["column_names"]:
                unique_cols.add(col)
    assert "name" in unique_cols


def test_create_label() -> None:
    with TestSession() as db:
        label = Label(name="bug", color="#FF0000")
        db.add(label)
        db.commit()
        db.refresh(label)

        assert isinstance(label.id, uuid.UUID)
        assert label.name == "bug"
        assert label.color == "#FF0000"
        assert label.created_at is not None


def test_task_labels_columns() -> None:
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("task_labels")}
    assert {"task_id", "label_id", "created_at"} <= cols


def test_task_labels_relationship() -> None:
    """Task.labels and Label.tasks M:N relationship works."""
    with TestSession() as db:
        epic = Epic(title="E")
        db.add(epic)
        db.commit()
        db.refresh(epic)

        story = Story(title="S", epic_id=epic.id)
        db.add(story)
        db.commit()
        db.refresh(story)

        task = Task(title="T", story_id=story.id)
        label = Label(name="urgent", color="#FF0000")
        db.add_all([task, label])
        db.commit()
        db.refresh(task)
        db.refresh(label)

        task.labels.append(label)
        db.commit()
        db.refresh(task)
        db.refresh(label)

        assert len(task.labels) == 1
        assert task.labels[0].name == "urgent"
        assert len(label.tasks) == 1
        assert label.tasks[0].title == "T"


def test_label_tasks_back_populates() -> None:
    """Label.tasks reverse relationship works."""
    with TestSession() as db:
        epic = Epic(title="E")
        db.add(epic)
        db.commit()
        db.refresh(epic)

        story = Story(title="S", epic_id=epic.id)
        db.add(story)
        db.commit()
        db.refresh(story)

        t1 = Task(title="T1", story_id=story.id)
        t2 = Task(title="T2", story_id=story.id)
        label = Label(name="feature", color="#00FF00")
        db.add_all([t1, t2, label])
        db.commit()

        t1.labels.append(label)
        t2.labels.append(label)
        db.commit()
        db.refresh(label)

        assert len(label.tasks) == 2
