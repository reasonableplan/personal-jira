import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from personal_jira.models.issue_template import IssueTemplate
from personal_jira.schemas.issue_template import (
    IssueTemplateCreate,
    IssueTemplateResponse,
    IssueTemplateUpdate,
    IssueFromTemplateRequest,
    IssueCloneRequest,
    IssueCloneResponse,
)
from personal_jira.services.template_service import TemplateService
from personal_jira.routers.template import router


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


@pytest.fixture
def client(app: FastAPI):
    return TestClient(app)


@pytest.fixture
def template_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def issue_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def sample_template(template_id: uuid.UUID) -> dict:
    return {
        "id": template_id,
        "name": "Bug Report Template",
        "description": "Standard bug report",
        "default_title": "[BUG] ",
        "default_description": "## Steps to Reproduce\n\n## Expected\n\n## Actual",
        "default_priority": "high",
        "default_issue_type": "bug",
        "default_labels": ["bug", "triage"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    db.delete = AsyncMock()
    return db


class TestIssueTemplateSchema:
    def test_create_schema_valid(self):
        data = IssueTemplateCreate(
            name="Bug Template",
            description="For bugs",
            default_title="[BUG]",
            default_priority="high",
            default_issue_type="bug",
            default_labels=["bug"],
        )
        assert data.name == "Bug Template"
        assert data.default_labels == ["bug"]

    def test_create_schema_minimal(self):
        data = IssueTemplateCreate(name="Minimal")
        assert data.name == "Minimal"
        assert data.default_title is None
        assert data.default_labels == []

    def test_create_schema_name_required(self):
        with pytest.raises(Exception):
            IssueTemplateCreate()

    def test_update_schema_partial(self):
        data = IssueTemplateUpdate(name="Updated")
        dumped = data.model_dump(exclude_unset=True)
        assert dumped == {"name": "Updated"}

    def test_update_schema_empty(self):
        data = IssueTemplateUpdate()
        dumped = data.model_dump(exclude_unset=True)
        assert dumped == {}

    def test_clone_request_defaults(self):
        req = IssueCloneRequest()
        assert req.include_comments is True
        assert req.include_work_logs is False
        assert req.include_children is False
        assert req.title_prefix == "[CLONE] "

    def test_clone_request_custom(self):
        req = IssueCloneRequest(
            include_comments=False,
            include_children=True,
            title_prefix="[COPY] ",
        )
        assert req.include_comments is False
        assert req.include_children is True
        assert req.title_prefix == "[COPY] "

    def test_from_template_request(self):
        tid = uuid.uuid4()
        req = IssueFromTemplateRequest(
            template_id=tid,
            title_override="Custom Title",
        )
        assert req.template_id == tid
        assert req.title_override == "Custom Title"
        assert req.parent_id is None


class TestIssueTemplateModel:
    def test_model_table_name(self):
        assert IssueTemplate.__tablename__ == "issue_templates"

    def test_model_has_required_columns(self):
        columns = {c.name for c in IssueTemplate.__table__.columns}
        expected = {
            "id", "name", "description",
            "default_title", "default_description",
            "default_priority", "default_issue_type",
            "default_labels", "created_at", "updated_at",
        }
        assert expected.issubset(columns)

    def test_model_id_is_uuid(self):
        col = IssueTemplate.__table__.columns["id"]
        assert "UUID" in str(col.type).upper() or "CHAR" in str(col.type).upper()


class TestTemplateService:
    @pytest.mark.asyncio
    async def test_create_template(self, mock_db: AsyncMock):
        service = TemplateService(mock_db)
        data = IssueTemplateCreate(
            name="Test Template",
            default_priority="medium",
            default_issue_type="task",
        )

        mock_db.refresh = AsyncMock(
            side_effect=lambda obj: setattr(obj, "id", uuid.uuid4())
        )

        result = await service.create_template(data)
        assert result.name == "Test Template"
        assert result.default_priority == "medium"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_template_found(self, mock_db: AsyncMock, template_id: uuid.UUID):
        service = TemplateService(mock_db)
        mock_template = IssueTemplate(id=template_id, name="Found")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_template
        mock_db.execute.return_value = mock_result

        result = await service.get_template(template_id)
        assert result is not None
        assert result.name == "Found"

    @pytest.mark.asyncio
    async def test_get_template_not_found(self, mock_db: AsyncMock):
        service = TemplateService(mock_db)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await service.get_template(uuid.uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_list_templates(self, mock_db: AsyncMock):
        service = TemplateService(mock_db)
        t1 = IssueTemplate(id=uuid.uuid4(), name="T1")
        t2 = IssueTemplate(id=uuid.uuid4(), name="T2")
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [t1, t2]
        mock_db.execute.return_value = mock_result

        result = await service.list_templates()
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_update_template(self, mock_db: AsyncMock, template_id: uuid.UUID):
        service = TemplateService(mock_db)
        existing = IssueTemplate(id=template_id, name="Old")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_db.execute.return_value = mock_result

        update_data = IssueTemplateUpdate(name="New")
        result = await service.update_template(template_id, update_data)
        assert result is not None
        assert result.name == "New"
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_template_not_found(self, mock_db: AsyncMock):
        service = TemplateService(mock_db)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await service.update_template(
            uuid.uuid4(), IssueTemplateUpdate(name="X")
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_template(self, mock_db: AsyncMock, template_id: uuid.UUID):
        service = TemplateService(mock_db)
        existing = IssueTemplate(id=template_id, name="ToDelete")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_db.execute.return_value = mock_result

        result = await service.delete_template(template_id)
        assert result is True
        mock_db.delete.assert_awaited_once_with(existing)

    @pytest.mark.asyncio
    async def test_delete_template_not_found(self, mock_db: AsyncMock):
        service = TemplateService(mock_db)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await service.delete_template(uuid.uuid4())
        assert result is False

    @pytest.mark.asyncio
    async def test_create_issue_from_template(
        self, mock_db: AsyncMock, template_id: uuid.UUID
    ):
        service = TemplateService(mock_db)
        template = IssueTemplate(
            id=template_id,
            name="Bug Template",
            default_title="[BUG] ",
            default_description="Steps to reproduce",
            default_priority="high",
            default_issue_type="bug",
            default_labels=["bug"],
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = template
        mock_db.execute.return_value = mock_result
        mock_db.refresh = AsyncMock(
            side_effect=lambda obj: setattr(obj, "id", uuid.uuid4())
        )

        req = IssueFromTemplateRequest(template_id=template_id)
        issue = await service.create_issue_from_template(req)
        assert issue.title == "[BUG] "
        assert issue.description == "Steps to reproduce"
        assert issue.priority == "high"
        assert issue.issue_type == "bug"
        mock_db.add.assert_called()
        mock_db.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_create_issue_from_template_with_override(
        self, mock_db: AsyncMock, template_id: uuid.UUID
    ):
        service = TemplateService(mock_db)
        template = IssueTemplate(
            id=template_id,
            name="Bug Template",
            default_title="[BUG] ",
            default_description="Steps",
            default_priority="high",
            default_issue_type="bug",
            default_labels=[],
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = template
        mock_db.execute.return_value = mock_result
        mock_db.refresh = AsyncMock(
            side_effect=lambda obj: setattr(obj, "id", uuid.uuid4())
        )

        req = IssueFromTemplateRequest(
            template_id=template_id,
            title_override="Custom Bug Title",
            description_override="Custom desc",
            priority_override="low",
        )
        issue = await service.create_issue_from_template(req)
        assert issue.title == "Custom Bug Title"
        assert issue.description == "Custom desc"
        assert issue.priority == "low"

    @pytest.mark.asyncio
    async def test_create_issue_from_template_not_found(
        self, mock_db: AsyncMock
    ):
        service = TemplateService(mock_db)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        req = IssueFromTemplateRequest(template_id=uuid.uuid4())
        with pytest.raises(ValueError, match="Template not found"):
            await service.create_issue_from_template(req)

    @pytest.mark.asyncio
    async def test_clone_issue(self, mock_db: AsyncMock, issue_id: uuid.UUID):
        from personal_jira.models.issue import Issue

        service = TemplateService(mock_db)
        original = Issue(
            id=issue_id,
            title="Original Issue",
            description="Original desc",
            status="open",
            priority="high",
            issue_type="task",
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = original
        mock_db.execute.return_value = mock_result
        mock_db.refresh = AsyncMock(
            side_effect=lambda obj: setattr(obj, "id", uuid.uuid4())
        )

        req = IssueCloneRequest()
        cloned = await service.clone_issue(issue_id, req)
        assert cloned.title == "[CLONE] Original Issue"
        assert cloned.description == "Original desc"
        assert cloned.priority == "high"
        assert cloned.issue_type == "task"
        mock_db.add.assert_called()
        mock_db.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_clone_issue_custom_prefix(
        self, mock_db: AsyncMock, issue_id: uuid.UUID
    ):
        from personal_jira.models.issue import Issue

        service = TemplateService(mock_db)
        original = Issue(
            id=issue_id,
            title="Original",
            description="Desc",
            status="open",
            priority="medium",
            issue_type="story",
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = original
        mock_db.execute.return_value = mock_result
        mock_db.refresh = AsyncMock(
            side_effect=lambda obj: setattr(obj, "id", uuid.uuid4())
        )

        req = IssueCloneRequest(title_prefix="[COPY] ")
        cloned = await service.clone_issue(issue_id, req)
        assert cloned.title == "[COPY] Original"

    @pytest.mark.asyncio
    async def test_clone_issue_not_found(self, mock_db: AsyncMock):
        service = TemplateService(mock_db)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        req = IssueCloneRequest()
        with pytest.raises(ValueError, match="Issue not found"):
            await service.clone_issue(uuid.uuid4(), req)


class TestTemplateAPI:
    API_PREFIX = "/api/v1/templates"

    def test_create_template(self, client: TestClient):
        with patch(
            "personal_jira.routers.template.TemplateService"
        ) as MockService:
            mock_svc = AsyncMock()
            template = IssueTemplate(
                id=uuid.uuid4(),
                name="Bug Template",
                description="For bugs",
                default_title="[BUG]",
                default_description="",
                default_priority="high",
                default_issue_type="bug",
                default_labels=["bug"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_svc.create_template.return_value = template
            MockService.return_value = mock_svc

            resp = client.post(
                self.API_PREFIX,
                json={"name": "Bug Template", "default_priority": "high"},
            )
            assert resp.status_code == 201
            body = resp.json()
            assert body["name"] == "Bug Template"

    def test_get_template(self, client: TestClient, template_id: uuid.UUID):
        with patch(
            "personal_jira.routers.template.TemplateService"
        ) as MockService:
            mock_svc = AsyncMock()
            template = IssueTemplate(
                id=template_id,
                name="Found",
                default_labels=[],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_svc.get_template.return_value = template
            MockService.return_value = mock_svc

            resp = client.get(f"{self.API_PREFIX}/{template_id}")
            assert resp.status_code == 200

    def test_get_template_not_found(self, client: TestClient):
        with patch(
            "personal_jira.routers.template.TemplateService"
        ) as MockService:
            mock_svc = AsyncMock()
            mock_svc.get_template.return_value = None
            MockService.return_value = mock_svc

            resp = client.get(f"{self.API_PREFIX}/{uuid.uuid4()}")
            assert resp.status_code == 404

    def test_list_templates(self, client: TestClient):
        with patch(
            "personal_jira.routers.template.TemplateService"
        ) as MockService:
            mock_svc = AsyncMock()
            mock_svc.list_templates.return_value = []
            MockService.return_value = mock_svc

            resp = client.get(self.API_PREFIX)
            assert resp.status_code == 200
            assert resp.json() == []

    def test_update_template(self, client: TestClient, template_id: uuid.UUID):
        with patch(
            "personal_jira.routers.template.TemplateService"
        ) as MockService:
            mock_svc = AsyncMock()
            updated = IssueTemplate(
                id=template_id,
                name="Updated",
                default_labels=[],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_svc.update_template.return_value = updated
            MockService.return_value = mock_svc

            resp = client.patch(
                f"{self.API_PREFIX}/{template_id}",
                json={"name": "Updated"},
            )
            assert resp.status_code == 200
            assert resp.json()["name"] == "Updated"

    def test_update_template_not_found(self, client: TestClient):
        with patch(
            "personal_jira.routers.template.TemplateService"
        ) as MockService:
            mock_svc = AsyncMock()
            mock_svc.update_template.return_value = None
            MockService.return_value = mock_svc

            resp = client.patch(
                f"{self.API_PREFIX}/{uuid.uuid4()}",
                json={"name": "X"},
            )
            assert resp.status_code == 404

    def test_delete_template(self, client: TestClient, template_id: uuid.UUID):
        with patch(
            "personal_jira.routers.template.TemplateService"
        ) as MockService:
            mock_svc = AsyncMock()
            mock_svc.delete_template.return_value = True
            MockService.return_value = mock_svc

            resp = client.delete(f"{self.API_PREFIX}/{template_id}")
            assert resp.status_code == 204

    def test_delete_template_not_found(self, client: TestClient):
        with patch(
            "personal_jira.routers.template.TemplateService"
        ) as MockService:
            mock_svc = AsyncMock()
            mock_svc.delete_template.return_value = False
            MockService.return_value = mock_svc

            resp = client.delete(f"{self.API_PREFIX}/{uuid.uuid4()}")
            assert resp.status_code == 404

    def test_create_issue_from_template(self, client: TestClient):
        from personal_jira.models.issue import Issue

        with patch(
            "personal_jira.routers.template.TemplateService"
        ) as MockService:
            mock_svc = AsyncMock()
            issue = Issue(
                id=uuid.uuid4(),
                title="[BUG] New",
                description="desc",
                status="open",
                priority="high",
                issue_type="bug",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_svc.create_issue_from_template.return_value = issue
            MockService.return_value = mock_svc

            tid = uuid.uuid4()
            resp = client.post(
                f"{self.API_PREFIX}/create-issue",
                json={"template_id": str(tid)},
            )
            assert resp.status_code == 201

    def test_create_issue_from_template_not_found(self, client: TestClient):
        with patch(
            "personal_jira.routers.template.TemplateService"
        ) as MockService:
            mock_svc = AsyncMock()
            mock_svc.create_issue_from_template.side_effect = ValueError(
                "Template not found"
            )
            MockService.return_value = mock_svc

            resp = client.post(
                f"{self.API_PREFIX}/create-issue",
                json={"template_id": str(uuid.uuid4())},
            )
            assert resp.status_code == 404


class TestCloneAPI:
    def test_clone_issue(self, client: TestClient, issue_id: uuid.UUID):
        from personal_jira.models.issue import Issue

        with patch(
            "personal_jira.routers.template.TemplateService"
        ) as MockService:
            mock_svc = AsyncMock()
            cloned = Issue(
                id=uuid.uuid4(),
                title="[CLONE] Original",
                description="desc",
                status="open",
                priority="medium",
                issue_type="task",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_svc.clone_issue.return_value = cloned
            MockService.return_value = mock_svc

            resp = client.post(
                f"/api/v1/issues/{issue_id}/clone",
                json={},
            )
            assert resp.status_code == 201
            body = resp.json()
            assert body["title"] == "[CLONE] Original"
            assert "source_issue_id" in body

    def test_clone_issue_not_found(self, client: TestClient):
        with patch(
            "personal_jira.routers.template.TemplateService"
        ) as MockService:
            mock_svc = AsyncMock()
            mock_svc.clone_issue.side_effect = ValueError("Issue not found")
            MockService.return_value = mock_svc

            resp = client.post(
                f"/api/v1/issues/{uuid.uuid4()}/clone",
                json={},
            )
            assert resp.status_code == 404

    def test_clone_issue_invalid_uuid(self, client: TestClient):
        resp = client.post("/api/v1/issues/not-a-uuid/clone", json={})
        assert resp.status_code == 422
