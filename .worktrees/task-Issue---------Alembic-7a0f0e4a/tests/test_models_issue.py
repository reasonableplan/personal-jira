from datetime import datetime

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base, Issue


def test_issue_table_name():
    assert Issue.__tablename__ == "issues"


def test_issue_columns():
    mapper = inspect(Issue)
    columns = {c.key for c in mapper.columns}
    expected = {"id", "title", "description", "status", "priority", "created_at", "updated_at"}
    assert expected == columns


def test_issue_id_primary_key():
    mapper = inspect(Issue)
    pk_cols = [c.name for c in mapper.columns if c.primary_key]
    assert pk_cols == ["id"]


def test_issue_title_not_nullable():
    mapper = inspect(Issue)
    title_col = mapper.columns["title"]
    assert title_col.nullable is False


def test_issue_description_nullable():
    mapper = inspect(Issue)
    desc_col = mapper.columns["description"]
    assert desc_col.nullable is True


def test_issue_status_default():
    issue = Issue(title="Test")
    assert issue.status == "todo"


def test_issue_priority_default():
    issue = Issue(title="Test")
    assert issue.priority == "medium"


def test_issue_status_indexed():
    mapper = inspect(Issue)
    status_col = mapper.columns["status"]
    assert status_col.index is True


def test_issue_priority_indexed():
    mapper = inspect(Issue)
    priority_col = mapper.columns["priority"]
    assert priority_col.index is True


def test_issue_inherits_base():
    assert issubclass(Issue, Base)


@pytest.mark.asyncio
async def test_issue_create_and_read(db_session: AsyncSession):
    issue = Issue(title="Test issue", description="A test", status="todo", priority="high")
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)

    assert issue.id is not None
    assert issue.title == "Test issue"
    assert issue.description == "A test"
    assert issue.status == "todo"
    assert issue.priority == "high"
    assert isinstance(issue.created_at, datetime)
    assert isinstance(issue.updated_at, datetime)


@pytest.mark.asyncio
async def test_issue_defaults_applied_in_db(db_session: AsyncSession):
    issue = Issue(title="Defaults test")
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)

    assert issue.status == "todo"
    assert issue.priority == "medium"
    assert issue.created_at is not None
    assert issue.updated_at is not None
