from __future__ import annotations

import uuid
from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue, IssueStatus

pytestmark = pytest.mark.asyncio(mode="auto")

API_V1 = "/api/v1"
ISSUES_URL = f"{API_V1}/issues"
AGENT_ID = "agent-backend-test"


def _issue_payload(**overrides: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "title": f"lifecycle-test-{uuid.uuid4().hex[:8]}",
        "description": "Integration test issue for full lifecycle",
        "priority": "high",
        "issue_type": "task",
    }
    defaults.update(overrides)
    return defaults


def _worklog_payload(**overrides: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "agent_id": AGENT_ID,
        "message": "Completed implementation",
        "duration_minutes": 30,
    }
    defaults.update(overrides)
    return defaults


def _artifact_payload(**overrides: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "agent_id": AGENT_ID,
        "artifact_type": "code",
        "path": "src/personal_jira/services/example.py",
        "description": "New service implementation",
    }
    defaults.update(overrides)
    return defaults


class TestIssueLifecycle:
    """Full lifecycle: create -> claim -> work log -> artifact -> review -> done."""

    async def test_full_lifecycle_happy_path(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # 1. Create issue
        resp = await client.post(ISSUES_URL, json=_issue_payload())
        assert resp.status_code == 201, resp.text
        issue = resp.json()
        issue_id: str = issue["id"]
        assert issue["status"] == IssueStatus.BACKLOG.value

        # 2. Transition BACKLOG -> TODO
        resp = await client.post(
            f"{ISSUES_URL}/{issue_id}/transition",
            json={"status": IssueStatus.TODO.value},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == IssueStatus.TODO.value

        # 3. Agent claims the issue
        resp = await client.post(
            f"{ISSUES_URL}/claim",
            json={"agent_id": AGENT_ID},
        )
        assert resp.status_code == 200, resp.text
        claimed = resp.json()
        assert claimed["id"] == issue_id
        assert claimed["status"] == IssueStatus.IN_PROGRESS.value
        assert claimed["assignee"] == AGENT_ID

        # 4. Add work log
        resp = await client.post(
            f"{ISSUES_URL}/{issue_id}/worklogs",
            json=_worklog_payload(),
        )
        assert resp.status_code == 201, resp.text
        worklog = resp.json()
        assert worklog["issue_id"] == issue_id
        assert worklog["agent_id"] == AGENT_ID

        # 5. Add artifact
        resp = await client.post(
            f"{ISSUES_URL}/{issue_id}/artifacts",
            json=_artifact_payload(),
        )
        assert resp.status_code == 201, resp.text
        artifact = resp.json()
        assert artifact["issue_id"] == issue_id
        assert artifact["artifact_type"] == "code"

        # 6. Transition IN_PROGRESS -> IN_REVIEW
        resp = await client.post(
            f"{ISSUES_URL}/{issue_id}/transition",
            json={"status": IssueStatus.IN_REVIEW.value},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == IssueStatus.IN_REVIEW.value

        # 7. Transition IN_REVIEW -> DONE
        resp = await client.post(
            f"{ISSUES_URL}/{issue_id}/transition",
            json={"status": IssueStatus.DONE.value},
        )
        assert resp.status_code == 200, resp.text
        final = resp.json()
        assert final["status"] == IssueStatus.DONE.value

        # 8. Verify final state via GET
        resp = await client.get(f"{ISSUES_URL}/{issue_id}")
        assert resp.status_code == 200
        result = resp.json()
        assert result["status"] == IssueStatus.DONE.value
        assert result["assignee"] == AGENT_ID

    async def test_claim_returns_204_when_no_eligible_issues(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(
            f"{ISSUES_URL}/claim",
            json={"agent_id": "agent-no-work"},
        )
        assert resp.status_code == 204

    async def test_invalid_transition_returns_422(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(ISSUES_URL, json=_issue_payload())
        assert resp.status_code == 201
        issue_id = resp.json()["id"]

        # BACKLOG -> DONE is not allowed
        resp = await client.post(
            f"{ISSUES_URL}/{issue_id}/transition",
            json={"status": IssueStatus.DONE.value},
        )
        assert resp.status_code == 422
        body = resp.json()
        assert "detail" in body

    async def test_worklog_on_non_in_progress_issue_rejected(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(ISSUES_URL, json=_issue_payload())
        assert resp.status_code == 201
        issue_id = resp.json()["id"]

        # Issue is BACKLOG, work logs should be rejected
        resp = await client.post(
            f"{ISSUES_URL}/{issue_id}/worklogs",
            json=_worklog_payload(),
        )
        assert resp.status_code in (400, 409, 422)

    async def test_artifact_on_non_in_progress_issue_rejected(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(ISSUES_URL, json=_issue_payload())
        assert resp.status_code == 201
        issue_id = resp.json()["id"]

        resp = await client.post(
            f"{ISSUES_URL}/{issue_id}/artifacts",
            json=_artifact_payload(),
        )
        assert resp.status_code in (400, 409, 422)

    async def test_cannot_transition_done_issue(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        # Create and drive to DONE
        resp = await client.post(ISSUES_URL, json=_issue_payload())
        issue_id = resp.json()["id"]

        for target in (
            IssueStatus.TODO.value,
            IssueStatus.IN_PROGRESS.value,
            IssueStatus.IN_REVIEW.value,
            IssueStatus.DONE.value,
        ):
            resp = await client.post(
                f"{ISSUES_URL}/{issue_id}/transition",
                json={"status": target},
            )
            assert resp.status_code == 200, (
                f"Transition to {target} failed: {resp.text}"
            )

        # DONE -> anything should fail
        for target in (
            IssueStatus.BACKLOG.value,
            IssueStatus.TODO.value,
            IssueStatus.IN_PROGRESS.value,
        ):
            resp = await client.post(
                f"{ISSUES_URL}/{issue_id}/transition",
                json={"status": target},
            )
            assert resp.status_code == 422, (
                f"DONE -> {target} should be rejected"
            )

    async def test_concurrent_claims_only_one_succeeds(
        self, client: AsyncClient
    ) -> None:
        import asyncio

        # Create two TODO issues
        for _ in range(2):
            resp = await client.post(ISSUES_URL, json=_issue_payload())
            issue_id = resp.json()["id"]
            await client.post(
                f"{ISSUES_URL}/{issue_id}/transition",
                json={"status": IssueStatus.TODO.value},
            )

        # Fire 5 concurrent claims
        results = await asyncio.gather(
            *[
                client.post(
                    f"{ISSUES_URL}/claim",
                    json={"agent_id": f"agent-{i}"},
                )
                for i in range(5)
            ]
        )

        success = [r for r in results if r.status_code == 200]
        no_content = [r for r in results if r.status_code == 204]
        assert len(success) == 2
        assert len(no_content) == 3

        # All successful claims should be unique issues
        claimed_ids = [r.json()["id"] for r in success]
        assert len(set(claimed_ids)) == 2

    async def test_get_worklogs_and_artifacts_after_lifecycle(
        self, client: AsyncClient
    ) -> None:
        # Create -> TODO -> claim -> add worklog + artifact
        resp = await client.post(ISSUES_URL, json=_issue_payload())
        issue_id = resp.json()["id"]

        await client.post(
            f"{ISSUES_URL}/{issue_id}/transition",
            json={"status": IssueStatus.TODO.value},
        )
        await client.post(
            f"{ISSUES_URL}/claim",
            json={"agent_id": AGENT_ID},
        )

        await client.post(
            f"{ISSUES_URL}/{issue_id}/worklogs",
            json=_worklog_payload(message="Step 1"),
        )
        await client.post(
            f"{ISSUES_URL}/{issue_id}/worklogs",
            json=_worklog_payload(message="Step 2"),
        )
        await client.post(
            f"{ISSUES_URL}/{issue_id}/artifacts",
            json=_artifact_payload(path="src/a.py"),
        )

        # Verify GET endpoints
        resp = await client.get(f"{ISSUES_URL}/{issue_id}/worklogs")
        assert resp.status_code == 200
        worklogs = resp.json()
        assert len(worklogs) == 2

        resp = await client.get(f"{ISSUES_URL}/{issue_id}/artifacts")
        assert resp.status_code == 200
        artifacts = resp.json()
        assert len(artifacts) == 1
