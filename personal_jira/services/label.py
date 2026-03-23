from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from personal_jira.models.issue import Issue


class LabelService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _get_issue(self, issue_id: uuid.UUID) -> Optional[Issue]:
        return (
            self._db.query(Issue)
            .filter(Issue.id == issue_id, Issue.deleted_at.is_(None))
            .first()
        )

    def add_labels(self, issue_id: uuid.UUID, labels: list[str]) -> Optional[list[str]]:
        issue = self._get_issue(issue_id)
        if issue is None:
            return None
        existing = set(issue.labels or [])
        existing.update(labels)
        issue.labels = sorted(existing)
        self._db.commit()
        self._db.refresh(issue)
        return list(issue.labels)

    def remove_labels(self, issue_id: uuid.UUID, labels: list[str]) -> Optional[list[str]]:
        issue = self._get_issue(issue_id)
        if issue is None:
            return None
        to_remove = set(labels)
        issue.labels = [l for l in (issue.labels or []) if l not in to_remove]
        self._db.commit()
        self._db.refresh(issue)
        return list(issue.labels)

    def get_labels(self, issue_id: uuid.UUID) -> Optional[list[str]]:
        issue = self._get_issue(issue_id)
        if issue is None:
            return None
        return list(issue.labels or [])

    def get_all_labels(self) -> list[str]:
        issues = (
            self._db.query(Issue)
            .filter(Issue.deleted_at.is_(None), Issue.labels.isnot(None))
            .all()
        )
        all_labels: set[str] = set()
        for issue in issues:
            all_labels.update(issue.labels or [])
        return sorted(all_labels)
