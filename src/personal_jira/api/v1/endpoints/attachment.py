import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_db
from personal_jira.schemas.attachment import AttachmentResponse
from personal_jira.services.attachment import AttachmentService, StorageService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/{issue_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    issue_id: uuid.UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
) -> AttachmentResponse:
    service = AttachmentService(db)
    try:
        attachment = await service.upload(issue_id, file)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    return AttachmentResponse.model_validate(attachment)


@router.get(
    "/{issue_id}/attachments",
    response_model=list[AttachmentResponse],
)
async def list_attachments(
    issue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[AttachmentResponse]:
    service = AttachmentService(db)
    attachments = await service.list_by_issue(issue_id)
    return [AttachmentResponse.model_validate(a) for a in attachments]


@router.get("/{issue_id}/attachments/{attachment_id}/download")
async def download_attachment(
    issue_id: uuid.UUID,
    attachment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    service = AttachmentService(db)
    attachment = await service.get(issue_id, attachment_id)
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="첨부파일을 찾을 수 없습니다",
        )
    try:
        content = await StorageService.read_file(attachment.storage_path)
    except FileNotFoundError:
        logger.error("Storage file missing: %s", attachment.storage_path)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="파일이 스토리지에 존재하지 않습니다",
        )
    return Response(
        content=content,
        media_type=attachment.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{attachment.filename}"'
        },
    )


@router.delete(
    "/{issue_id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_attachment(
    issue_id: uuid.UUID,
    attachment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    service = AttachmentService(db)
    deleted = await service.delete(issue_id, attachment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="첨부파일을 찾을 수 없습니다",
        )
