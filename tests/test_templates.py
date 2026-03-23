import uuid
from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient

from personal_jira.models.template import IssueTemplate
from personal_jira.schemas.template import TemplateCreate, TemplateResponse


API_TEMPLATES = "/api/v1/templates"
API_ISSUES = "/api/v1/issues"


@pytest.mark.asyncio
class TestTemplateModel:
    async def test_table_name(self) -> None:
        assert IssueTemplate.__tablename__ == "issue_templates"

    async def test_required_columns(self) -> None:
        columns = {c.name for c in IssueTemplate.__table__.columns}
        expected = {"id", "name", "title_pattern", "description", "priority", "labels", "created_at", "updated_at"}
        assert expected.issubset(columns)


@pytest.mark.asyncio
class TestTemplateSchema:
    async def test_create_schema(self) -> None:
        data = TemplateCreate(
            name="Bug Report",
            title_pattern="[BUG] {summary}",
            description="Steps to reproduce:\n1.\n2.",
            priority="high",
            labels=["bug"],
        )
        assert data.name == "Bug Report"
        assert data.labels == ["bug"]

    async def test_create_schema_defaults(self) -> None:
        data = TemplateCreate(name="Minimal", title_pattern="{summary}")
        assert data.priority is None
        assert data.labels == []


@pytest.mark.asyncio
class TestTemplateAPI:
    async def test_create_template(self, client: AsyncClient) -> None:
        resp = await client.post(API_TEMPLATES, json={
            "name": "Bug Report",
            "title_pattern": "[BUG] {summary}",
            "description": "Reproduce steps",
            "priority": "high",
            "labels": ["bug"],
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Bug Report"
        assert body["title_pattern"] == "[BUG] {summary}"

    async def test_create_template_minimal(self, client: AsyncClient) -> None:
        resp = await client.post(API_TEMPLATES, json={
            "name": "Simple",
            "title_pattern": "{summary}",
        })
        assert resp.status_code == 201
        assert resp.json()["labels"] == []

    async def test_create_template_duplicate_name(self, client: AsyncClient) -> None:
        payload = {"name": "Dup", "title_pattern": "{s}"}
        await client.post(API_TEMPLATES, json=payload)
        resp = await client.post(API_TEMPLATES, json=payload)
        assert resp.status_code == 409

    async def test_list_templates(self, client: AsyncClient) -> None:
        await client.post(API_TEMPLATES, json={"name": "A", "title_pattern": "{s}"})
        await client.post(API_TEMPLATES, json={"name": "B", "title_pattern": "{s}"})
        resp = await client.get(API_TEMPLATES)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_get_template(self, client: AsyncClient) -> None:
        create = await client.post(API_TEMPLATES, json={"name": "Get", "title_pattern": "{s}"})
        tid = create.json()["id"]
        resp = await client.get(f"{API_TEMPLATES}/{tid}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Get"

    async def test_get_template_not_found(self, client: AsyncClient) -> None:
        resp = await client.get(f"{API_TEMPLATES}/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_delete_template(self, client: AsyncClient) -> None:
        create = await client.post(API_TEMPLATES, json={"name": "Del", "title_pattern": "{s}"})
        tid = create.json()["id"]
        resp = await client.delete(f"{API_TEMPLATES}/{tid}")
        assert resp.status_code == 204

    async def test_create_issue_from_template(self, client: AsyncClient) -> None:
        tmpl = await client.post(API_TEMPLATES, json={
            "name": "Feature",
            "title_pattern": "[FEAT] {summary}",
            "description": "As a user...",
            "priority": "medium",
            "labels": ["feature"],
        })
        tid = tmpl.json()["id"]
        resp = await client.post(f"{API_TEMPLATES}/{tid}/issues", json={
            "summary": "Add dark mode",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "[FEAT] Add dark mode"
        assert body["description"] == "As a user..."
        assert body["priority"] == "medium"


@pytest.mark.asyncio
class TestIssueClone:
    async def test_clone_issue(self, client: AsyncClient, sample_issue: dict[str, Any]) -> None:
        issue_id = sample_issue["id"]
        resp = await client.post(f"{API_ISSUES}/{issue_id}/clone")
        assert resp.status_code == 201
        clone = resp.json()
        assert clone["id"] != issue_id
        assert clone["title"] == f"[CLONE] {sample_issue['title']}"
        assert clone["description"] == sample_issue["description"]
        assert clone["priority"] == sample_issue["priority"]

    async def test_clone_issue_custom_title(self, client: AsyncClient, sample_issue: dict[str, Any]) -> None:
        issue_id = sample_issue["id"]
        resp = await client.post(f"{API_ISSUES}/{issue_id}/clone", json={
            "title_override": "Custom Clone Title",
        })
        assert resp.status_code == 201
        assert resp.json()["title"] == "Custom Clone Title"

    async def test_clone_nonexistent_issue(self, client: AsyncClient) -> None:
        resp = await client.post(f"{API_ISSUES}/{uuid.uuid4()}/clone")
        assert resp.status_code == 404
