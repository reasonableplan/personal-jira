from datetime import datetime

from sqlalchemy import inspect

from app.models.issue import Issue


def test_issue_table_name() -> None:
    assert Issue.__tablename__ == "issues"


def test_issue_columns_exist() -> None:
    mapper = inspect(Issue)
    columns = {c.key for c in mapper.columns}
    expected = {"id", "title", "description", "status", "priority", "created_at", "updated_at"}
    assert expected == columns


def test_issue_id_is_primary_key() -> None:
    mapper = inspect(Issue)
    pk_cols = [c.key for c in mapper.columns if c.primary_key]
    assert pk_cols == ["id"]


def test_issue_title_not_nullable() -> None:
    mapper = inspect(Issue)
    title_col = mapper.columns["title"]
    assert title_col.nullable is False


def test_issue_description_nullable() -> None:
    mapper = inspect(Issue)
    desc_col = mapper.columns["description"]
    assert desc_col.nullable is True


def test_issue_status_default() -> None:
    issue = Issue(title="test")
    assert issue.status == "todo"


def test_issue_priority_default() -> None:
    issue = Issue(title="test")
    assert issue.priority == 3


def test_issue_status_indexed() -> None:
    mapper = inspect(Issue)
    status_col = mapper.columns["status"]
    assert status_col.index is True


def test_issue_priority_indexed() -> None:
    mapper = inspect(Issue)
    priority_col = mapper.columns["priority"]
    assert priority_col.index is True


def test_issue_title_max_length() -> None:
    mapper = inspect(Issue)
    title_col = mapper.columns["title"]
    assert title_col.type.length == 200


def test_issue_status_max_length() -> None:
    mapper = inspect(Issue)
    status_col = mapper.columns["status"]
    assert status_col.type.length == 20
