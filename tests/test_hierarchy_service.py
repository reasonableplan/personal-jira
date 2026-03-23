import pytest
from sqlalchemy.orm import Session

from personal_jira.models import Issue, IssueType, IssueStatus, IssuePriority
from personal_jira.services.hierarchy import HierarchyService


def _make_issue(
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


class TestGetChildren:
    def test_direct_children(self, db_session):
        svc = HierarchyService(db_session)
        epic = _make_issue(db_session, "E", IssueType.EPIC)
        s1 = _make_issue(db_session, "S1", IssueType.STORY, epic.id)
        s2 = _make_issue(db_session, "S2", IssueType.STORY, epic.id)
        children = svc.get_children(epic.id)
        assert {c.id for c in children} == {s1.id, s2.id}

    def test_nonexistent_raises(self, db_session):
        svc = HierarchyService(db_session)
        with pytest.raises(ValueError, match="not found"):
            svc.get_children(99999)


class TestGetSubtree:
    def test_full_tree(self, db_session):
        svc = HierarchyService(db_session)
        epic = _make_issue(db_session, "E", IssueType.EPIC)
        story = _make_issue(db_session, "S", IssueType.STORY, epic.id)
        task = _make_issue(db_session, "T", IssueType.TASK, story.id)
        tree = svc.get_subtree(epic.id)
        assert tree["id"] == epic.id
        assert len(tree["children"]) == 1
        assert tree["children"][0]["id"] == story.id
        assert tree["children"][0]["children"][0]["id"] == task.id

    def test_max_depth_limits_recursion(self, db_session):
        svc = HierarchyService(db_session)
        epic = _make_issue(db_session, "E", IssueType.EPIC)
        story = _make_issue(db_session, "S", IssueType.STORY, epic.id)
        _make_issue(db_session, "T", IssueType.TASK, story.id)
        tree = svc.get_subtree(epic.id, max_depth=1)
        assert len(tree["children"]) == 1
        assert tree["children"][0]["children"] == []


class TestGetAncestors:
    def test_ancestors_bottom_up(self, db_session):
        svc = HierarchyService(db_session)
        epic = _make_issue(db_session, "E", IssueType.EPIC)
        story = _make_issue(db_session, "S", IssueType.STORY, epic.id)
        task = _make_issue(db_session, "T", IssueType.TASK, story.id)
        ancestors = svc.get_ancestors(task.id)
        assert [a.id for a in ancestors] == [story.id, epic.id]

    def test_root_has_no_ancestors(self, db_session):
        svc = HierarchyService(db_session)
        epic = _make_issue(db_session, "E", IssueType.EPIC)
        assert svc.get_ancestors(epic.id) == []

    def test_nonexistent_raises(self, db_session):
        svc = HierarchyService(db_session)
        with pytest.raises(ValueError, match="not found"):
            svc.get_ancestors(99999)
