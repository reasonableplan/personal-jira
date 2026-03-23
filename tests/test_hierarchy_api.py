import pytest
from fastapi import status
from sqlalchemy.orm import Session

from personal_jira.models import Issue, IssueType, IssueStatus, IssuePriority


API_PREFIX = "/api/v1"


def _create_issue(
    db: Session,
    title: str,
    issue_type: IssueType,
    parent_id: int | None = None,
) -> Issue:
    issue = Issue(
        title=title,
        issue_type=issue_type,
        status=IssueStatus.BACKLOG,
        priority=IssuePriority.MEDIUM,
        parent_id=parent_id,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def _build_epic_tree(db: Session) -> dict[str, Issue]:
    epic = _create_issue(db, "Epic-1", IssueType.EPIC)
    story1 = _create_issue(db, "Story-1", IssueType.STORY, parent_id=epic.id)
    story2 = _create_issue(db, "Story-2", IssueType.STORY, parent_id=epic.id)
    task1 = _create_issue(db, "Task-1", IssueType.TASK, parent_id=story1.id)
    task2 = _create_issue(db, "Task-2", IssueType.TASK, parent_id=story1.id)
    sub = _create_issue(db, "Sub-1", IssueType.SUB_TASK, parent_id=task1.id)
    task3 = _create_issue(db, "Task-3", IssueType.TASK, parent_id=story2.id)
    return {
        "epic": epic,
        "story1": story1,
        "story2": story2,
        "task1": task1,
        "task2": task2,
        "sub": sub,
        "task3": task3,
    }


class TestGetChildren:
    def test_returns_direct_children(self, client, db_session):
        tree = _build_epic_tree(db_session)
        resp = client.get(f"{API_PREFIX}/issues/{tree['epic'].id}/children")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data) == 2
        titles = {item["title"] for item in data}
        assert titles == {"Story-1", "Story-2"}

    def test_returns_empty_for_leaf_node(self, client, db_session):
        tree = _build_epic_tree(db_session)
        resp = client.get(f"{API_PREFIX}/issues/{tree['sub'].id}/children")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_404_for_nonexistent_issue(self, client):
        resp = client.get(f"{API_PREFIX}/issues/99999/children")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_children_contain_expected_fields(self, client, db_session):
        tree = _build_epic_tree(db_session)
        resp = client.get(f"{API_PREFIX}/issues/{tree['story1'].id}/children")
        data = resp.json()
        assert len(data) == 2
        for item in data:
            assert "id" in item
            assert "title" in item
            assert "issue_type" in item
            assert "status" in item
            assert "priority" in item


class TestGetSubtree:
    def test_epic_subtree_returns_full_hierarchy(self, client, db_session):
        tree = _build_epic_tree(db_session)
        resp = client.get(f"{API_PREFIX}/issues/{tree['epic'].id}/subtree")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["id"] == tree["epic"].id
        assert data["title"] == "Epic-1"
        assert len(data["children"]) == 2
        story_titles = {c["title"] for c in data["children"]}
        assert story_titles == {"Story-1", "Story-2"}

    def test_subtree_depth(self, client, db_session):
        tree = _build_epic_tree(db_session)
        resp = client.get(f"{API_PREFIX}/issues/{tree['epic'].id}/subtree")
        data = resp.json()
        story1_node = next(c for c in data["children"] if c["title"] == "Story-1")
        assert len(story1_node["children"]) == 2
        task1_node = next(c for c in story1_node["children"] if c["title"] == "Task-1")
        assert len(task1_node["children"]) == 1
        assert task1_node["children"][0]["title"] == "Sub-1"

    def test_subtree_leaf_has_empty_children(self, client, db_session):
        tree = _build_epic_tree(db_session)
        resp = client.get(f"{API_PREFIX}/issues/{tree['sub'].id}/subtree")
        data = resp.json()
        assert data["id"] == tree["sub"].id
        assert data["children"] == []

    def test_subtree_max_depth(self, client, db_session):
        tree = _build_epic_tree(db_session)
        resp = client.get(
            f"{API_PREFIX}/issues/{tree['epic'].id}/subtree",
            params={"max_depth": 1},
        )
        data = resp.json()
        assert len(data["children"]) == 2
        for child in data["children"]:
            assert child["children"] == []

    def test_404_for_nonexistent_issue(self, client):
        resp = client.get(f"{API_PREFIX}/issues/99999/subtree")
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestGetAncestors:
    def test_returns_ancestors_bottom_up(self, client, db_session):
        tree = _build_epic_tree(db_session)
        resp = client.get(f"{API_PREFIX}/issues/{tree['sub'].id}/ancestors")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        titles = [item["title"] for item in data]
        assert titles == ["Task-1", "Story-1", "Epic-1"]

    def test_root_has_no_ancestors(self, client, db_session):
        tree = _build_epic_tree(db_session)
        resp = client.get(f"{API_PREFIX}/issues/{tree['epic'].id}/ancestors")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_404_for_nonexistent_issue(self, client):
        resp = client.get(f"{API_PREFIX}/issues/99999/ancestors")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
