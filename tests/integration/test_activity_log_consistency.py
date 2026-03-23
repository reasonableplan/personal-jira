import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


pytestmark = pytest.mark.asyncio(mode="auto")

import uuid  # noqa: E402


async def _create_issue(client: AsyncClient, title: str) -> dict:
    resp = await client.post("/api/v1/issues", json={"title": title})
    assert resp.status_code == 201
    return resp.json()


async def _get_activity_log(client: AsyncClient, issue_id: str) -> list[dict]:
    resp = await client.get(f"/api/v1/issues/{issue_id}/activity")
    assert resp.status_code == 200
    return resp.json()


class TestTransitionActivityLog:

    async def test_transition_creates_log_entry(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        issue = await _create_issue(client, "Log Test")

        await client.post(
            f"/api/v1/issues/{issue['id']}/transition",
            json={"to_status": "Ready"},
        )

        logs = await _get_activity_log(client, issue["id"])
        transition_logs = [
            log for log in logs if log.get("action") == "transition"
        ]
        assert len(transition_logs) >= 1
        latest = transition_logs[-1]
        assert latest["from_status"] == "Backlog"
        assert latest["to_status"] == "Ready"

    async def test_multiple_transitions_ordered(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        issue = await _create_issue(client, "Multi Trans")

        await client.post(
            f"/api/v1/issues/{issue['id']}/transition",
            json={"to_status": "Ready"},
        )
        await client.post(
            f"/api/v1/issues/{issue['id']}/transition",
            json={"to_status": "InProgress"},
        )

        logs = await _get_activity_log(client, issue["id"])
        transition_logs = [
            log for log in logs if log.get("action") == "transition"
        ]
        assert len(transition_logs) >= 2

        statuses = [(l["from_status"], l["to_status"]) for l in transition_logs]
        assert ("Backlog", "Ready") in statuses
        assert ("Ready", "InProgress") in statuses


class TestDependencyActivityLog:

    async def test_add_dependency_creates_log(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(client, "Blocker")
        b = await _create_issue(client, "Blocked")

        await client.post(
            f"/api/v1/issues/{b['id']}/dependencies",
            json={"blocker_id": a["id"]},
        )

        logs = await _get_activity_log(client, b["id"])
        dep_logs = [
            log for log in logs if log.get("action") in ("dependency_added", "add_dependency")
        ]
        assert len(dep_logs) >= 1

    async def test_remove_dependency_creates_log(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(client, "Blocker")
        b = await _create_issue(client, "Blocked")

        await client.post(
            f"/api/v1/issues/{b['id']}/dependencies",
            json={"blocker_id": a["id"]},
        )
        await client.delete(
            f"/api/v1/issues/{b['id']}/dependencies/{a['id']}",
        )

        logs = await _get_activity_log(client, b["id"])
        remove_logs = [
            log for log in logs
            if log.get("action") in ("dependency_removed", "remove_dependency")
        ]
        assert len(remove_logs) >= 1


class TestAutoReleaseActivityLog:

    async def test_auto_release_creates_log(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        blocker = await _create_issue(client, "Blocker")
        blocked = await _create_issue(client, "Blocked")

        await client.post(
            f"/api/v1/issues/{blocked['id']}/dependencies",
            json={"blocker_id": blocker["id"]},
        )

        await client.post(
            f"/api/v1/issues/{blocker['id']}/transition",
            json={"to_status": "Ready"},
        )
        await client.post(
            f"/api/v1/issues/{blocker['id']}/transition",
            json={"to_status": "InProgress"},
        )
        await client.post(
            f"/api/v1/issues/{blocker['id']}/transition",
            json={"to_status": "Done"},
        )

        blocked_data = await client.get(f"/api/v1/issues/{blocked['id']}")
        assert blocked_data.json()["status"] == "Ready"

        logs = await _get_activity_log(client, blocked["id"])
        auto_logs = [
            log for log in logs
            if log.get("action") in ("auto_release", "transition", "dependency_released")
            and log.get("to_status") == "Ready"
        ]
        assert len(auto_logs) >= 1, "Auto-release transition must be logged"

    async def test_chain_release_logs_all_transitions(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(client, "A")
        b = await _create_issue(client, "B")
        c = await _create_issue(client, "C")

        await client.post(
            f"/api/v1/issues/{b['id']}/dependencies",
            json={"blocker_id": a["id"]},
        )
        await client.post(
            f"/api/v1/issues/{c['id']}/dependencies",
            json={"blocker_id": b["id"]},
        )

        # Complete A
        await client.post(
            f"/api/v1/issues/{a['id']}/transition",
            json={"to_status": "Ready"},
        )
        await client.post(
            f"/api/v1/issues/{a['id']}/transition",
            json={"to_status": "InProgress"},
        )
        await client.post(
            f"/api/v1/issues/{a['id']}/transition",
            json={"to_status": "Done"},
        )

        b_logs = await _get_activity_log(client, b["id"])
        assert any(
            log.get("to_status") == "Ready"
            for log in b_logs
            if log.get("action") in ("auto_release", "transition", "dependency_released")
        ), "B should have auto-release log entry"

        # Complete B
        await client.post(
            f"/api/v1/issues/{b['id']}/transition",
            json={"to_status": "InProgress"},
        )
        await client.post(
            f"/api/v1/issues/{b['id']}/transition",
            json={"to_status": "Done"},
        )

        c_logs = await _get_activity_log(client, c["id"])
        assert any(
            log.get("to_status") == "Ready"
            for log in c_logs
            if log.get("action") in ("auto_release", "transition", "dependency_released")
        ), "C should have auto-release log entry"


class TestBulkActivityLog:

    async def test_bulk_transition_logs_each_issue(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        issues = [await _create_issue(client, f"Bulk {i}") for i in range(3)]
        ids = [i["id"] for i in issues]

        await client.post(
            "/api/v1/issues/bulk/transition",
            json={"issue_ids": ids, "to_status": "Ready"},
        )

        for issue_id in ids:
            logs = await _get_activity_log(client, issue_id)
            transition_logs = [
                log for log in logs if log.get("action") == "transition"
            ]
            assert len(transition_logs) >= 1, (
                f"Issue {issue_id} must have transition activity log"
            )

    async def test_bulk_done_with_dependency_logs_both(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        blocker = await _create_issue(client, "Blocker")
        blocked = await _create_issue(client, "Blocked")

        await client.post(
            f"/api/v1/issues/{blocked['id']}/dependencies",
            json={"blocker_id": blocker["id"]},
        )

        await client.post(
            f"/api/v1/issues/{blocker['id']}/transition",
            json={"to_status": "Ready"},
        )
        await client.post(
            f"/api/v1/issues/{blocker['id']}/transition",
            json={"to_status": "InProgress"},
        )

        await client.post(
            "/api/v1/issues/bulk/transition",
            json={"issue_ids": [blocker["id"]], "to_status": "Done"},
        )

        blocker_logs = await _get_activity_log(client, blocker["id"])
        assert any(
            log.get("to_status") == "Done" for log in blocker_logs
            if log.get("action") == "transition"
        )

        blocked_logs = await _get_activity_log(client, blocked["id"])
        assert any(
            log.get("to_status") == "Ready" for log in blocked_logs
            if log.get("action") in ("auto_release", "transition", "dependency_released")
        ), "Blocked issue must have auto-release activity log"
