import enum
import uuid

from sqlalchemy import DateTime, Integer, String, Text, inspect

from app.models.base import Base
from app.models.issue import Issue, IssueStatus


def test_issue_status_is_str_enum() -> None:
    assert issubclass(IssueStatus, enum.StrEnum)
    assert IssueStatus.TODO == "todo"
    assert IssueStatus.IN_PROGRESS == "in_progress"
    assert IssueStatus.DONE == "done"


def test_issue_inherits_base() -> None:
    assert issubclass(Issue, Base)


def test_issue_tablename() -> None:
    assert Issue.__tablename__ == "issues"


def test_issue_columns_exist() -> None:
    mapper = inspect(Issue)
    column_names = {c.key for c in mapper.columns}
    expected = {"id", "title", "description", "status", "priority", "created_at", "updated_at"}
    assert expected == column_names


def test_id_column() -> None:
    col = Issue.__table__.c.id
    assert col.primary_key
    assert col.server_default is not None


def test_title_column() -> None:
    col = Issue.__table__.c.title
    assert not col.nullable
    assert isinstance(col.type, String)
    assert col.type.length == 200


def test_description_column() -> None:
    col = Issue.__table__.c.description
    assert col.nullable
    assert isinstance(col.type, Text)


def test_status_column() -> None:
    col = Issue.__table__.c.status
    assert not col.nullable


def test_priority_column() -> None:
    col = Issue.__table__.c.priority
    assert isinstance(col.type, Integer)


def test_created_at_column() -> None:
    col = Issue.__table__.c.created_at
    assert isinstance(col.type, DateTime)
    assert col.server_default is not None


def test_updated_at_column() -> None:
    col = Issue.__table__.c.updated_at
    assert isinstance(col.type, DateTime)
