from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from personal_jira.database import get_db
from personal_jira.schemas.label import LabelAddRequest, LabelListResponse, LabelRemoveRequest
from personal_jira.services.label import LabelService

router = APIRouter()


@router.post(
    "/issues/{issue_id}/labels",
    response_model=LabelListResponse,
    status_code=status.HTTP_200_OK,
)
def add_labels(
    issue_id: uuid.UUID,
    body: LabelAddRequest,
    db: Session = Depends(get_db),
) -> LabelListResponse:
    service = LabelService(db)
    result = service.add_labels(issue_id, body.labels)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return LabelListResponse(labels=result, count=len(result))


@router.delete(
    "/issues/{issue_id}/labels",
    response_model=LabelListResponse,
    status_code=status.HTTP_200_OK,
)
def remove_labels(
    issue_id: uuid.UUID,
    body: LabelRemoveRequest,
    db: Session = Depends(get_db),
) -> LabelListResponse:
    service = LabelService(db)
    result = service.remove_labels(issue_id, body.labels)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return LabelListResponse(labels=result, count=len(result))


@router.get(
    "/issues/{issue_id}/labels",
    response_model=LabelListResponse,
    status_code=status.HTTP_200_OK,
)
def get_labels(
    issue_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> LabelListResponse:
    service = LabelService(db)
    result = service.get_labels(issue_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return LabelListResponse(labels=result, count=len(result))


@router.get(
    "/labels",
    response_model=LabelListResponse,
    status_code=status.HTTP_200_OK,
)
def get_all_labels(
    db: Session = Depends(get_db),
) -> LabelListResponse:
    service = LabelService(db)
    result = service.get_all_labels()
    return LabelListResponse(labels=result, count=len(result))
