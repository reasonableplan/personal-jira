import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from personal_jira.models.dependency import IssueDependency
from personal_jira.models.issue import Issue, IssueStatus
from tests.conftest import create_issue


class TestIssueDependencyModel:
    def test_create_dependency(self, db: Session) -> None:
        issue_a = create_issue(db, "Issue A")
        issue_b = create_issue(db, "Issue B")

        dep = IssueDependency(
            blocked_issue_id=issue_a.id,
            blocker_issue_id=issue_b.id,
        )
        db.add(dep)
        db.commit()
        db.refresh(dep)

        assert dep.id is not None
        assert dep.blocked_issue_id == issue_a.id
        assert dep.blocker_issue_id == issue_b.id
        assert dep.created_at is not None

    def test_unique_constraint_prevents_duplicate(self, db: Session) -> None:
        issue_a = create_issue(db, "Issue A")
        issue_b = create_issue(db, "Issue B")

        dep1 = IssueDependency(blocked_issue_id=issue_a.id, blocker_issue_id=issue_b.id)
        db.add(dep1)
        db.commit()

        dep2 = IssueDependency(blocked_issue_id=issue_a.id, blocker_issue_id=issue_b.id)
        db.add(dep2)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_check_constraint_prevents_self_dependency(self, db: Session) -> None:
        issue = create_issue(db, "Self Issue")

        dep = IssueDependency(blocked_issue_id=issue.id, blocker_issue_id=issue.id)
        db.add(dep)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_cascade_delete_on_blocked_issue(self, db: Session) -> None:
        issue_a = create_issue(db, "Issue A")
        issue_b = create_issue(db, "Issue B")

        dep = IssueDependency(blocked_issue_id=issue_a.id, blocker_issue_id=issue_b.id)
        db.add(dep)
        db.commit()

        db.delete(issue_a)
        db.commit()

        remaining = db.query(IssueDependency).all()
        assert len(remaining) == 0

    def test_cascade_delete_on_blocker_issue(self, db: Session) -> None:
        issue_a = create_issue(db, "Issue A")
        issue_b = create_issue(db, "Issue B")

        dep = IssueDependency(blocked_issue_id=issue_a.id, blocker_issue_id=issue_b.id)
        db.add(dep)
        db.commit()

        db.delete(issue_b)
        db.commit()

        remaining = db.query(IssueDependency).all()
        assert len(remaining) == 0

    def test_relationship_access(self, db: Session) -> None:
        issue_a = create_issue(db, "Blocked")
        issue_b = create_issue(db, "Blocker")

        dep = IssueDependency(blocked_issue_id=issue_a.id, blocker_issue_id=issue_b.id)
        db.add(dep)
        db.commit()
        db.refresh(dep)

        assert dep.blocked_issue.title == "Blocked"
        assert dep.blocker_issue.title == "Blocker"
