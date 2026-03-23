from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from personal_jira.database import get_db
from personal_jira.schemas.bulk import BulkUpdateRequest, BulkUpdateResponse
from personal_jira.services.bulk import BulkUpdateService

router = APIRouter()


@router.patch("/bulk", response_model=BulkUpdateResponse)
def bulk_update_issues(
    body: BulkUpdateRequest,
    db: Session = Depends(get_db),
) -> BulkUpdateResponse:
    service = BulkUpdateService(db)
    return service.bulk_update(body.items)
