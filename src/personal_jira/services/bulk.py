from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from personal_jira.models.issue import Issue
from personal_jira.schemas.bulk import (
    BulkUpdateItem,
    BulkUpdateResponse,
    BulkUpdateResultItem,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_UPDATABLE_FIELDS = {"status", "assignee", "labels", "priority"}


class BulkUpdateService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def bulk_update(self, items: list[BulkUpdateItem]) -> BulkUpdateResponse:
        results: list[BulkUpdateResultItem] = []
        succeeded = 0
        failed = 0

        for item in items:
            issue = self._db.query(Issue).filter(Issue.id == item.id).first()

            if issue is None:
                results.append(BulkUpdateResultItem(id=item.id, success=False, error="Issue not found"))
                failed += 1
                continue

            if getattr(issue, "deleted_at", None) is not None:
                results.append(BulkUpdateResultItem(id=item.id, success=False, error="Issue is deleted"))
                failed += 1
                continue

            for field in _UPDATABLE_FIELDS:
                value = getattr(item, field)
                if value is not None:
                    setattr(issue, field, value)

            results.append(BulkUpdateResultItem(id=item.id, success=True))
            succeeded += 1

        try:
            self._db.commit()
        except Exception:
            self._db.rollback()
            logger.exception("Bulk update commit failed")
            raise

        return BulkUpdateResponse(
            total=len(items),
            succeeded=succeeded,
            failed=failed,
            results=results,
        )
