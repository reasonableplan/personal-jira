import logging
import uuid

from sqlalchemy.orm import Session

from src.personal_jira.constants import MAX_RETRY_COUNT
from src.personal_jira.models.issue import Issue, IssueStatus

logger = logging.getLogger(__name__)


class RetryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def retry_issue(self, issue_id: uuid.UUID, last_error: str | None) -> Issue:
        issue = self.db.get(Issue, issue_id)
        if issue is None:
            raise ValueError(f"Issue {issue_id} not found")

        issue.retry_count += 1

        if last_error is not None:
            issue.last_error = last_error

        if issue.retry_count >= MAX_RETRY_COUNT:
            issue.status = IssueStatus.ABANDONED
            logger.warning(
                "Issue %s exceeded max retry count (%d), status set to Abandoned",
                issue_id,
                MAX_RETRY_COUNT,
            )
        else:
            issue.status = IssueStatus.READY

        try:
            self.db.commit()
            self.db.refresh(issue)
        except Exception:
            self.db.rollback()
            logger.error("Failed to commit retry for issue %s", issue_id)
            raise

        return issue
