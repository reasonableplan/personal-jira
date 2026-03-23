import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.dependencies import get_session
from personal_jira.schemas.attachment import AttachmentResponse
from personal_jira.services.attachment import AttachmentService, FileTooLargeError

router = APIRouter(tags=["attachments"])


def _to_response(att: "Attachment") -> dict:  # type: ignore[name-defined]
    return {
        "id": str(att.id),
        "issue_id": str(att.issue_id),
        "filename": att.filename,
        "content_type": att.content_type,
        "size_bytes": att.size_bytes,
        "created_at": str(att.created_at),
    }


@router.post(
    "/api/v1/issues/{issue_id}/attachments",
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    issue_id: uuid.UUID,
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> dict:
    svc = AttachmentService(session)
    data = await file.read()
    try:
        att = await svc.upload(
            issue_id=issue_id,
            filename=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
            data=data,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Issue not found")
    except FileTooLargeError:
        raise HTTPException(status_code=413, detail="File too large")
    return _to_response(att)


@router.get("/api/v1/issues/{issue_id}/attachments", response_model=list[AttachmentResponse])
async def list_attachments(
    issue_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> list[dict]:
    svc = AttachmentService(session)
    attachments = await svc.list_by_issue(issue_id)
    return [_to_response(a) for a in attachments]


@router.delete("/api/v1/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> None:
    svc = AttachmentService(session)
    deleted = await svc.delete(attachment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Attachment not found")


@router.get("/api/v1/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> Response:
    svc = AttachmentService(session)
    result = await svc.read_content(attachment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Attachment not found")
    data, content_type, filename = result
    return Response(
        content=data,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
