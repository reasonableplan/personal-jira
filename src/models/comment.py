# Shim: re-export from canonical location
from personal_jira.models.comment import Comment, CommentType  # noqa: F401

__all__ = ["Comment", "CommentType"]
