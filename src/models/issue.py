# Shim: re-export from canonical location
from personal_jira.models.issue import Issue, IssueStatus, IssueType, IssuePriority  # noqa: F401

__all__ = ["Issue", "IssueStatus", "IssueType", "IssuePriority"]
