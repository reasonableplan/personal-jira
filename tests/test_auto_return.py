import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from personal_jira.models.issue import IssueStatus
from personal_jira.services.auto_return import (
    AUTO_RETURN_TIMEOUT_MINUTES,
    AutoReturnService,
)


class TestAutoReturnConstants:
    def test_timeout_is_positive(self) -> None:
        assert AUTO_RETURN_TIMEOUT_MINUTES > 0

    def test_timeout_default(self) -> None:
        assert AUTO_RETURN_TIMEOUT_MINUTES == 30


class TestAutoReturnService:
    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        return db

    @pytest.fixture
    def service(self) -> AutoReturnService:
        return AutoReturnService()

    @pytest.mark.asyncio
    async def test_returns_stale_in_progress_issues(
        self, service: AutoReturnService, mock_db: AsyncMock
    ) -> None:
        stale_issue = MagicMock()
        stale_issue.id = uuid.uuid4()
        stale_issue.status = IssueStatus.IN_PROGRESS
        stale_issue.assignee_id = uuid.uuid4()
        stale_issue.started_at = datetime.now(timezone.utc) - timedelta(minutes=60)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [stale_issue]
        mock_db.execute.return_value = mock_result

        returned = await service.return_stale_issues(mock_db)

        assert len(returned) == 1
        assert stale_issue.status == IssueStatus.READY
        assert stale_issue.assignee_id is None
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_stale_issues(
        self, service: AutoReturnService, mock_db: AsyncMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        returned = await service.return_stale_issues(mock_db)

        assert len(returned) == 0
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_does_not_return_recent_issues(
        self, service: AutoReturnService, mock_db: AsyncMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        returned = await service.return_stale_issues(mock_db)
        assert len(returned) == 0

    @pytest.mark.asyncio
    async def test_clears_assignee_and_started_at(
        self, service: AutoReturnService, mock_db: AsyncMock
    ) -> None:
        stale_issue = MagicMock()
        stale_issue.id = uuid.uuid4()
        stale_issue.status = IssueStatus.IN_PROGRESS
        stale_issue.assignee_id = uuid.uuid4()
        stale_issue.started_at = datetime.now(timezone.utc) - timedelta(minutes=60)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [stale_issue]
        mock_db.execute.return_value = mock_result

        await service.return_stale_issues(mock_db)

        assert stale_issue.assignee_id is None
        assert stale_issue.started_at is None

    @pytest.mark.asyncio
    async def test_multiple_stale_issues(
        self, service: AutoReturnService, mock_db: AsyncMock
    ) -> None:
        issues = []
        for _ in range(3):
            issue = MagicMock()
            issue.id = uuid.uuid4()
            issue.status = IssueStatus.IN_PROGRESS
            issue.assignee_id = uuid.uuid4()
            issue.started_at = datetime.now(timezone.utc) - timedelta(minutes=45)
            issues.append(issue)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = issues
        mock_db.execute.return_value = mock_result

        returned = await service.return_stale_issues(mock_db)

        assert len(returned) == 3
        for issue in issues:
            assert issue.status == IssueStatus.READY
            assert issue.assignee_id is None


class TestAutoReturnBackgroundTask:
    @pytest.mark.asyncio
    async def test_run_auto_return_task(self) -> None:
        from personal_jira.tasks.auto_return import run_auto_return_cycle

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        with patch(
            "personal_jira.tasks.auto_return.get_async_session"
        ) as mock_get_session:
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_db)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=False)
            await run_auto_return_cycle()
