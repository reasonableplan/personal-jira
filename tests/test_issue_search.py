import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import create_app
from app.models.issue import Issue, IssueStatus, IssuePriority, IssueType


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(engine):
    app = create_app()
    Session = sessionmaker(bind=engine)

    def _override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app)


@pytest.fixture
def seed_issues(db_session):
    issues = [
        Issue(
            id=uuid.uuid4(),
            title="Fix login bug",
            description="Login fails on mobile",
            status=IssueStatus.OPEN,
            priority=IssuePriority.HIGH,
            issue_type=IssueType.BUG,
            assignee="alice",
            labels=["frontend", "auth"],
        ),
        Issue(
            id=uuid.uuid4(),
            title="Add dark mode",
            description="Support dark theme",
            status=IssueStatus.IN_PROGRESS,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.FEATURE,
            assignee="bob",
            labels=["frontend", "ui"],
        ),
        Issue(
            id=uuid.uuid4(),
            title="Refactor auth module",
            description="Clean up auth code",
            status=IssueStatus.OPEN,
            priority=IssuePriority.LOW,
            issue_type=IssueType.TASK,
            assignee="alice",
            labels=["backend", "auth"],
        ),
        Issue(
            id=uuid.uuid4(),
            title="Fix crash on submit",
            description="App crashes when submitting form",
            status=IssueStatus.DONE,
            priority=IssuePriority.CRITICAL,
            issue_type=IssueType.BUG,
            assignee="charlie",
            labels=["frontend"],
        ),
        Issue(
            id=uuid.uuid4(),
            title="Update dependencies",
            description="Bump all packages",
            status=IssueStatus.BACKLOG,
            priority=IssuePriority.LOW,
            issue_type=IssueType.TASK,
            assignee=None,
            labels=[],
        ),
    ]
    for issue in issues:
        db_session.add(issue)
    db_session.commit()
    return issues


class TestFilterByStatus:
    def test_filter_single_status(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"status": "open"})
        assert resp.status_code == 200
        data = resp.json()
        assert all(item["status"] == "open" for item in data["items"])
        assert data["total"] == 2

    def test_filter_multiple_status(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"status": ["open", "in_progress"]})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        statuses = {item["status"] for item in data["items"]}
        assert statuses <= {"open", "in_progress"}

    def test_filter_status_no_match(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"status": "abandoned"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_filter_invalid_status_422(self, client):
        resp = client.get("/api/v1/issues", params={"status": "invalid_status"})
        assert resp.status_code == 422


class TestFilterByPriority:
    def test_filter_single_priority(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"priority": "high"})
        assert resp.status_code == 200
        data = resp.json()
        assert all(item["priority"] == "high" for item in data["items"])
        assert data["total"] == 1

    def test_filter_multiple_priority(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"priority": ["high", "critical"]})
        assert resp.status_code == 200
        assert resp.json()["total"] == 2


class TestFilterByAssignee:
    def test_filter_by_assignee(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"assignee": "alice"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert all(item["assignee"] == "alice" for item in data["items"])

    def test_filter_unassigned(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"assignee": "__unassigned__"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        assert resp.json()["items"][0]["assignee"] is None

    def test_filter_assignee_no_match(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"assignee": "nobody"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestFilterByLabel:
    def test_filter_single_label(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"label": "auth"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert "auth" in item["labels"]

    def test_filter_multiple_labels_intersection(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"label": ["frontend", "auth"]})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert "frontend" in data["items"][0]["labels"]
        assert "auth" in data["items"][0]["labels"]

    def test_filter_label_no_match(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"label": "nonexistent"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestFilterByIssueType:
    def test_filter_by_type(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"issue_type": "bug"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 2


class TestSearchByKeyword:
    def test_search_title(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"q": "login"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        assert "login" in resp.json()["items"][0]["title"].lower()

    def test_search_description(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"q": "crashes"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_search_case_insensitive(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"q": "FIX"})
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_search_no_match(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"q": "zzzznotfound"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestCombinedFilters:
    def test_status_and_assignee(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"status": "open", "assignee": "alice"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert item["status"] == "open"
            assert item["assignee"] == "alice"

    def test_priority_and_label(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"priority": "high", "label": "auth"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1

    def test_all_filters_combined(self, client, seed_issues):
        resp = client.get(
            "/api/v1/issues",
            params={
                "status": "open",
                "priority": "high",
                "assignee": "alice",
                "label": "auth",
                "q": "login",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1


class TestSorting:
    def test_sort_by_created_at_desc(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"sort_by": "created_at", "sort_order": "desc"})
        assert resp.status_code == 200
        items = resp.json()["items"]
        dates = [item["created_at"] for item in items]
        assert dates == sorted(dates, reverse=True)

    def test_sort_by_priority_asc(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"sort_by": "priority", "sort_order": "asc"})
        assert resp.status_code == 200
        assert len(resp.json()["items"]) > 0

    def test_sort_by_title(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"sort_by": "title", "sort_order": "asc"})
        assert resp.status_code == 200
        items = resp.json()["items"]
        titles = [item["title"] for item in items]
        assert titles == sorted(titles)

    def test_invalid_sort_field_422(self, client):
        resp = client.get("/api/v1/issues", params={"sort_by": "nonexistent_field"})
        assert resp.status_code == 422

    def test_default_sort_created_at_desc(self, client, seed_issues):
        resp = client.get("/api/v1/issues")
        assert resp.status_code == 200
        items = resp.json()["items"]
        dates = [item["created_at"] for item in items]
        assert dates == sorted(dates, reverse=True)


class TestPagination:
    def test_default_pagination(self, client, seed_issues):
        resp = client.get("/api/v1/issues")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data

    def test_custom_offset_limit(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"offset": 2, "limit": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 2
        assert data["offset"] == 2
        assert data["limit"] == 2

    def test_offset_beyond_total(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"offset": 100})
        assert resp.status_code == 200
        assert resp.json()["items"] == []
        assert resp.json()["total"] == 5

    def test_limit_clamp_max(self, client, seed_issues):
        resp = client.get("/api/v1/issues", params={"limit": 500})
        assert resp.status_code == 200
        assert resp.json()["limit"] <= 100

    def test_negative_offset_422(self, client):
        resp = client.get("/api/v1/issues", params={"offset": -1})
        assert resp.status_code == 422

    def test_zero_limit_422(self, client):
        resp = client.get("/api/v1/issues", params={"limit": 0})
        assert resp.status_code == 422


class TestSoftDeleteExcluded:
    def test_deleted_issues_excluded(self, client, db_session, seed_issues):
        issue = seed_issues[0]
        issue.deleted_at = datetime.now(timezone.utc)
        db_session.commit()
        resp = client.get("/api/v1/issues")
        assert resp.status_code == 200
        ids = [item["id"] for item in resp.json()["items"]]
        assert str(issue.id) not in ids


class TestNoFilters:
    def test_no_filters_returns_all(self, client, seed_issues):
        resp = client.get("/api/v1/issues")
        assert resp.status_code == 200
        assert resp.json()["total"] == 5
