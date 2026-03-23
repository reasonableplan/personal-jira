import uuid

from personal_jira.models.issue import IssueStatus


class IssueNotFoundError(Exception):
    def __init__(self, issue_id: uuid.UUID) -> None:
        self.issue_id = issue_id
        super().__init__(f"Issue {issue_id} not found")


class IssueNotInReviewError(Exception):
    def __init__(self, issue_id: uuid.UUID, current_status: IssueStatus) -> None:
        self.issue_id = issue_id
        self.current_status = current_status
        super().__init__(
            f"Issue {issue_id} is in '{current_status.value}' status, expected 'in_review'"
        )


class InvalidReviewTransitionError(Exception):
    def __init__(self, issue_id: uuid.UUID, from_status: str, to_status: str) -> None:
        self.issue_id = issue_id
        super().__init__(
            f"Cannot transition issue {issue_id} from '{from_status}' to '{to_status}'"
        )
