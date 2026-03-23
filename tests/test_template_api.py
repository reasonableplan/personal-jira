import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from personal_jira.app import create_app
from personal_jira.models.issue import Issue
from personal_jira.models.template import IssueTemplate

app = create_app()


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
async def client(mock_db):
    async def override_get_db():
        yield mock_db

    from personal_jira.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


class TestCreateTemplateEndpoint:
    @pytest.mark.asyncio
    async def test_create_template_201(self, client: AsyncClient) -> None:
        payload = {
            "name": "Bug Report",
            "title_pattern": "[BUG] {summary}",
            "description_template": "## Steps\n\n## Expected",
            "default_priority": "high",
            "default_issue_type": "bug",
            "default_labels": ["bug"],
        }
        with patch(
            "personal_jira.api.template.template_service.create",
            new_callable=AsyncMock,
        ) as mock_create:
            template_id = uuid.uuid4()
            mock_create.return_value = IssueTemplate(
                id=template_id,
                name="Bug Report",
                title_pattern="[BUG] {summary}",
                description_template="## Steps\n\n## Expected",
                default_priority="high",
                default_issue_type="bug",
                default_labels=["bug"],
            )
            resp = await client.post("/api/v1/templates", json=payload)

        assert resp.status_code == 201
        assert resp.json()["name"] == "Bug Report"

    @pytest.mark.asyncio
    async def test_create_template_422_missing_name(self, client: AsyncClient) -> None:
        payload = {"title_pattern": "[BUG] {summary}"}
        resp = await client.post("/api/v1/templates", json=payload)
        assert resp.status_code == 422


class TestListTemplatesEndpoint:
    @pytest.mark.asyncio
    async def test_list_templates_200(self, client: AsyncClient) -> None:
        with patch(
            "personal_jira.api.template.template_service.list_all",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = [
                IssueTemplate(name="Bug", title_pattern="[BUG] {s}"),
                IssueTemplate(name="Feature", title_pattern="[FEAT] {s}"),
            ]
            resp = await client.get("/api/v1/templates")

        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestGetTemplateEndpoint:
    @pytest.mark.asyncio
    async def test_get_template_200(self, client: AsyncClient) -> None:
        template_id = uuid.uuid4()
        with patch(
            "personal_jira.api.template.template_service.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = IssueTemplate(
                id=template_id,
                name="Bug Report",
                title_pattern="[BUG] {summary}",
            )
            resp = await client.get(f"/api/v1/templates/{template_id}")

        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_template_404(self, client: AsyncClient) -> None:
        with patch(
            "personal_jira.api.template.template_service.get_by_id",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None
            resp = await client.get(f"/api/v1/templates/{uuid.uuid4()}")

        assert resp.status_code == 404


class TestCreateFromTemplateEndpoint:
    @pytest.mark.asyncio
    async def test_create_from_template_201(self, client: AsyncClient) -> None:
        template_id = uuid.uuid4()
        issue_id = uuid.uuid4()
        payload = {"variables": {"summary": "Login crash"}}
        with patch(
            "personal_jira.api.template.template_service.create_issue_from_template",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = Issue(
                id=issue_id,
                title="[BUG] Login crash",
                priority="high",
                issue_type="bug",
                status="backlog",
            )
            resp = await client.post(
                f"/api/v1/templates/{template_id}/issues",
                json=payload,
            )

        assert resp.status_code == 201
        assert resp.json()["title"] == "[BUG] Login crash"

    @pytest.mark.asyncio
    async def test_create_from_template_404(self, client: AsyncClient) -> None:
        payload = {"variables": {"summary": "Test"}}
        with patch(
            "personal_jira.api.template.template_service.create_issue_from_template",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.side_effect = ValueError("Template not found")
            resp = await client.post(
                f"/api/v1/templates/{uuid.uuid4()}/issues",
                json=payload,
            )

        assert resp.status_code == 404


class TestCloneIssueEndpoint:
    @pytest.mark.asyncio
    async def test_clone_issue_201(self, client: AsyncClient) -> None:
        issue_id = uuid.uuid4()
        cloned_id = uuid.uuid4()
        payload = {"title_prefix": "[CLONE]", "reset_status": True}
        with patch(
            "personal_jira.api.template.template_service.clone_issue",
            new_callable=AsyncMock,
        ) as mock_clone:
            mock_clone.return_value = Issue(
                id=cloned_id,
                title="[CLONE] Original",
                priority="high",
                issue_type="task",
                status="backlog",
            )
            resp = await client.post(
                f"/api/v1/issues/{issue_id}/clone",
                json=payload,
            )

        assert resp.status_code == 201
        assert resp.json()["title"] == "[CLONE] Original"

    @pytest.mark.asyncio
    async def test_clone_issue_404(self, client: AsyncClient) -> None:
        payload = {}
        with patch(
            "personal_jira.api.template.template_service.clone_issue",
            new_callable=AsyncMock,
        ) as mock_clone:
            mock_clone.side_effect = ValueError("Issue not found")
            resp = await client.post(
                f"/api/v1/issues/{uuid.uuid4()}/clone",
                json=payload,
            )

        assert resp.status_code == 404
