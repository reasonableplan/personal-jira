import uuid
from collections import deque

from sqlalchemy.orm import Session

from personal_jira.exceptions import (
    CircularDependencyError,
    DependencyNotFoundError,
    DuplicateDependencyError,
    IssueNotFoundError,
    SelfDependencyError,
)
from personal_jira.models.dependency import IssueDependency
from personal_jira.models.issue import Issue


class DependencyService:
    @staticmethod
    def create(
        db: Session,
        *,
        blocked_issue_id: uuid.UUID,
        blocker_issue_id: uuid.UUID,
    ) -> IssueDependency:
        if blocked_issue_id == blocker_issue_id:
            raise SelfDependencyError()

        blocked = db.get(Issue, blocked_issue_id)
        if not blocked:
            raise IssueNotFoundError(blocked_issue_id)

        blocker = db.get(Issue, blocker_issue_id)
        if not blocker:
            raise IssueNotFoundError(blocker_issue_id)

        existing = (
            db.query(IssueDependency)
            .filter_by(
                blocked_issue_id=blocked_issue_id,
                blocker_issue_id=blocker_issue_id,
            )
            .first()
        )
        if existing:
            raise DuplicateDependencyError()

        DependencyService._check_circular(db, blocked_issue_id, blocker_issue_id)

        dep = IssueDependency(
            blocked_issue_id=blocked_issue_id,
            blocker_issue_id=blocker_issue_id,
        )
        db.add(dep)
        db.commit()
        db.refresh(dep)
        return dep

    @staticmethod
    def get_blockers(db: Session, *, issue_id: uuid.UUID) -> list[IssueDependency]:
        return (
            db.query(IssueDependency)
            .filter_by(blocked_issue_id=issue_id)
            .all()
        )

    @staticmethod
    def get_blocked_by(db: Session, *, issue_id: uuid.UUID) -> list[IssueDependency]:
        return (
            db.query(IssueDependency)
            .filter_by(blocker_issue_id=issue_id)
            .all()
        )

    @staticmethod
    def delete(db: Session, *, dependency_id: uuid.UUID) -> None:
        dep = db.get(IssueDependency, dependency_id)
        if not dep:
            raise DependencyNotFoundError(dependency_id)
        db.delete(dep)
        db.commit()

    @staticmethod
    def _check_circular(
        db: Session,
        blocked_issue_id: uuid.UUID,
        blocker_issue_id: uuid.UUID,
    ) -> None:
        visited: set[uuid.UUID] = set()
        queue: deque[uuid.UUID] = deque([blocker_issue_id])
        parent: dict[uuid.UUID, uuid.UUID] = {}

        while queue:
            current = queue.popleft()
            if current == blocked_issue_id:
                cycle = DependencyService._reconstruct_cycle(
                    parent, blocked_issue_id, blocker_issue_id
                )
                raise CircularDependencyError(cycle)

            if current in visited:
                continue
            visited.add(current)

            deps = (
                db.query(IssueDependency)
                .filter_by(blocked_issue_id=current)
                .all()
            )
            for dep in deps:
                if dep.blocker_issue_id not in visited:
                    parent[dep.blocker_issue_id] = current
                    queue.append(dep.blocker_issue_id)

    @staticmethod
    def _reconstruct_cycle(
        parent: dict[uuid.UUID, uuid.UUID],
        start: uuid.UUID,
        end: uuid.UUID,
    ) -> list[uuid.UUID]:
        path = [start]
        current = end
        while current != start:
            path.append(current)
            current = parent.get(current, start)
        path.append(start)
        return path
