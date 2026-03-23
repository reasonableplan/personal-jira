from dataclasses import dataclass
from typing import Any

from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.schemas.issue_search import IssueSearchParams, UNASSIGNED_SENTINEL


@dataclass
class SearchResult:
    items: list[Issue]
    total: int
    offset: int
    limit: int


class IssueSearchService:
    def search(self, db: Session, params: IssueSearchParams) -> SearchResult:
        query = db.query(Issue).filter(Issue.deleted_at.is_(None))
        query = self._apply_filters(query, params)
        total = query.count()
        query = self._apply_sorting(query, params)
        query = query.offset(params.offset).limit(params.limit)
        return SearchResult(
            items=query.all(),
            total=total,
            offset=params.offset,
            limit=params.limit,
        )

    def _apply_filters(self, query: Any, params: IssueSearchParams) -> Any:
        if params.status:
            query = query.filter(Issue.status.in_(params.status))
        if params.priority:
            query = query.filter(Issue.priority.in_(params.priority))
        if params.issue_type:
            query = query.filter(Issue.issue_type == params.issue_type)
        if params.assignee:
            if params.assignee == UNASSIGNED_SENTINEL:
                query = query.filter(Issue.assignee.is_(None))
            else:
                query = query.filter(Issue.assignee == params.assignee)
        if params.label:
            for lbl in params.label:
                query = query.filter(Issue.labels.any(lbl))
        if params.q:
            pattern = f"%{params.q}%"
            query = query.filter(
                or_(
                    Issue.title.ilike(pattern),
                    Issue.description.ilike(pattern),
                )
            )
        return query

    def _apply_sorting(self, query: Any, params: IssueSearchParams) -> Any:
        column = getattr(Issue, params.sort_by)
        if params.sort_order == "desc":
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())
        return query
