from sqlalchemy.orm import Session

from personal_jira.models.issue import Issue, IssueStatus
from personal_jira.services.dependency_release_service import DependencyReleaseService
from personal_jira.services.dependency_service import DependencyService
from tests.conftest import create_issue


class TestDependencyRelease:
    def test_no_dependencies_no_change(self, db: Session) -> None:
        blocker = create_issue(db, "Blocker", IssueStatus.DONE)

        released = DependencyReleaseService.handle_issue_done(db, blocker_id=blocker.id)
        assert released == []

    def test_single_blocker_done_transitions_to_ready(self, db: Session) -> None:
        blocker = create_issue(db, "Blocker", IssueStatus.DONE)
        blocked = create_issue(db, "Blocked", IssueStatus.BACKLOG)

        DependencyService.create(db, blocked_issue_id=blocked.id, blocker_issue_id=blocker.id)

        released = DependencyReleaseService.handle_issue_done(db, blocker_id=blocker.id)

        db.refresh(blocked)
        assert blocked.status == IssueStatus.READY
        assert len(released) == 1
        assert released[0].id == blocked.id

    def test_partial_blockers_done_no_transition(self, db: Session) -> None:
        blocker1 = create_issue(db, "Blocker1", IssueStatus.DONE)
        blocker2 = create_issue(db, "Blocker2", IssueStatus.IN_PROGRESS)
        blocked = create_issue(db, "Blocked", IssueStatus.BACKLOG)

        DependencyService.create(db, blocked_issue_id=blocked.id, blocker_issue_id=blocker1.id)
        DependencyService.create(db, blocked_issue_id=blocked.id, blocker_issue_id=blocker2.id)

        released = DependencyReleaseService.handle_issue_done(db, blocker_id=blocker1.id)

        db.refresh(blocked)
        assert blocked.status == IssueStatus.BACKLOG
        assert released == []

    def test_all_blockers_done_transitions_to_ready(self, db: Session) -> None:
        blocker1 = create_issue(db, "Blocker1", IssueStatus.DONE)
        blocker2 = create_issue(db, "Blocker2", IssueStatus.DONE)
        blocked = create_issue(db, "Blocked", IssueStatus.BACKLOG)

        DependencyService.create(db, blocked_issue_id=blocked.id, blocker_issue_id=blocker1.id)
        DependencyService.create(db, blocked_issue_id=blocked.id, blocker_issue_id=blocker2.id)

        released = DependencyReleaseService.handle_issue_done(db, blocker_id=blocker1.id)

        db.refresh(blocked)
        assert blocked.status == IssueStatus.READY
        assert len(released) == 1

    def test_non_backlog_issue_not_transitioned(self, db: Session) -> None:
        blocker = create_issue(db, "Blocker", IssueStatus.DONE)
        blocked = create_issue(db, "Blocked", IssueStatus.IN_PROGRESS)

        DependencyService.create(db, blocked_issue_id=blocked.id, blocker_issue_id=blocker.id)

        released = DependencyReleaseService.handle_issue_done(db, blocker_id=blocker.id)

        db.refresh(blocked)
        assert blocked.status == IssueStatus.IN_PROGRESS
        assert released == []

    def test_multiple_blocked_issues_released(self, db: Session) -> None:
        blocker = create_issue(db, "Blocker", IssueStatus.DONE)
        blocked1 = create_issue(db, "Blocked1", IssueStatus.BACKLOG)
        blocked2 = create_issue(db, "Blocked2", IssueStatus.BACKLOG)

        DependencyService.create(db, blocked_issue_id=blocked1.id, blocker_issue_id=blocker.id)
        DependencyService.create(db, blocked_issue_id=blocked2.id, blocker_issue_id=blocker.id)

        released = DependencyReleaseService.handle_issue_done(db, blocker_id=blocker.id)

        db.refresh(blocked1)
        db.refresh(blocked2)
        assert blocked1.status == IssueStatus.READY
        assert blocked2.status == IssueStatus.READY
        assert len(released) == 2
