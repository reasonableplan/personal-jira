import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


pytestmark = pytest.mark.asyncio(mode="auto")


async def _create_issue(client: AsyncClient, title: str) -> dict:
    resp = await client.post("/api/v1/issues", json={"title": title})
    assert resp.status_code == 201
    return resp.json()


class TestBulkStatusUpdate:

    async def test_bulk_transition_multiple_issues(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        issues = []
        for i in range(3):
            issue = await _create_issue(client, f"Bulk Issue {i}")
            issues.append(issue)

        ids = [i["id"] for i in issues]
        resp = await client.post(
            "/api/v1/issues/bulk/transition",
            json={"issue_ids": ids, "to_status": "Ready"},
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["success_count"] == 3
        assert result["failure_count"] == 0

        for issue_id in ids:
            r = await client.get(f"/api/v1/issues/{issue_id}")
            assert r.json()["status"] == "Ready"

    async def test_bulk_transition_partial_failure(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        issue_backlog = await _create_issue(client, "Backlog Issue")
        issue_ready = await _create_issue(client, "Ready Issue")
        await client.post(
            f"/api/v1/issues/{issue_ready['id']}/transition",
            json={"to_status": "Ready"},
        )

        resp = await client.post(
            "/api/v1/issues/bulk/transition",
            json={
                "issue_ids": [issue_backlog["id"], issue_ready["id"]],
                "to_status": "Ready",
            },
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["success_count"] >= 1

    async def test_bulk_transition_empty_list(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        resp = await client.post(
            "/api/v1/issues/bulk/transition",
            json={"issue_ids": [], "to_status": "Ready"},
        )
        assert resp.status_code in (200, 422)

    async def test_bulk_transition_nonexistent_ids(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        fake_id = str(uuid.uuid4()) if True else ""
        resp = await client.post(
            "/api/v1/issues/bulk/transition",
            json={"issue_ids": [fake_id], "to_status": "Ready"},
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["failure_count"] == 1


class TestBulkPriorityUpdate:

    async def test_bulk_priority_change(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        issues = [await _create_issue(client, f"P-Issue {i}") for i in range(3)]
        ids = [i["id"] for i in issues]

        resp = await client.post(
            "/api/v1/issues/bulk/priority",
            json={"issue_ids": ids, "priority": "High"},
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["success_count"] == 3

        for issue_id in ids:
            r = await client.get(f"/api/v1/issues/{issue_id}")
            assert r.json()["priority"] == "High"


class TestBulkWithDependencyRelease:

    async def test_bulk_done_triggers_dependency_release(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        blocker_a = await _create_issue(client, "Blocker A")
        blocker_b = await _create_issue(client, "Blocker B")
        blocked = await _create_issue(client, "Blocked")

        await client.post(
            f"/api/v1/issues/{blocked['id']}/dependencies",
            json={"blocker_id": blocker_a["id"]},
        )
        await client.post(
            f"/api/v1/issues/{blocked['id']}/dependencies",
            json={"blocker_id": blocker_b["id"]},
        )

        for bid in [blocker_a["id"], blocker_b["id"]]:
            await client.post(
                f"/api/v1/issues/{bid}/transition",
                json={"to_status": "Ready"},
            )
            await client.post(
                f"/api/v1/issues/{bid}/transition",
                json={"to_status": "InProgress"},
            )

        resp = await client.post(
            "/api/v1/issues/bulk/transition",
            json={
                "issue_ids": [blocker_a["id"], blocker_b["id"]],
                "to_status": "Done",
            },
        )
        assert resp.status_code == 200

        blocked_data = await client.get(f"/api/v1/issues/{blocked['id']}")
        assert blocked_data.json()["status"] == "Ready"
