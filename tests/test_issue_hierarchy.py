import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.personal_jira.models.enums import IssuePriority, IssueStatus, IssueType
from src.personal_jira.models.issue import Issue

API_BASE = "/api/v1/issues"


class TestIssueHierarchyModel:
    async def test_parent_child_relationship(
        self, db_session: AsyncSession, sample_epic: Issue, sample_story: Issue
    ) -> None:
        result = await db_session.execute(
            select(Issue).where(Issue.parent_id == sample_epic.id)
        )
        children = result.scalars().all()
        assert len(children) == 1
        assert children[0].id == sample_story.id

    async def test_three_level_hierarchy(
        self,
        db_session: AsyncSession,
        sample_epic: Issue,
        sample_story: Issue,
        sample_task: Issue,
    ) -> None:
        assert sample_story.parent_id == sample_epic.id
        assert sample_task.parent_id == sample_story.id

        result = await db_session.execute(
            select(Issue).where(Issue.parent_id == sample_story.id)
        )
        tasks = result.scalars().all()
        assert len(tasks) == 1
        assert tasks[0].id == sample_task.id

    async def test_issue_without_parent(self, db_session: AsyncSession) -> None:
        issue = Issue(
            id=uuid.uuid4(),
            title="Standalone Issue",
            issue_type=IssueType.TASK,
            status=IssueStatus.TODO,
            priority=IssuePriority.MEDIUM,
        )
        db_session.add(issue)
        await db_session.commit()
        await db_session.refresh(issue)
        assert issue.parent_id is None

    async def test_multiple_children(
        self, db_session: AsyncSession, sample_epic: Issue
    ) -> None:
        children_ids = []
        for i in range(3):
            child = Issue(
                id=uuid.uuid4(),
                title=f"Child {i}",
                issue_type=IssueType.STORY,
                status=IssueStatus.TODO,
                priority=IssuePriority.MEDIUM,
                parent_id=sample_epic.id,
            )
            db_session.add(child)
            children_ids.append(child.id)
        await db_session.commit()

        result = await db_session.execute(
            select(Issue).where(Issue.parent_id == sample_epic.id)
        )
        children = result.scalars().all()
        assert len(children) == 3
        assert {c.id for c in children} == set(children_ids)

    async def test_subtask_under_task(
        self, db_session: AsyncSession, sample_task: Issue
    ) -> None:
        subtask = Issue(
            id=uuid.uuid4(),
            title="Subtask",
            issue_type=IssueType.SUBTASK,
            status=IssueStatus.BACKLOG,
            priority=IssuePriority.LOW,
            parent_id=sample_task.id,
        )
        db_session.add(subtask)
        await db_session.commit()
        await db_session.refresh(subtask)
        assert subtask.parent_id == sample_task.id


class TestIssueHierarchyAPI:
    async def test_create_child_issue(
        self, client: AsyncClient, sample_epic: Issue
    ) -> None:
        payload = {
            "title": "Child Story",
            "issue_type": IssueType.STORY.value,
            "status": IssueStatus.TODO.value,
            "priority": IssuePriority.MEDIUM.value,
            "parent_id": str(sample_epic.id),
        }
        resp = await client.post(API_BASE, json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["parent_id"] == str(sample_epic.id)

    async def test_get_issue_includes_children(
        self, client: AsyncClient, sample_epic: Issue, sample_story: Issue
    ) -> None:
        resp = await client.get(f"{API_BASE}/{sample_epic.id}")
        assert resp.status_code == 200
        data = resp.json()
        children_ids = [c["id"] for c in data.get("children", [])]
        assert str(sample_story.id) in children_ids

    async def test_get_issue_detail_shows_parent(
        self, client: AsyncClient, sample_epic: Issue, sample_story: Issue
    ) -> None:
        resp = await client.get(f"{API_BASE}/{sample_story.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["parent_id"] == str(sample_epic.id)

    async def test_list_issues_pagination(
        self, client: AsyncClient, sample_epic: Issue, sample_story: Issue
    ) -> None:
        resp = await client.get(API_BASE, params={"offset": 0, "limit": 1})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["total"] >= 2

    async def test_delete_parent_with_children_returns_409(
        self, client: AsyncClient, sample_epic: Issue, sample_story: Issue
    ) -> None:
        resp = await client.delete(f"{API_BASE}/{sample_epic.id}")
        assert resp.status_code == 409

    async def test_create_issue_with_invalid_parent_returns_404(
        self, client: AsyncClient
    ) -> None:
        fake_id = str(uuid.uuid4())
        payload = {
            "title": "Orphan",
            "issue_type": IssueType.TASK.value,
            "status": IssueStatus.TODO.value,
            "priority": IssuePriority.MEDIUM.value,
            "parent_id": fake_id,
        }
        resp = await client.post(API_BASE, json=payload)
        assert resp.status_code in (404, 422)
