import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.core.database import get_db
from personal_jira.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from personal_jira.services.comment_service import CommentService

router = APIRouter()


@router.post(
    "/issues/{issue_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    issue_id: uuid.UUID, data: CommentCreate, db: AsyncSession = Depends(get_db)
) -> CommentResponse:
    service = CommentService(db)
    comment = await service.create_comment(issue_id, data)
    return CommentResponse.model_validate(comment)


@router.get("/issues/{issue_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    issue_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> Sequence[CommentResponse]:
    service = CommentService(db)
    comments = await service.list_comments(issue_id)
    return [CommentResponse.model_validate(c) for c in comments]


@router.patch(
    "/issues/{issue_id}/comments/{comment_id}", response_model=CommentResponse
)
async def update_comment(
    issue_id: uuid.UUID,
    comment_id: uuid.UUID,
    data: CommentUpdate,
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    service = CommentService(db)
    comment = await service.update_comment(issue_id, comment_id, data)
    return CommentResponse.model_validate(comment)


@router.delete(
    "/issues/{issue_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_comment(
    issue_id: uuid.UUID, comment_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    service = CommentService(db)
    await service.delete_comment(issue_id, comment_id)
