import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.personal_jira.database import get_db
from src.personal_jira.schemas.retry import RetryRequest, RetryResponse
from src.personal_jira.services.retry import RetryService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/issues/{issue_id}/retry", response_model=RetryResponse)
def retry_issue(
    issue_id: uuid.UUID,
    body: RetryRequest | None = None,
    db: Session = Depends(get_db),
) -> RetryResponse:
    service = RetryService(db)
    last_error = body.last_error if body else None

    try:
        issue = service.retry_issue(issue_id, last_error=last_error)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error retrying issue %s: %s", issue_id, e)
        raise HTTPException(status_code=500, detail="Internal server error")

    return RetryResponse.model_validate(issue)
