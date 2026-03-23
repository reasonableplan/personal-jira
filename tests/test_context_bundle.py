import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from personal_jira.models.context_bundle import ContextBundle, BundleItemType
from personal_jira.schemas.context_bundle import (
    BundleItemCreate,
    BundleItemResponse,
    ContextBundleCreate,
    ContextBundleResponse,
)
from personal_jira.services.context_bundle import ContextBundleService


class TestBundleItemType:
    def test_file_type(self) -> None:
        assert BundleItemType.FILE == "file"

    def test_spec_type(self) -> None:
        assert BundleItemType.SPEC == "spec"

    def test_snippet_type(self) -> None:
        assert BundleItemType.SNIPPET == "snippet"


class TestContextBundleModel:
    def test_create_bundle(self) -> None:
        issue_id = uuid.uuid4()
        bundle = ContextBundle(
            id=uuid.uuid4(),
            issue_id=issue_id,
            items=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        assert bundle.issue_id == issue_id
        assert bundle.items == []

    def test_bundle_requires_issue_id(self) -> None:
        with pytest.raises(Exception):
            ContextBundle(id=uuid.uuid4(), items=[])


class TestContextBundleSchema:
    def test_bundle_item_create_file(self) -> None:
        item = BundleItemCreate(
            item_type=BundleItemType.FILE,
            path="src/main.py",
            content=None,
        )
        assert item.item_type == BundleItemType.FILE
        assert item.path == "src/main.py"

    def test_bundle_item_create_snippet(self) -> None:
        item = BundleItemCreate(
            item_type=BundleItemType.SNIPPET,
            path="src/utils.py",
            content="def helper(): pass",
            line_start=10,
            line_end=15,
        )
        assert item.content == "def helper(): pass"
        assert item.line_start == 10

    def test_bundle_item_create_spec(self) -> None:
        item = BundleItemCreate(
            item_type=BundleItemType.SPEC,
            path=None,
            content="## Requirements\n- Feature A",
        )
        assert item.item_type == BundleItemType.SPEC

    def test_bundle_create_with_items(self) -> None:
        bundle = ContextBundleCreate(
            items=[
                BundleItemCreate(
                    item_type=BundleItemType.FILE,
                    path="README.md",
                ),
            ],
        )
        assert len(bundle.items) == 1

    def test_bundle_create_empty_items_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ContextBundleCreate(items=[])

    def test_bundle_response_serialization(self) -> None:
        now = datetime.now(timezone.utc)
        resp = ContextBundleResponse(
            id=uuid.uuid4(),
            issue_id=uuid.uuid4(),
            items=[
                BundleItemResponse(
                    id=uuid.uuid4(),
                    item_type=BundleItemType.FILE,
                    path="src/app.py",
                    content=None,
                    line_start=None,
                    line_end=None,
                ),
            ],
            created_at=now,
            updated_at=now,
        )
        assert len(resp.items) == 1


class TestContextBundleService:
    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        return db

    @pytest.fixture
    def service(self) -> ContextBundleService:
        return ContextBundleService()

    @pytest.mark.asyncio
    async def test_create_bundle(self, service: ContextBundleService, mock_db: AsyncMock) -> None:
        issue_id = uuid.uuid4()
        payload = ContextBundleCreate(
            items=[
                BundleItemCreate(
                    item_type=BundleItemType.FILE,
                    path="src/main.py",
                ),
            ],
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(id=issue_id)
        mock_db.execute.return_value = mock_result

        with patch.object(service, "_get_issue_or_404", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock(id=issue_id)
            mock_db.refresh = AsyncMock()
            result = await service.create_bundle(mock_db, issue_id, payload)

        assert result is not None

    @pytest.mark.asyncio
    async def test_get_bundle(self, service: ContextBundleService, mock_db: AsyncMock) -> None:
        issue_id = uuid.uuid4()
        bundle_id = uuid.uuid4()
        mock_bundle = MagicMock()
        mock_bundle.id = bundle_id
        mock_bundle.issue_id = issue_id
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_bundle
        mock_db.execute.return_value = mock_result

        result = await service.get_bundle(mock_db, issue_id, bundle_id)
        assert result.id == bundle_id

    @pytest.mark.asyncio
    async def test_get_bundle_not_found(self, service: ContextBundleService, mock_db: AsyncMock) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await service.get_bundle(mock_db, uuid.uuid4(), uuid.uuid4())
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_bundle(self, service: ContextBundleService, mock_db: AsyncMock) -> None:
        bundle_id = uuid.uuid4()
        mock_bundle = MagicMock()
        mock_bundle.id = bundle_id
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_bundle
        mock_db.execute.return_value = mock_result

        await service.delete_bundle(mock_db, uuid.uuid4(), bundle_id)
        mock_db.delete.assert_called_once_with(mock_bundle)

    @pytest.mark.asyncio
    async def test_list_bundles(self, service: ContextBundleService, mock_db: AsyncMock) -> None:
        mock_bundles = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_bundles
        mock_db.execute.return_value = mock_result

        result = await service.list_bundles(mock_db, uuid.uuid4())
        assert len(result) == 2
