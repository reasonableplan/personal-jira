"""Tests for SQLAlchemy models: Label, task_labels association table."""

import uuid

from app.models import Base, Label, Task
from app.models.epic import Epic
from app.models.story import Story
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


# --- Import & Table Existence ---


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
    # Also check via index
    indexes = inspector.get_indexes("labels")
    for idx in indexes:
        if idx["unique"]:
            for col in idx["column_names"]:
                unique_cols.add(col)
    assert "name" in unique_cols


# --- task_labels Association Table ---


def test_task_labels_table_columns() -> None:
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("task_labels")}
    assert {"task_id", "label_id", "created_at"} <= cols


def test_task_labels_fks() -> None:
    inspector = inspect(engine)
    fks = inspector.get_foreign_keys("task_labels")
    fk_cols = {fk["constrained_columns"][0] for fk in fks}
    assert {"task_id", "label_id"} <= fk_cols


# --- CRUD ---


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


# --- Relationships ---


def test_task_labels_relationship() -> None:
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
        label = Label(name="bug", color="#FF0000")
        db.add_all([task, label])
        db.commit()
        db.refresh(task)
        db.refresh(label)

        task.labels.append(label)
        db.commit()
        db.refresh(task)

        assert len(task.labels) == 1
        assert task.labels[0].name == "bug"


def test_label_tasks_back_populates() -> None:
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
        label = Label(name="feature", color="#00FF00")
        db.add_all([task, label])
        db.commit()

        task.labels.append(label)
        db.commit()
        db.refresh(label)

        assert len(label.tasks) == 1
        assert label.tasks[0].title == "T"
