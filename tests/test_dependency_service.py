import uuid

import pytest
from sqlalchemy.orm import Session

from personal_jira.exceptions import (
    CircularDependencyError,
    DependencyNotFoundError,
    DuplicateDependencyError,
    IssueNotFoundError,
    SelfDependencyError,
)
from personal_jira.models.dependency import IssueDependency
from personal_jira.models.issue import Issue, IssueStatus
from personal_jira.services.dependency_service import DependencyService
from tests.conftest import create_issue


class TestDependencyServiceCreate:
    def test_create_dependency(self, db: Session) -> None:
        issue_a = create_issue(db, "Blocked")
        issue_b = create_issue(db, "Blocker")

        dep = DependencyService.create(db, blocked_issue_id=issue_a.id, blocker_issue_id=issue_b.id)

        assert dep.blocked_issue_id == issue_a.id
        assert dep.blocker_issue_id == issue_b.id

    def test_create_self_dependency_raises(self, db: Session) -> None:
        issue = create_issue(db, "Self")

        with pytest.raises(SelfDependencyError):
            DependencyService.create(db, blocked_issue_id=issue.id, blocker_issue_id=issue.id)

    def test_create_duplicate_raises(self, db: Session) -> None:
        issue_a = create_issue(db, "A")
        issue_b = create_issue(db, "B")

        DependencyService.create(db, blocked_issue_id=issue_a.id, blocker_issue_id=issue_b.id)

        with pytest.raises(DuplicateDependencyError):
            DependencyService.create(db, blocked_issue_id=issue_a.id, blocker_issue_id=issue_b.id)

    def test_create_with_nonexistent_blocked_issue_raises(self, db: Session) -> None:
        issue_b = create_issue(db, "Blocker")
        fake_id = uuid.uuid4()

        with pytest.raises(IssueNotFoundError):
            DependencyService.create(db, blocked_issue_id=fake_id, blocker_issue_id=issue_b.id)

    def test_create_with_nonexistent_blocker_issue_raises(self, db: Session) -> None:
        issue_a = create_issue(db, "Blocked")
        fake_id = uuid.uuid4()

        with pytest.raises(IssueNotFoundError):
            DependencyService.create(db, blocked_issue_id=issue_a.id, blocker_issue_id=fake_id)

    def test_circular_dependency_direct(self, db: Session) -> None:
        issue_a = create_issue(db, "A")
        issue_b = create_issue(db, "B")

        DependencyService.create(db, blocked_issue_id=issue_a.id, blocker_issue_id=issue_b.id)

        with pytest.raises(CircularDependencyError):
            DependencyService.create(db, blocked_issue_id=issue_b.id, blocker_issue_id=issue_a.id)

    def test_circular_dependency_transitive(self, db: Session) -> None:
        issue_a = create_issue(db, "A")
        issue_b = create_issue(db, "B")
        issue_c = create_issue(db, "C")

        DependencyService.create(db, blocked_issue_id=issue_a.id, blocker_issue_id=issue_b.id)
        DependencyService.create(db, blocked_issue_id=issue_b.id, blocker_issue_id=issue_c.id)

        with pytest.raises(CircularDependencyError):
            DependencyService.create(db, blocked_issue_id=issue_c.id, blocker_issue_id=issue_a.id)


class TestDependencyServiceGet:
    def test_get_blockers(self, db: Session) -> None:
        issue_a = create_issue(db, "Blocked")
        issue_b = create_issue(db, "Blocker1")
        issue_c = create_issue(db, "Blocker2")

        DependencyService.create(db, blocked_issue_id=issue_a.id, blocker_issue_id=issue_b.id)
        DependencyService.create(db, blocked_issue_id=issue_a.id, blocker_issue_id=issue_c.id)

        deps = DependencyService.get_blockers(db, issue_id=issue_a.id)
        blocker_ids = {d.blocker_issue_id for d in deps}
        assert blocker_ids == {issue_b.id, issue_c.id}

    def test_get_blocked_by(self, db: Session) -> None:
        issue_a = create_issue(db, "Blocker")
        issue_b = create_issue(db, "Blocked1")
        issue_c = create_issue(db, "Blocked2")

        DependencyService.create(db, blocked_issue_id=issue_b.id, blocker_issue_id=issue_a.id)
        DependencyService.create(db, blocked_issue_id=issue_c.id, blocker_issue_id=issue_a.id)

        deps = DependencyService.get_blocked_by(db, issue_id=issue_a.id)
        blocked_ids = {d.blocked_issue_id for d in deps}
        assert blocked_ids == {issue_b.id, issue_c.id}

    def test_get_blockers_empty(self, db: Session) -> None:
        issue = create_issue(db, "Alone")
        deps = DependencyService.get_blockers(db, issue_id=issue.id)
        assert deps == []


class TestDependencyServiceDelete:
    def test_delete_dependency(self, db: Session) -> None:
        issue_a = create_issue(db, "Blocked")
        issue_b = create_issue(db, "Blocker")

        dep = DependencyService.create(db, blocked_issue_id=issue_a.id, blocker_issue_id=issue_b.id)
        DependencyService.delete(db, dependency_id=dep.id)

        remaining = db.query(IssueDependency).all()
        assert len(remaining) == 0

    def test_delete_nonexistent_raises(self, db: Session) -> None:
        fake_id = uuid.uuid4()
        with pytest.raises(DependencyNotFoundError):
            DependencyService.delete(db, dependency_id=fake_id)
