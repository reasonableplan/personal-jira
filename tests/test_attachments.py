import uuid
from typing import Any
from io import BytesIO

import pytest
import pytest_asyncio
from httpx import AsyncClient

from personal_jira.models.attachment import Attachment
from personal_jira.schemas.attachment import AttachmentResponse
from personal_jira.services.attachment import AttachmentService


MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
API_PREFIX = "/api/v1/issues"


@pytest.mark.asyncio
class TestAttachmentModel:
    async def test_table_name(self) -> None:
        assert Attachment.__tablename__ == "attachments"

    async def test_required_columns(self) -> None:
        columns = {c.name for c in Attachment.__table__.columns}
        expected = {"id", "issue_id", "filename", "content_type", "size_bytes", "storage_path", "created_at"}
        assert expected.issubset(columns)

    async def test_issue_id_foreign_key(self) -> None:
        fks = {fk.target_fullname for c in Attachment.__table__.columns for fk in c.foreign_keys}
        assert "issues.id" in fks


@pytest.mark.asyncio
class TestAttachmentSchema:
    async def test_response_schema(self) -> None:
        resp = AttachmentResponse(
            id=uuid.uuid4(),
            issue_id=uuid.uuid4(),
            filename="report.pdf",
            content_type="application/pdf",
            size_bytes=1024,
            created_at="2026-01-01T00:00:00",
        )
        assert resp.filename == "report.pdf"
        assert resp.size_bytes == 1024


@pytest.mark.asyncio
class TestAttachmentAPI:
    async def test_upload_file(self, client: AsyncClient, sample_issue: dict[str, Any]) -> None:
        issue_id = sample_issue["id"]
        content = b"hello world"
        resp = await client.post(
            f"{API_PREFIX}/{issue_id}/attachments",
            files={"file": ("test.txt", BytesIO(content), "text/plain")},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["filename"] == "test.txt"
        assert body["content_type"] == "text/plain"
        assert body["size_bytes"] == len(content)
        assert body["issue_id"] == issue_id

    async def test_upload_to_nonexistent_issue(self, client: AsyncClient) -> None:
        resp = await client.post(
            f"{API_PREFIX}/{uuid.uuid4()}/attachments",
            files={"file": ("test.txt", BytesIO(b"data"), "text/plain")},
        )
        assert resp.status_code == 404

    async def test_upload_exceeds_max_size(self, client: AsyncClient, sample_issue: dict[str, Any]) -> None:
        issue_id = sample_issue["id"]
        large_content = b"x" * (MAX_FILE_SIZE_BYTES + 1)
        resp = await client.post(
            f"{API_PREFIX}/{issue_id}/attachments",
            files={"file": ("big.bin", BytesIO(large_content), "application/octet-stream")},
        )
        assert resp.status_code == 413

    async def test_list_attachments(self, client: AsyncClient, sample_issue: dict[str, Any]) -> None:
        issue_id = sample_issue["id"]
        await client.post(
            f"{API_PREFIX}/{issue_id}/attachments",
            files={"file": ("a.txt", BytesIO(b"aaa"), "text/plain")},
        )
        await client.post(
            f"{API_PREFIX}/{issue_id}/attachments",
            files={"file": ("b.txt", BytesIO(b"bbb"), "text/plain")},
        )
        resp = await client.get(f"{API_PREFIX}/{issue_id}/attachments")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_delete_attachment(self, client: AsyncClient, sample_issue: dict[str, Any]) -> None:
        issue_id = sample_issue["id"]
        upload = await client.post(
            f"{API_PREFIX}/{issue_id}/attachments",
            files={"file": ("del.txt", BytesIO(b"delete me"), "text/plain")},
        )
        att_id = upload.json()["id"]
        del_resp = await client.delete(f"/api/v1/attachments/{att_id}")
        assert del_resp.status_code == 204

    async def test_delete_attachment_not_found(self, client: AsyncClient) -> None:
        resp = await client.delete(f"/api/v1/attachments/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_download_attachment(self, client: AsyncClient, sample_issue: dict[str, Any]) -> None:
        issue_id = sample_issue["id"]
        content = b"download this"
        upload = await client.post(
            f"{API_PREFIX}/{issue_id}/attachments",
            files={"file": ("dl.txt", BytesIO(content), "text/plain")},
        )
        att_id = upload.json()["id"]
        resp = await client.get(f"/api/v1/attachments/{att_id}/download")
        assert resp.status_code == 200
        assert resp.content == content
        assert resp.headers["content-type"] == "text/plain"
