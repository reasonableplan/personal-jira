from __future__ import annotations

from uuid import UUID

import pytest
import pytest_asyncio
from httpx import AsyncClient

API_V1 = "/api/v1"


@pytest.mark.asyncio
class TestIssueLifecycleE2E:
    """E2E: 이슈 생성 → 에이전트 선점 → 상태 전이(완료) → 대시보드 반영"""

    async def test_full_lifecycle_create_claim_complete_dashboard(
        self, client: AsyncClient
    ) -> None:
        # Step 1: 이슈 생성
        create_payload = {
            "title": "E2E 테스트 이슈",
            "description": "풀스택 시나리오 검증용",
            "priority": "high",
            "issue_type": "task",
        }
        resp = await client.post(f"{API_V1}/issues", json=create_payload)
        assert resp.status_code == 201
        issue = resp.json()
        issue_id: str = issue["id"]
        assert UUID(issue_id)
        assert issue["title"] == create_payload["title"]
        assert issue["status"] == "backlog"

        # Step 2: Backlog → Ready 전이
        resp = await client.post(
            f"{API_V1}/issues/{issue_id}/transition",
            json={"status": "ready"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ready"

        # Step 3: 에이전트 선점 (claim)
        resp = await client.post(
            f"{API_V1}/issues/claim",
            json={"agent_id": "agent-backend-01"},
        )
        assert resp.status_code == 200
        claimed = resp.json()
        assert claimed["id"] == issue_id
        assert claimed["status"] == "in_progress"
        assert claimed["assignee"] == "agent-backend-01"

        # Step 4: InProgress → InReview 전이
        resp = await client.post(
            f"{API_V1}/issues/{issue_id}/transition",
            json={"status": "in_review"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "in_review"

        # Step 5: InReview → Done 전이
        resp = await client.post(
            f"{API_V1}/issues/{issue_id}/transition",
            json={"status": "done"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "done"

        # Step 6: 대시보드에서 완료 이슈 반영 확인
        resp = await client.get(f"{API_V1}/dashboard")
        assert resp.status_code == 200
        dashboard = resp.json()
        assert dashboard["total"] >= 1
        assert dashboard["by_status"]["done"] >= 1

        # Step 7: 개별 이슈 조회로 최종 상태 확인
        resp = await client.get(f"{API_V1}/issues/{issue_id}")
        assert resp.status_code == 200
        final = resp.json()
        assert final["status"] == "done"
        assert final["assignee"] == "agent-backend-01"

    async def test_claim_no_ready_issues_returns_204(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(
            f"{API_V1}/issues/claim",
            json={"agent_id": "agent-idle"},
        )
        assert resp.status_code == 204

    async def test_invalid_transition_returns_422(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(
            f"{API_V1}/issues",
            json={"title": "전이 실패 테스트", "priority": "low", "issue_type": "bug"},
        )
        assert resp.status_code == 201
        issue_id = resp.json()["id"]

        # Backlog → Done 은 허용되지 않음
        resp = await client.post(
            f"{API_V1}/issues/{issue_id}/transition",
            json={"status": "done"},
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestDependencyE2E:
    """E2E: 이슈 의존성 + 자동 해제 시나리오"""

    async def test_dependency_blocks_then_auto_release(
        self, client: AsyncClient
    ) -> None:
        # 선행 이슈 생성
        resp = await client.post(
            f"{API_V1}/issues",
            json={"title": "선행 이슈", "priority": "high", "issue_type": "task"},
        )
        assert resp.status_code == 201
        blocker_id = resp.json()["id"]

        # 후행 이슈 생성
        resp = await client.post(
            f"{API_V1}/issues",
            json={"title": "후행 이슈", "priority": "medium", "issue_type": "task"},
        )
        assert resp.status_code == 201
        blocked_id = resp.json()["id"]

        # 의존성 등록: 후행 blocked-by 선행
        resp = await client.post(
            f"{API_V1}/issues/{blocked_id}/dependencies",
            json={"blocker_id": blocker_id, "type": "blocked_by"},
        )
        assert resp.status_code == 201

        # 의존성 조회
        resp = await client.get(f"{API_V1}/issues/{blocked_id}/dependencies")
        assert resp.status_code == 200
        deps = resp.json()
        assert len(deps) >= 1
        assert any(d["blocker_id"] == blocker_id for d in deps)

        # 선행 이슈를 Done으로 전이: Backlog → Ready → InProgress → InReview → Done
        for status in ["ready", "in_progress", "in_review", "done"]:
            resp = await client.post(
                f"{API_V1}/issues/{blocker_id}/transition",
                json={"status": status},
            )
            assert resp.status_code == 200

        # 후행 이슈가 자동으로 Backlog → Ready 전이되었는지 확인
        resp = await client.get(f"{API_V1}/issues/{blocked_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ready"

    async def test_circular_dependency_rejected(
        self, client: AsyncClient
    ) -> None:
        resp_a = await client.post(
            f"{API_V1}/issues",
            json={"title": "이슈 A", "priority": "low", "issue_type": "task"},
        )
        resp_b = await client.post(
            f"{API_V1}/issues",
            json={"title": "이슈 B", "priority": "low", "issue_type": "task"},
        )
        id_a = resp_a.json()["id"]
        id_b = resp_b.json()["id"]

        # A blocked-by B
        resp = await client.post(
            f"{API_V1}/issues/{id_a}/dependencies",
            json={"blocker_id": id_b, "type": "blocked_by"},
        )
        assert resp.status_code == 201

        # B blocked-by A → 순환 의존성 거부
        resp = await client.post(
            f"{API_V1}/issues/{id_b}/dependencies",
            json={"blocker_id": id_a, "type": "blocked_by"},
        )
        assert resp.status_code == 409


@pytest.mark.asyncio
class TestDashboardE2E:
    """E2E: 대시보드 집계 시나리오"""

    async def test_dashboard_reflects_multiple_issues(
        self, client: AsyncClient
    ) -> None:
        # 여러 이슈 생성
        for i in range(3):
            resp = await client.post(
                f"{API_V1}/issues",
                json={
                    "title": f"대시보드 이슈 {i}",
                    "priority": "medium",
                    "issue_type": "task",
                },
            )
            assert resp.status_code == 201

        # 첫 번째 이슈를 Ready로 전이
        resp = await client.get(f"{API_V1}/issues")
        issues = resp.json()
        first_id = issues["items"][0]["id"] if "items" in issues else issues[0]["id"]

        await client.post(
            f"{API_V1}/issues/{first_id}/transition",
            json={"status": "ready"},
        )

        resp = await client.get(f"{API_V1}/dashboard")
        assert resp.status_code == 200
        dashboard = resp.json()
        assert dashboard["total"] == 3
        assert dashboard["by_status"]["backlog"] == 2
        assert dashboard["by_status"]["ready"] == 1

    async def test_dashboard_empty_state(
        self, client: AsyncClient
    ) -> None:
        resp = await client.get(f"{API_V1}/dashboard")
        assert resp.status_code == 200
        dashboard = resp.json()
        assert dashboard["total"] == 0
        assert all(v == 0 for v in dashboard["by_status"].values())
