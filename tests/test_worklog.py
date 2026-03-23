import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from personal_jira.constants import WORKLOG_MAX_CONTENT_LENGTH
from personal_jira.models.worklog import WorkLog
from personal_jira.schemas.worklog import WorkLogCreate, WorkLogResponse
from personal_jira.services.worklog import WorkLogService


class TestWorkLogConstants:
    def test_max_content_length_defined(self) -> None:
        assert WORKLOG_MAX_CONTENT_LENGTH > 0

    def test_max_content_length_value(self) -> None:
        assert WORKLOG_MAX_CONTENT_LENGTH == 10000


class TestWorkLogModel:
    def test_table_name(self) -> None:
        assert WorkLog.__tablename__ == "work_logs"

    def test_has_id_column(self) -> None:
        columns = {c.name for c in WorkLog.__table__.columns}
        assert "id" in columns

    def test_has_issue_id_column(self) -> None:
        columns = {c.name for c in WorkLog.__table__.columns}
        assert "issue_id" in columns

    def test_has_agent_id_column(self) -> None:
        columns = {c.name for c in WorkLog.__table__.columns}
        assert "agent_id" in columns

    def test_has_llm_calls_column(self) -> None:
        columns = {c.name for c in WorkLog.__table__.columns}
        assert "llm_calls" in columns

    def test_has_tokens_used_column(self) -> None:
        columns = {c.name for c in WorkLog.__table__.columns}
        assert "tokens_used" in columns

    def test_has_content_column(self) -> None:
        columns = {c.name for c in WorkLog.__table__.columns}
        assert "content" in columns

    def test_has_created_at_column(self) -> None:
        columns = {c.name for c in WorkLog.__table__.columns}
        assert "created_at" in columns

    def test_has_updated_at_column(self) -> None:
        columns = {c.name for c in WorkLog.__table__.columns}
        assert "updated_at" in columns

    def test_issue_id_not_nullable(self) -> None:
        col = WorkLog.__table__.columns["issue_id"]
        assert col.nullable is False

    def test_llm_calls_default(self) -> None:
        col = WorkLog.__table__.columns["llm_calls"]
        assert col.default.arg == 0

    def test_tokens_used_default(self) -> None:
        col = WorkLog.__table__.columns["tokens_used"]
        assert col.default.arg == 0

    def test_issue_id_has_index(self) -> None:
        col = WorkLog.__table__.columns["issue_id"]
        assert col.index is True

    def test_agent_id_has_index(self) -> None:
        col = WorkLog.__table__.columns["agent_id"]
        assert col.index is True


class TestWorkLogCreateSchema:
    def test_valid_minimal(self) -> None:
        data = WorkLogCreate(llm_calls=1, tokens_used=100)
        assert data.llm_calls == 1
        assert data.tokens_used == 100
        assert data.content is None
        assert data.agent_id is None

    def test_valid_full(self) -> None:
        data = WorkLogCreate(
            llm_calls=5,
            tokens_used=2500,
            content="Attempted code generation with GPT-4",
            agent_id="agent-backend",
        )
        assert data.llm_calls == 5
        assert data.tokens_used == 2500
        assert data.content == "Attempted code generation with GPT-4"
        assert data.agent_id == "agent-backend"

    def test_llm_calls_required(self) -> None:
        with pytest.raises(ValidationError):
            WorkLogCreate(tokens_used=100)

    def test_tokens_used_required(self) -> None:
        with pytest.raises(ValidationError):
            WorkLogCreate(llm_calls=1)

    def test_llm_calls_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            WorkLogCreate(llm_calls=-1, tokens_used=100)

    def test_tokens_used_non_negative(self) -> None:
        with pytest.raises(ValidationError):
            WorkLogCreate(llm_calls=1, tokens_used=-1)

    def test_content_max_length(self) -> None:
        with pytest.raises(ValidationError):
            WorkLogCreate(
                llm_calls=1,
                tokens_used=100,
                content="x" * (WORKLOG_MAX_CONTENT_LENGTH + 1),
            )

    def test_content_at_max_length(self) -> None:
        data = WorkLogCreate(
            llm_calls=1,
            tokens_used=100,
            content="x" * WORKLOG_MAX_CONTENT_LENGTH,
        )
        assert len(data.content) == WORKLOG_MAX_CONTENT_LENGTH


class TestWorkLogResponseSchema:
    def test_from_attributes(self) -> None:
        assert WorkLogResponse.model_config.get("from_attributes") is True

    def test_fields(self) -> None:
        fields = set(WorkLogResponse.model_fields.keys())
        expected = {"id", "issue_id", "agent_id", "llm_calls", "tokens_used", "content", "created_at", "updated_at"}
        assert expected == fields


class TestWorkLogService:
    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.add = MagicMock()
        return db

    @pytest.fixture
    def service(self) -> WorkLogService:
        return WorkLogService()

    @pytest.fixture
    def issue_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_create_worklog(self, service: WorkLogService, mock_db: AsyncMock, issue_id: uuid.UUID) -> None:
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.deleted_at = None

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_issue
        mock_db.execute = AsyncMock(return_value=result_mock)

        data = WorkLogCreate(llm_calls=3, tokens_used=1500, content="test attempt")
        worklog = await service.create(mock_db, issue_id, data)

        assert worklog.issue_id == issue_id
        assert worklog.llm_calls == 3
        assert worklog.tokens_used == 1500
        assert worklog.content == "test attempt"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()
        mock_db.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_worklog_with_agent_id(self, service: WorkLogService, mock_db: AsyncMock, issue_id: uuid.UUID) -> None:
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.deleted_at = None

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_issue
        mock_db.execute = AsyncMock(return_value=result_mock)

        data = WorkLogCreate(llm_calls=1, tokens_used=500, agent_id="agent-backend")
        worklog = await service.create(mock_db, issue_id, data)

        assert worklog.agent_id == "agent-backend"

    @pytest.mark.asyncio
    async def test_create_worklog_issue_not_found(self, service: WorkLogService, mock_db: AsyncMock) -> None:
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result_mock)

        data = WorkLogCreate(llm_calls=1, tokens_used=100)
        with pytest.raises(ValueError, match="Issue not found"):
            await service.create(mock_db, uuid.uuid4(), data)

    @pytest.mark.asyncio
    async def test_create_worklog_deleted_issue(self, service: WorkLogService, mock_db: AsyncMock, issue_id: uuid.UUID) -> None:
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.deleted_at = datetime.utcnow()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_issue
        mock_db.execute = AsyncMock(return_value=result_mock)

        data = WorkLogCreate(llm_calls=1, tokens_used=100)
        with pytest.raises(ValueError, match="Issue not found"):
            await service.create(mock_db, issue_id, data)

    @pytest.mark.asyncio
    async def test_list_worklogs(self, service: WorkLogService, mock_db: AsyncMock, issue_id: uuid.UUID) -> None:
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.deleted_at = None

        wl1 = MagicMock(spec=WorkLog)
        wl2 = MagicMock(spec=WorkLog)

        issue_result = MagicMock()
        issue_result.scalar_one_or_none.return_value = mock_issue

        list_result = MagicMock()
        list_result.scalars.return_value.all.return_value = [wl1, wl2]

        mock_db.execute = AsyncMock(side_effect=[issue_result, list_result])

        worklogs = await service.list_by_issue(mock_db, issue_id)
        assert len(worklogs) == 2

    @pytest.mark.asyncio
    async def test_list_worklogs_empty(self, service: WorkLogService, mock_db: AsyncMock, issue_id: uuid.UUID) -> None:
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.deleted_at = None

        issue_result = MagicMock()
        issue_result.scalar_one_or_none.return_value = mock_issue

        list_result = MagicMock()
        list_result.scalars.return_value.all.return_value = []

        mock_db.execute = AsyncMock(side_effect=[issue_result, list_result])

        worklogs = await service.list_by_issue(mock_db, issue_id)
        assert worklogs == []

    @pytest.mark.asyncio
    async def test_list_worklogs_issue_not_found(self, service: WorkLogService, mock_db: AsyncMock) -> None:
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result_mock)

        with pytest.raises(ValueError, match="Issue not found"):
            await service.list_by_issue(mock_db, uuid.uuid4())


class TestWorkLogEndpoint:
    @pytest.fixture
    def issue_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_create_worklog_endpoint(self, issue_id: uuid.UUID) -> None:
        from personal_jira.api.v1.endpoints.worklog import create_worklog

        mock_db = AsyncMock()
        mock_worklog = MagicMock()
        mock_worklog.id = uuid.uuid4()
        mock_worklog.issue_id = issue_id
        mock_worklog.agent_id = None
        mock_worklog.llm_calls = 2
        mock_worklog.tokens_used = 800
        mock_worklog.content = "attempt content"
        mock_worklog.created_at = datetime.utcnow()
        mock_worklog.updated_at = datetime.utcnow()

        with patch(
            "personal_jira.api.v1.endpoints.worklog.WorkLogService"
        ) as MockService:
            instance = MockService.return_value
            instance.create = AsyncMock(return_value=mock_worklog)

            data = WorkLogCreate(llm_calls=2, tokens_used=800, content="attempt content")
            result = await create_worklog(issue_id, data, mock_db)

            instance.create.assert_awaited_once_with(mock_db, issue_id, data)
            assert result == mock_worklog

    @pytest.mark.asyncio
    async def test_create_worklog_not_found(self, issue_id: uuid.UUID) -> None:
        from personal_jira.api.v1.endpoints.worklog import create_worklog

        mock_db = AsyncMock()

        with patch(
            "personal_jira.api.v1.endpoints.worklog.WorkLogService"
        ) as MockService:
            instance = MockService.return_value
            instance.create = AsyncMock(side_effect=ValueError("Issue not found"))

            from fastapi import HTTPException

            data = WorkLogCreate(llm_calls=1, tokens_used=100)
            with pytest.raises(HTTPException) as exc_info:
                await create_worklog(issue_id, data, mock_db)
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_list_worklogs_endpoint(self, issue_id: uuid.UUID) -> None:
        from personal_jira.api.v1.endpoints.worklog import list_worklogs

        mock_db = AsyncMock()
        mock_worklogs = [MagicMock(), MagicMock()]

        with patch(
            "personal_jira.api.v1.endpoints.worklog.WorkLogService"
        ) as MockService:
            instance = MockService.return_value
            instance.list_by_issue = AsyncMock(return_value=mock_worklogs)

            result = await list_worklogs(issue_id, mock_db)

            instance.list_by_issue.assert_awaited_once_with(mock_db, issue_id)
            assert result == mock_worklogs

    @pytest.mark.asyncio
    async def test_list_worklogs_not_found(self, issue_id: uuid.UUID) -> None:
        from personal_jira.api.v1.endpoints.worklog import list_worklogs

        mock_db = AsyncMock()

        with patch(
            "personal_jira.api.v1.endpoints.worklog.WorkLogService"
        ) as MockService:
            instance = MockService.return_value
            instance.list_by_issue = AsyncMock(side_effect=ValueError("Issue not found"))

            from fastapi import HTTPException

            with pytest.raises(HTTPException) as exc_info:
                await list_worklogs(issue_id, mock_db)
            assert exc_info.value.status_code == 404
