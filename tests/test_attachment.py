import uuid
from datetime import datetime, timezone
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile
from pydantic import ValidationError

from personal_jira.models.attachment import Attachment
from personal_jira.schemas.attachment import (
    AttachmentResponse,
    ALLOWED_CONTENT_TYPES,
    MAX_FILE_SIZE_BYTES,
)
from personal_jira.services.attachment import AttachmentService, StorageService


class TestAttachmentModel:
    def test_columns_exist(self) -> None:
        cols = {c.name for c in Attachment.__table__.columns}
        assert "id" in cols
        assert "issue_id" in cols
        assert "filename" in cols
        assert "content_type" in cols
        assert "file_size" in cols
        assert "storage_path" in cols
        assert "created_at" in cols

    def test_table_name(self) -> None:
        assert Attachment.__tablename__ == "attachments"

    def test_issue_id_not_nullable(self) -> None:
        col = Attachment.__table__.columns["issue_id"]
        assert col.nullable is False

    def test_filename_not_nullable(self) -> None:
        col = Attachment.__table__.columns["filename"]
        assert col.nullable is False

    def test_storage_path_not_nullable(self) -> None:
        col = Attachment.__table__.columns["storage_path"]
        assert col.nullable is False


class TestAttachmentSchema:
    def test_response_schema(self) -> None:
        now = datetime.now(timezone.utc)
        att_id = uuid.uuid4()
        issue_id = uuid.uuid4()
        resp = AttachmentResponse(
            id=att_id,
            issue_id=issue_id,
            filename="screenshot.png",
            content_type="image/png",
            file_size=1024,
            created_at=now,
        )
        assert resp.id == att_id
        assert resp.filename == "screenshot.png"
        assert resp.content_type == "image/png"
        assert resp.file_size == 1024

    def test_allowed_content_types(self) -> None:
        assert "image/png" in ALLOWED_CONTENT_TYPES
        assert "image/jpeg" in ALLOWED_CONTENT_TYPES
        assert "text/plain" in ALLOWED_CONTENT_TYPES
        assert "application/pdf" in ALLOWED_CONTENT_TYPES
        assert "application/zip" in ALLOWED_CONTENT_TYPES

    def test_max_file_size(self) -> None:
        assert MAX_FILE_SIZE_BYTES == 10 * 1024 * 1024


class TestStorageService:
    def test_generate_storage_path(self) -> None:
        issue_id = uuid.uuid4()
        path = StorageService.generate_storage_path(issue_id, "test.png")
        assert str(issue_id) in path
        assert path.endswith(".png")

    def test_generate_storage_path_preserves_extension(self) -> None:
        issue_id = uuid.uuid4()
        path = StorageService.generate_storage_path(issue_id, "log.txt")
        assert path.endswith(".txt")

    def test_generate_storage_path_no_extension(self) -> None:
        issue_id = uuid.uuid4()
        path = StorageService.generate_storage_path(issue_id, "noext")
        assert str(issue_id) in path


class TestAttachmentService:
    @pytest.fixture()
    def mock_db(self) -> AsyncMock:
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        return db

    @pytest.fixture()
    def service(self, mock_db: AsyncMock) -> AttachmentService:
        return AttachmentService(mock_db)

    @pytest.mark.asyncio
    async def test_validate_file_invalid_content_type(self, service: AttachmentService) -> None:
        file = MagicMock(spec=UploadFile)
        file.content_type = "application/exe"
        file.size = 100
        with pytest.raises(ValueError, match="허용되지 않는 파일 형식"):
            service.validate_file(file)

    @pytest.mark.asyncio
    async def test_validate_file_too_large(self, service: AttachmentService) -> None:
        file = MagicMock(spec=UploadFile)
        file.content_type = "image/png"
        file.size = MAX_FILE_SIZE_BYTES + 1
        with pytest.raises(ValueError, match="파일 크기 초과"):
            service.validate_file(file)

    @pytest.mark.asyncio
    async def test_validate_file_success(self, service: AttachmentService) -> None:
        file = MagicMock(spec=UploadFile)
        file.content_type = "image/png"
        file.size = 1024
        service.validate_file(file)

    @pytest.mark.asyncio
    async def test_validate_file_none_size_passes(self, service: AttachmentService) -> None:
        file = MagicMock(spec=UploadFile)
        file.content_type = "image/png"
        file.size = None
        service.validate_file(file)


class TestAttachmentEndpoint:
    @pytest.fixture()
    def mock_db(self) -> AsyncMock:
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        return db

    def test_upload_endpoint_exists(self) -> None:
        from personal_jira.api.v1.endpoints.attachment import router
        routes = [r.path for r in router.routes]
        assert "/{issue_id}/attachments" in routes

    def test_list_endpoint_exists(self) -> None:
        from personal_jira.api.v1.endpoints.attachment import router
        routes = [r.path for r in router.routes]
        assert "/{issue_id}/attachments" in routes

    def test_download_endpoint_exists(self) -> None:
        from personal_jira.api.v1.endpoints.attachment import router
        routes = [r.path for r in router.routes]
        assert "/{issue_id}/attachments/{attachment_id}/download" in routes

    def test_delete_endpoint_exists(self) -> None:
        from personal_jira.api.v1.endpoints.attachment import router
        routes = [r.path for r in router.routes]
        assert "/{issue_id}/attachments/{attachment_id}" in routes
