from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from personal_jira.exceptions import IssueNotFoundError
from personal_jira.models.issue import Issue


class AssignService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def assign(self, issue_id: uuid.UUID, assignee_id: Optional[uuid.UUID]) -> Issue:
        issue = (
            self._db.query(Issue)
            .filter(Issue.id == issue_id)
            .first()
        )
        if issue is None:
            raise IssueNotFoundError(issue_id)

        issue.assignee_id = assignee_id
        self._db.commit()
        self._db.refresh(issue)
        return issue
