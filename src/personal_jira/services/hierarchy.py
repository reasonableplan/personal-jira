from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from personal_jira.models import Issue

MAX_ANCESTOR_DEPTH = 50


class HierarchyService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_children(self, issue_id: int) -> list[Issue]:
        issue = self._db.get(Issue, issue_id)
        if issue is None:
            raise ValueError(f"Issue {issue_id} not found")
        return (
            self._db.query(Issue)
            .filter(Issue.parent_id == issue_id)
            .order_by(Issue.id)
            .all()
        )

    def get_subtree(self, issue_id: int, max_depth: int | None = None) -> dict[str, Any]:
        issue = self._db.get(Issue, issue_id)
        if issue is None:
            raise ValueError(f"Issue {issue_id} not found")
        return self._build_node(issue, current_depth=0, max_depth=max_depth)

    def _build_node(
        self, issue: Issue, current_depth: int, max_depth: int | None
    ) -> dict[str, Any]:
        node: dict[str, Any] = {
            "id": issue.id,
            "title": issue.title,
            "issue_type": issue.issue_type,
            "status": issue.status,
            "priority": issue.priority,
            "children": [],
        }
        if max_depth is not None and current_depth >= max_depth:
            return node
        children = (
            self._db.query(Issue)
            .filter(Issue.parent_id == issue.id)
            .order_by(Issue.id)
            .all()
        )
        node["children"] = [
            self._build_node(child, current_depth + 1, max_depth)
            for child in children
        ]
        return node

    def get_ancestors(self, issue_id: int) -> list[Issue]:
        issue = self._db.get(Issue, issue_id)
        if issue is None:
            raise ValueError(f"Issue {issue_id} not found")
        ancestors: list[Issue] = []
        current = issue
        for _ in range(MAX_ANCESTOR_DEPTH):
            if current.parent_id is None:
                break
            parent = self._db.get(Issue, current.parent_id)
            if parent is None:
                break
            ancestors.append(parent)
            current = parent
        return ancestors
