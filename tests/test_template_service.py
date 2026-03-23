import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from personal_jira.models.issue import Issue
from personal_jira.models.template import IssueTemplate
from personal_jira.schemas.template import TemplateCreate, CloneIssueRequest
from personal_jira.services.template import TemplateService


@pytest.fixture
def mock_db() -> AsyncMock:
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture
def service() -> TemplateService:
    return TemplateService()


class TestTemplateServiceCreate:
    @pytest.mark.asyncio
    async def test_create_template(self, service: TemplateService, mock_db: AsyncMock) -> None:
        data = TemplateCreate(
            name="Bug Report",
            title_pattern="[BUG] {summary}",
            description_template="## Steps\n\n## Expected\n\n## Actual",
            default_priority="high",
            default_issue_type="bug",
            default_labels=["bug"],
        )
        result = await service.create(mock_db, data)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()
        assert isinstance(result, IssueTemplate)
        assert result.name == "Bug Report"


class TestTemplateServiceGet:
    @pytest.mark.asyncio
    async def test_get_template(self, service: TemplateService, mock_db: AsyncMock) -> None:
        template_id = uuid.uuid4()
        mock_template = IssueTemplate(
            id=template_id,
            name="Bug Report",
            title_pattern="[BUG] {summary}",
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_template
        mock_db.execute.return_value = mock_result

        result = await service.get_by_id(mock_db, template_id)
        assert result is not None
        assert result.id == template_id

    @pytest.mark.asyncio
    async def test_get_template_not_found(self, service: TemplateService, mock_db: AsyncMock) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await service.get_by_id(mock_db, uuid.uuid4())
        assert result is None


class TestTemplateServiceList:
    @pytest.mark.asyncio
    async def test_list_templates(self, service: TemplateService, mock_db: AsyncMock) -> None:
        templates = [
            IssueTemplate(name="Bug", title_pattern="[BUG] {s}"),
            IssueTemplate(name="Feature", title_pattern="[FEAT] {s}"),
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = templates
        mock_db.execute.return_value = mock_result

        result = await service.list_all(mock_db)
        assert len(result) == 2


class TestCreateIssueFromTemplate:
    @pytest.mark.asyncio
    async def test_create_from_template(self, service: TemplateService, mock_db: AsyncMock) -> None:
        template_id = uuid.uuid4()
        template = IssueTemplate(
            id=template_id,
            name="Bug Report",
            title_pattern="[BUG] {summary}",
            description_template="## Steps\n{details}",
            default_priority="high",
            default_issue_type="bug",
            default_labels=["bug"],
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = template
        mock_db.execute.return_value = mock_result

        result = await service.create_issue_from_template(
            mock_db,
            template_id,
            variables={"summary": "Login crash", "details": "App crashes on login"},
        )

        assert isinstance(result, Issue)
        assert result.title == "[BUG] Login crash"
        assert result.priority == "high"
        assert result.issue_type == "bug"
        mock_db.add.assert_called()
        mock_db.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_create_from_template_not_found(self, service: TemplateService, mock_db: AsyncMock) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="Template not found"):
            await service.create_issue_from_template(mock_db, uuid.uuid4(), variables={})


class TestCloneIssue:
    @pytest.mark.asyncio
    async def test_clone_issue(self, service: TemplateService, mock_db: AsyncMock) -> None:
        issue_id = uuid.uuid4()
        original = Issue(
            id=issue_id,
            title="Original Issue",
            description="Original description",
            priority="high",
            issue_type="task",
            status="done",
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = original
        mock_db.execute.return_value = mock_result

        request = CloneIssueRequest(title_prefix="[CLONE]", reset_status=True)
        result = await service.clone_issue(mock_db, issue_id, request)

        assert isinstance(result, Issue)
        assert result.title == "[CLONE] Original Issue"
        assert result.description == "Original description"
        assert result.priority == "high"
        assert result.status == "backlog"
        assert result.id != issue_id
        mock_db.add.assert_called()
        mock_db.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_clone_issue_not_found(self, service: TemplateService, mock_db: AsyncMock) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        request = CloneIssueRequest()
        with pytest.raises(ValueError, match="Issue not found"):
            await service.clone_issue(mock_db, uuid.uuid4(), request)

    @pytest.mark.asyncio
    async def test_clone_issue_keep_status(self, service: TemplateService, mock_db: AsyncMock) -> None:
        issue_id = uuid.uuid4()
        original = Issue(
            id=issue_id,
            title="Original",
            status="in_progress",
            priority="medium",
            issue_type="task",
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = original
        mock_db.execute.return_value = mock_result

        request = CloneIssueRequest(reset_status=False)
        result = await service.clone_issue(mock_db, issue_id, request)

        assert result.status == "in_progress"
