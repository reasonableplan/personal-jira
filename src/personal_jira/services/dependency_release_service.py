import uuid

from sqlalchemy.orm import Session

from personal_jira.models.dependency import IssueDependency
from personal_jira.models.issue import Issue, IssueStatus


class DependencyReleaseService:
    @staticmethod
    def handle_issue_done(db: Session, *, blocker_id: uuid.UUID) -> list[Issue]:
        blocked_deps = (
            db.query(IssueDependency)
            .filter_by(blocker_issue_id=blocker_id)
            .all()
        )

        released: list[Issue] = []
        for dep in blocked_deps:
            blocked_issue = db.get(Issue, dep.blocked_issue_id)
            if not blocked_issue or blocked_issue.status != IssueStatus.BACKLOG:
                continue

            if DependencyReleaseService._all_blockers_done(db, blocked_issue.id):
                blocked_issue.status = IssueStatus.READY
                released.append(blocked_issue)

        if released:
            db.commit()
            for issue in released:
                db.refresh(issue)

        return released

    @staticmethod
    def _all_blockers_done(db: Session, issue_id: uuid.UUID) -> bool:
        blockers = (
            db.query(IssueDependency)
            .filter_by(blocked_issue_id=issue_id)
            .all()
        )
        for dep in blockers:
            blocker = db.get(Issue, dep.blocker_issue_id)
            if not blocker or blocker.status != IssueStatus.DONE:
                return False
        return True
