import os
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.config import MAX_FILE_SIZE_BYTES, UPLOAD_DIR
from personal_jira.models.attachment import Attachment
from personal_jira.models.issue import Issue


class FileTooLargeError(Exception):
    pass


class StorageService:
    """Static helper for reading files from storage."""

    @staticmethod
    async def read_file(storage_path: str) -> bytes:
        if not os.path.exists(storage_path):
            raise FileNotFoundError(f"File not found: {storage_path}")
        with open(storage_path, "rb") as f:
            return f.read()


class AttachmentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upload(
        self, issue_id: uuid.UUID, filename: str, content_type: str, data: bytes
    ) -> Attachment:
        issue = await self._session.get(Issue, issue_id)
        if not issue:
            raise FileNotFoundError(f"Issue {issue_id} not found")

        if len(data) > MAX_FILE_SIZE_BYTES:
            raise FileTooLargeError(f"File exceeds max size of {MAX_FILE_SIZE_BYTES} bytes")

        storage_name = f"{uuid.uuid4()}_{filename}"
        storage_path = os.path.join(UPLOAD_DIR, storage_name)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(storage_path, "wb") as f:
            f.write(data)

        attachment = Attachment(
            issue_id=issue_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            storage_path=storage_path,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._session.add(attachment)
        await self._session.commit()
        await self._session.refresh(attachment)
        return attachment

    async def list_by_issue(self, issue_id: uuid.UUID) -> list[Attachment]:
        result = await self._session.execute(
            select(Attachment).where(Attachment.issue_id == issue_id)
        )
        return list(result.scalars().all())

    async def get(self, attachment_id: uuid.UUID) -> Attachment | None:
        return await self._session.get(Attachment, attachment_id)

    async def delete(self, attachment_id: uuid.UUID) -> bool:
        attachment = await self._session.get(Attachment, attachment_id)
        if not attachment:
            return False
        if os.path.exists(attachment.storage_path):
            os.remove(attachment.storage_path)
        await self._session.delete(attachment)
        await self._session.commit()
        return True

    async def read_content(self, attachment_id: uuid.UUID) -> tuple[bytes, str, str] | None:
        attachment = await self._session.get(Attachment, attachment_id)
        if not attachment:
            return None
        if not os.path.exists(attachment.storage_path):
            return None
        with open(attachment.storage_path, "rb") as f:
            data = f.read()
        return data, attachment.content_type, attachment.filename
