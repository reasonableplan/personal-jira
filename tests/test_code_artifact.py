import uuid
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app import create_app
from database import get_db
from models.issue import Issue
from models.code_artifact import CodeArtifact, ArtifactType
from schemas.code_artifact import CodeArtifactCreate
from services.code_artifact import CodeArtifactService
from workflows.issue_status import IssueStatus


@pytest.fixture
def sample_issue_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
async def created_issue(db_session, sample_issue_id: uuid.UUID) -> Issue:
    issue = Issue(
        id=sample_issue_id,
        title="Test issue for artifacts",
        status=IssueStatus.IN_PROGRESS,
        priority="medium",
        issue_type="task",
    )
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)
    return issue


class TestArtifactTypeEnum:
    def test_file_type(self):
        assert ArtifactType.FILE == "file"

    def test_commit_type(self):
        assert ArtifactType.COMMIT == "commit"

    def test_pull_request_type(self):
        assert ArtifactType.PULL_REQUEST == "pull_request"


class TestCodeArtifactModel:
    @pytest.mark.asyncio
    async def test_create_artifact(self, db_session, created_issue: Issue):
        artifact = CodeArtifact(
            issue_id=created_issue.id,
            artifact_type=ArtifactType.FILE,
            identifier="src/main.py",
        )
        db_session.add(artifact)
        await db_session.commit()
        await db_session.refresh(artifact)

        assert artifact.id is not None
        assert artifact.issue_id == created_issue.id
        assert artifact.artifact_type == ArtifactType.FILE
        assert artifact.identifier == "src/main.py"
        assert artifact.metadata_ is None
        assert artifact.created_at is not None

    @pytest.mark.asyncio
    async def test_create_commit_artifact_with_metadata(self, db_session, created_issue: Issue):
        artifact = CodeArtifact(
            issue_id=created_issue.id,
            artifact_type=ArtifactType.COMMIT,
            identifier="abc123def456",
            metadata_={"branch": "feature/test", "message": "fix bug"},
        )
        db_session.add(artifact)
        await db_session.commit()
        await db_session.refresh(artifact)

        assert artifact.artifact_type == ArtifactType.COMMIT
        assert artifact.metadata_["branch"] == "feature/test"

    @pytest.mark.asyncio
    async def test_create_pr_artifact(self, db_session, created_issue: Issue):
        artifact = CodeArtifact(
            issue_id=created_issue.id,
            artifact_type=ArtifactType.PULL_REQUEST,
            identifier="https://github.com/org/repo/pull/42",
            metadata_={"pr_number": 42, "repo": "org/repo"},
        )
        db_session.add(artifact)
        await db_session.commit()
        await db_session.refresh(artifact)

        assert artifact.artifact_type == ArtifactType.PULL_REQUEST
        assert artifact.identifier == "https://github.com/org/repo/pull/42"


class TestCodeArtifactSchema:
    def test_create_file_schema(self):
        schema = CodeArtifactCreate(
            artifact_type=ArtifactType.FILE,
            identifier="src/utils.py",
        )
        assert schema.artifact_type == ArtifactType.FILE
        assert schema.identifier == "src/utils.py"
        assert schema.metadata_ is None

    def test_create_commit_schema_with_metadata(self):
        schema = CodeArtifactCreate(
            artifact_type=ArtifactType.COMMIT,
            identifier="abc123",
            metadata_={"branch": "main"},
        )
        assert schema.metadata_["branch"] == "main"

    def test_missing_identifier_raises(self):
        with pytest.raises(Exception):
            CodeArtifactCreate(
                artifact_type=ArtifactType.FILE,
                identifier="",
            )

    def test_missing_artifact_type_raises(self):
        with pytest.raises(Exception):
            CodeArtifactCreate(
                identifier="src/main.py",
            )


class TestCodeArtifactService:
    @pytest.mark.asyncio
    async def test_create_artifact(self, db_session, created_issue: Issue):
        service = CodeArtifactService(db_session)
        artifact = await service.create(
            issue_id=created_issue.id,
            data=CodeArtifactCreate(
                artifact_type=ArtifactType.FILE,
                identifier="src/main.py",
            ),
        )
        assert artifact.id is not None
        assert artifact.issue_id == created_issue.id

    @pytest.mark.asyncio
    async def test_create_commit_triggers_review_transition(
        self, db_session, created_issue: Issue
    ):
        service = CodeArtifactService(db_session)
        await service.create(
            issue_id=created_issue.id,
            data=CodeArtifactCreate(
                artifact_type=ArtifactType.COMMIT,
                identifier="abc123def456",
            ),
        )
        result = await db_session.execute(
            select(Issue).where(Issue.id == created_issue.id)
        )
        issue = result.scalar_one()
        assert issue.status == IssueStatus.IN_REVIEW

    @pytest.mark.asyncio
    async def test_create_file_does_not_trigger_transition(
        self, db_session, created_issue: Issue
    ):
        service = CodeArtifactService(db_session)
        await service.create(
            issue_id=created_issue.id,
            data=CodeArtifactCreate(
                artifact_type=ArtifactType.FILE,
                identifier="readme.md",
            ),
        )
        result = await db_session.execute(
            select(Issue).where(Issue.id == created_issue.id)
        )
        issue = result.scalar_one()
        assert issue.status == IssueStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_list_artifacts(self, db_session, created_issue: Issue):
        service = CodeArtifactService(db_session)
        await service.create(
            issue_id=created_issue.id,
            data=CodeArtifactCreate(artifact_type=ArtifactType.FILE, identifier="a.py"),
        )
        await service.create(
            issue_id=created_issue.id,
            data=CodeArtifactCreate(artifact_type=ArtifactType.COMMIT, identifier="sha1"),
        )
        artifacts = await service.list_by_issue(created_issue.id)
        assert len(artifacts) == 2

    @pytest.mark.asyncio
    async def test_get_artifact(self, db_session, created_issue: Issue):
        service = CodeArtifactService(db_session)
        created = await service.create(
            issue_id=created_issue.id,
            data=CodeArtifactCreate(artifact_type=ArtifactType.FILE, identifier="b.py"),
        )
        found = await service.get(created.id)
        assert found is not None
        assert found.id == created.id

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self, db_session):
        service = CodeArtifactService(db_session)
        result = await service.get(uuid.uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_artifact(self, db_session, created_issue: Issue):
        service = CodeArtifactService(db_session)
        created = await service.create(
            issue_id=created_issue.id,
            data=CodeArtifactCreate(artifact_type=ArtifactType.FILE, identifier="c.py"),
        )
        deleted = await service.delete(created.id)
        assert deleted is True
        assert await service.get(created.id) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_returns_false(self, db_session):
        service = CodeArtifactService(db_session)
        result = await service.delete(uuid.uuid4())
        assert result is False

    @pytest.mark.asyncio
    async def test_create_for_nonexistent_issue_raises(self, db_session):
        service = CodeArtifactService(db_session)
        with pytest.raises(ValueError, match="Issue not found"):
            await service.create(
                issue_id=uuid.uuid4(),
                data=CodeArtifactCreate(
                    artifact_type=ArtifactType.FILE,
                    identifier="x.py",
                ),
            )


class TestCodeArtifactAPI:
    @pytest.mark.asyncio
    async def test_create_artifact_endpoint(self, db_session, created_issue: Issue):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                f"/api/v1/issues/{created_issue.id}/artifacts",
                json={
                    "artifact_type": "file",
                    "identifier": "src/main.py",
                },
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["artifact_type"] == "file"
        assert data["identifier"] == "src/main.py"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_commit_auto_transition(self, db_session, created_issue: Issue):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                f"/api/v1/issues/{created_issue.id}/artifacts",
                json={
                    "artifact_type": "commit",
                    "identifier": "abc123def",
                    "metadata_": {"branch": "main"},
                },
            )
        assert resp.status_code == 201
        result = await db_session.execute(
            select(Issue).where(Issue.id == created_issue.id)
        )
        issue = result.scalar_one()
        assert issue.status == IssueStatus.IN_REVIEW

    @pytest.mark.asyncio
    async def test_list_artifacts_endpoint(self, db_session, created_issue: Issue):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.post(
                f"/api/v1/issues/{created_issue.id}/artifacts",
                json={"artifact_type": "file", "identifier": "a.py"},
            )
            resp = await client.get(
                f"/api/v1/issues/{created_issue.id}/artifacts"
            )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    @pytest.mark.asyncio
    async def test_get_artifact_endpoint(self, db_session, created_issue: Issue):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            create_resp = await client.post(
                f"/api/v1/issues/{created_issue.id}/artifacts",
                json={"artifact_type": "file", "identifier": "a.py"},
            )
            artifact_id = create_resp.json()["id"]
            resp = await client.get(
                f"/api/v1/issues/{created_issue.id}/artifacts/{artifact_id}"
            )
        assert resp.status_code == 200
        assert resp.json()["identifier"] == "a.py"

    @pytest.mark.asyncio
    async def test_get_artifact_not_found(self, db_session, created_issue: Issue):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session

        fake_id = uuid.uuid4()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                f"/api/v1/issues/{created_issue.id}/artifacts/{fake_id}"
            )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_artifact_endpoint(self, db_session, created_issue: Issue):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            create_resp = await client.post(
                f"/api/v1/issues/{created_issue.id}/artifacts",
                json={"artifact_type": "file", "identifier": "d.py"},
            )
            artifact_id = create_resp.json()["id"]
            resp = await client.delete(
                f"/api/v1/issues/{created_issue.id}/artifacts/{artifact_id}"
            )
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_artifact_not_found(self, db_session, created_issue: Issue):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session

        fake_id = uuid.uuid4()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.delete(
                f"/api/v1/issues/{created_issue.id}/artifacts/{fake_id}"
            )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_create_artifact_issue_not_found(self, db_session):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session

        fake_id = uuid.uuid4()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                f"/api/v1/issues/{fake_id}/artifacts",
                json={"artifact_type": "file", "identifier": "x.py"},
            )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_create_artifact_invalid_type(self, db_session, created_issue: Issue):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                f"/api/v1/issues/{created_issue.id}/artifacts",
                json={"artifact_type": "invalid", "identifier": "x.py"},
            )
        assert resp.status_code == 422
