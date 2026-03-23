import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue, IssueStatus, IssuePriority
from personal_jira.models.dependency import IssueDependency


pytestmark = pytest.mark.asyncio(mode="auto")


async def _create_issue(
    client: AsyncClient,
    title: str,
    status: str = "Backlog",
    priority: str = "Medium",
) -> dict:
    resp = await client.post(
        "/api/v1/issues",
        json={"title": title, "priority": priority},
    )
    assert resp.status_code == 201
    data = resp.json()
    if status != "Backlog":
        tr = await client.post(
            f"/api/v1/issues/{data['id']}/transition",
            json={"to_status": status},
        )
        assert tr.status_code == 200
    return data


async def _add_dependency(
    client: AsyncClient, blocked_id: str, blocker_id: str
) -> dict:
    resp = await client.post(
        f"/api/v1/issues/{blocked_id}/dependencies",
        json={"blocker_id": blocker_id},
    )
    assert resp.status_code == 201
    return resp.json()


async def _transition(client: AsyncClient, issue_id: str, to_status: str) -> dict:
    resp = await client.post(
        f"/api/v1/issues/{issue_id}/transition",
        json={"to_status": to_status},
    )
    return resp.json()


async def _get_issue(client: AsyncClient, issue_id: str) -> dict:
    resp = await client.get(f"/api/v1/issues/{issue_id}")
    assert resp.status_code == 200
    return resp.json()


class TestDependencyChainRelease:
    """A→B→C chain: completing A releases B, completing B releases C."""

    async def test_linear_chain_release(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(client, "Blocker A")
        b = await _create_issue(client, "Middle B")
        c = await _create_issue(client, "Leaf C")

        await _add_dependency(client, blocked_id=b["id"], blocker_id=a["id"])
        await _add_dependency(client, blocked_id=c["id"], blocker_id=b["id"])

        # Transition A: Backlog → Ready → InProgress → Done
        await _transition(client, a["id"], "Ready")
        await _transition(client, a["id"], "InProgress")
        resp = await client.post(
            f"/api/v1/issues/{a['id']}/transition",
            json={"to_status": "Done"},
        )
        assert resp.status_code == 200

        b_data = await _get_issue(client, b["id"])
        assert b_data["status"] == "Ready"

        c_data = await _get_issue(client, c["id"])
        assert c_data["status"] == "Backlog"

        # Now complete B
        await _transition(client, b["id"], "InProgress")
        resp = await client.post(
            f"/api/v1/issues/{b['id']}/transition",
            json={"to_status": "Done"},
        )
        assert resp.status_code == 200

        c_data = await _get_issue(client, c["id"])
        assert c_data["status"] == "Ready"

    async def test_multiple_blockers_partial_completion(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(client, "Blocker A")
        b = await _create_issue(client, "Blocker B")
        c = await _create_issue(client, "Blocked C")

        await _add_dependency(client, blocked_id=c["id"], blocker_id=a["id"])
        await _add_dependency(client, blocked_id=c["id"], blocker_id=b["id"])

        # Complete A only
        await _transition(client, a["id"], "Ready")
        await _transition(client, a["id"], "InProgress")
        await client.post(
            f"/api/v1/issues/{a['id']}/transition",
            json={"to_status": "Done"},
        )

        c_data = await _get_issue(client, c["id"])
        assert c_data["status"] == "Backlog", "Should stay Backlog when not all blockers Done"

        # Complete B
        await _transition(client, b["id"], "Ready")
        await _transition(client, b["id"], "InProgress")
        await client.post(
            f"/api/v1/issues/{b['id']}/transition",
            json={"to_status": "Done"},
        )

        c_data = await _get_issue(client, c["id"])
        assert c_data["status"] == "Ready", "Should become Ready when all blockers Done"

    async def test_diamond_dependency_release(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Diamond: A blocks B and C, both B and C block D."""
        a = await _create_issue(client, "Root A")
        b = await _create_issue(client, "Mid B")
        c = await _create_issue(client, "Mid C")
        d = await _create_issue(client, "Leaf D")

        await _add_dependency(client, blocked_id=b["id"], blocker_id=a["id"])
        await _add_dependency(client, blocked_id=c["id"], blocker_id=a["id"])
        await _add_dependency(client, blocked_id=d["id"], blocker_id=b["id"])
        await _add_dependency(client, blocked_id=d["id"], blocker_id=c["id"])

        # Complete A → B and C become Ready
        await _transition(client, a["id"], "Ready")
        await _transition(client, a["id"], "InProgress")
        await client.post(
            f"/api/v1/issues/{a['id']}/transition",
            json={"to_status": "Done"},
        )

        b_data = await _get_issue(client, b["id"])
        c_data = await _get_issue(client, c["id"])
        d_data = await _get_issue(client, d["id"])
        assert b_data["status"] == "Ready"
        assert c_data["status"] == "Ready"
        assert d_data["status"] == "Backlog"

        # Complete B → D still blocked by C
        await _transition(client, b["id"], "InProgress")
        await client.post(
            f"/api/v1/issues/{b['id']}/transition",
            json={"to_status": "Done"},
        )
        d_data = await _get_issue(client, d["id"])
        assert d_data["status"] == "Backlog"

        # Complete C → D released
        await _transition(client, c["id"], "InProgress")
        await client.post(
            f"/api/v1/issues/{c['id']}/transition",
            json={"to_status": "Done"},
        )
        d_data = await _get_issue(client, d["id"])
        assert d_data["status"] == "Ready"

    async def test_non_backlog_blocked_not_transitioned(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(client, "Blocker")
        b = await _create_issue(client, "Already Ready", status="Ready")

        await _add_dependency(client, blocked_id=b["id"], blocker_id=a["id"])

        await _transition(client, a["id"], "Ready")
        await _transition(client, a["id"], "InProgress")
        await client.post(
            f"/api/v1/issues/{a['id']}/transition",
            json={"to_status": "Done"},
        )

        b_data = await _get_issue(client, b["id"])
        assert b_data["status"] == "Ready", "Non-Backlog issue should not be re-transitioned"

    async def test_no_dependencies_no_side_effects(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(client, "Standalone")

        await _transition(client, a["id"], "Ready")
        await _transition(client, a["id"], "InProgress")
        resp = await client.post(
            f"/api/v1/issues/{a['id']}/transition",
            json={"to_status": "Done"},
        )
        assert resp.status_code == 200


class TestBulkDependencyRelease:

    async def test_single_blocker_releases_many(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        blocker = await _create_issue(client, "Single Blocker")
        blocked_ids = []
        for i in range(5):
            issue = await _create_issue(client, f"Blocked {i}")
            await _add_dependency(
                client, blocked_id=issue["id"], blocker_id=blocker["id"]
            )
            blocked_ids.append(issue["id"])

        await _transition(client, blocker["id"], "Ready")
        await _transition(client, blocker["id"], "InProgress")
        await client.post(
            f"/api/v1/issues/{blocker['id']}/transition",
            json={"to_status": "Done"},
        )

        for bid in blocked_ids:
            data = await _get_issue(client, bid)
            assert data["status"] == "Ready", f"Issue {bid} should be Ready"
