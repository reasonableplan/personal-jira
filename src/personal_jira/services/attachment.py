import os
import uuid
from pathlib import Path
from typing import Sequence

import aiofiles
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.attachment import Attachment
from personal_jira.schemas.attachment import ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE_BYTES

STORAGE_BASE_DIR: str = os.getenv("ATTACHMENT_STORAGE_DIR", "data/attachments")


class StorageService:
    @staticmethod
    def generate_storage_path(issue_id: uuid.UUID, filename: str) -> str:
        ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4().hex}{ext}"
        return f"{issue_id}/{unique_name}"

    @staticmethod
    async def save_file(storage_path: str, content: bytes) -> str:
        full_path = Path(STORAGE_BASE_DIR) / storage_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(content)
        return str(full_path)

    @staticmethod
    async def read_file(storage_path: str) -> bytes:
        full_path = Path(STORAGE_BASE_DIR) / storage_path
        if not full_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {storage_path}")
        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    @staticmethod
    def delete_file(storage_path: str) -> None:
        full_path = Path(STORAGE_BASE_DIR) / storage_path
        if full_path.exists():
            full_path.unlink()


class AttachmentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def validate_file(self, file: UploadFile) -> None:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"허용되지 않는 파일 형식: {file.content_type}. "
                f"허용: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}"
            )
        if file.size is not None and file.size > MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"파일 크기 초과: {file.size} bytes. "
                f"최대: {MAX_FILE_SIZE_BYTES} bytes"
            )

    async def upload(
        self, issue_id: uuid.UUID, file: UploadFile
    ) -> Attachment:
        self.validate_file(file)
        content = await file.read()
        file_size = len(content)
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"파일 크기 초과: {file_size} bytes. "
                f"최대: {MAX_FILE_SIZE_BYTES} bytes"
            )
        storage_path = StorageService.generate_storage_path(
            issue_id, file.filename or "unknown"
        )
        await StorageService.save_file(storage_path, content)
        attachment = Attachment(
            issue_id=issue_id,
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            storage_path=storage_path,
        )
        self.db.add(attachment)
        await self.db.commit()
        await self.db.refresh(attachment)
        return attachment

    async def list_by_issue(
        self, issue_id: uuid.UUID
    ) -> Sequence[Attachment]:
        result = await self.db.execute(
            select(Attachment)
            .where(Attachment.issue_id == issue_id)
            .order_by(Attachment.created_at.desc())
        )
        return result.scalars().all()

    async def get(
        self, issue_id: uuid.UUID, attachment_id: uuid.UUID
    ) -> Attachment | None:
        result = await self.db.execute(
            select(Attachment).where(
                Attachment.id == attachment_id,
                Attachment.issue_id == issue_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete(
        self, issue_id: uuid.UUID, attachment_id: uuid.UUID
    ) -> bool:
        attachment = await self.get(issue_id, attachment_id)
        if attachment is None:
            return False
        StorageService.delete_file(attachment.storage_path)
        await self.db.delete(attachment)
        await self.db.commit()
        return True
