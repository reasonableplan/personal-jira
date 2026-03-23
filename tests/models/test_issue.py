import enum
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from personal_jira.models.base import Base
from personal_jira.models.issue import Issue
from personal_jira.models.issue_type import IssueType
from personal_jira.models.issue_status import IssueStatus
from personal_jira.models.issue_priority import IssuePriority


@pytest.fixture(scope="module")
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s
        s.rollback()


class TestIssueTypeEnum:
    def test_values(self):
        assert IssueType.EPIC.value == "epic"
        assert IssueType.STORY.value == "story"
        assert IssueType.TASK.value == "task"
        assert IssueType.BUG.value == "bug"
        assert IssueType.SUB_TASK.value == "sub_task"

    def test_is_str_enum(self):
        assert isinstance(IssueType.EPIC, str)
        assert issubclass(IssueType, enum.Enum)

    def test_member_count(self):
        assert len(IssueType) == 5


class TestIssueStatusEnum:
    def test_values(self):
        assert IssueStatus.BACKLOG.value == "backlog"
        assert IssueStatus.READY.value == "ready"
        assert IssueStatus.IN_PROGRESS.value == "in_progress"
        assert IssueStatus.IN_REVIEW.value == "in_review"
        assert IssueStatus.DONE.value == "done"
        assert IssueStatus.CLOSED.value == "closed"
        assert IssueStatus.CANCELLED.value == "cancelled"

    def test_is_str_enum(self):
        assert isinstance(IssueStatus.BACKLOG, str)
        assert issubclass(IssueStatus, enum.Enum)

    def test_member_count(self):
        assert len(IssueStatus) == 7


class TestIssuePriorityEnum:
    def test_values(self):
        assert IssuePriority.CRITICAL.value == "critical"
        assert IssuePriority.HIGH.value == "high"
        assert IssuePriority.MEDIUM.value == "medium"
        assert IssuePriority.LOW.value == "low"
        assert IssuePriority.TRIVIAL.value == "trivial"

    def test_is_str_enum(self):
        assert isinstance(IssuePriority.CRITICAL, str)
        assert issubclass(IssuePriority, enum.Enum)

    def test_member_count(self):
        assert len(IssuePriority) == 5


class TestIssueModel:
    def test_tablename(self):
        assert Issue.__tablename__ == "issues"

    def test_columns_exist(self):
        mapper = inspect(Issue)
        column_names = {c.key for c in mapper.columns}
        expected = {
            "id", "title", "description", "issue_type", "status",
            "priority", "assignee", "parent_id",
            "labels", "required_skills", "context_bundle",
            "created_at", "updated_at",
        }
        assert expected.issubset(column_names)

    def test_primary_key(self):
        mapper = inspect(Issue)
        pk_cols = [c.name for c in mapper.primary_key]
        assert pk_cols == ["id"]

    def test_parent_id_foreign_key(self):
        mapper = inspect(Issue)
        parent_col = mapper.columns["parent_id"]
        fk_targets = {fk.target_fullname for fk in parent_col.foreign_keys}
        assert "issues.id" in fk_targets

    def test_nullable_constraints(self):
        mapper = inspect(Issue)
        assert not mapper.columns["title"].nullable
        assert not mapper.columns["issue_type"].nullable
        assert not mapper.columns["status"].nullable
        assert not mapper.columns["priority"].nullable
        assert mapper.columns["description"].nullable
        assert mapper.columns["assignee"].nullable
        assert mapper.columns["parent_id"].nullable

    def test_indexes(self):
        table = Issue.__table__
        index_names = {idx.name for idx in table.indexes}
        assert "ix_issues_status" in index_names
        assert "ix_issues_assignee" in index_names
        assert "ix_issues_priority" in index_names
        assert "ix_issues_parent_id" in index_names

    def test_default_values(self):
        mapper = inspect(Issue)
        status_col = mapper.columns["status"]
        priority_col = mapper.columns["priority"]
        assert status_col.default is not None
        assert priority_col.default is not None

    def test_create_issue(self, session: Session):
        issue = Issue(
            title="Test issue",
            issue_type=IssueType.TASK,
            status=IssueStatus.BACKLOG,
            priority=IssuePriority.MEDIUM,
        )
        session.add(issue)
        session.flush()
        assert issue.id is not None
        assert issue.title == "Test issue"
        assert issue.issue_type == IssueType.TASK
        assert issue.status == IssueStatus.BACKLOG
        assert issue.priority == IssuePriority.MEDIUM
        assert issue.created_at is not None
        assert issue.updated_at is not None

    def test_create_issue_with_all_fields(self, session: Session):
        parent = Issue(
            title="Parent",
            issue_type=IssueType.EPIC,
            status=IssueStatus.IN_PROGRESS,
            priority=IssuePriority.HIGH,
        )
        session.add(parent)
        session.flush()

        child = Issue(
            title="Child",
            description="A child issue",
            issue_type=IssueType.SUB_TASK,
            status=IssueStatus.READY,
            priority=IssuePriority.LOW,
            assignee="agent-backend",
            parent_id=parent.id,
            labels=["backend", "urgent"],
            required_skills=["python", "sqlalchemy"],
            context_bundle={"repo": "personal-jira", "branch": "main"},
        )
        session.add(child)
        session.flush()
        assert child.parent_id == parent.id
        assert child.assignee == "agent-backend"
        assert child.labels == ["backend", "urgent"]
        assert child.required_skills == ["python", "sqlalchemy"]
        assert child.context_bundle == {"repo": "personal-jira", "branch": "main"}

    def test_title_not_nullable(self, session: Session):
        issue = Issue(
            title=None,
            issue_type=IssueType.TASK,
            status=IssueStatus.BACKLOG,
            priority=IssuePriority.MEDIUM,
        )
        session.add(issue)
        with pytest.raises(Exception):
            session.flush()
