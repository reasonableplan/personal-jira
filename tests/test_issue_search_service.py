import uuid
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.issue import Issue, IssueStatus, IssuePriority, IssueType
from app.services.issue_search_service import IssueSearchService, IssueSearchParams


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
def service():
    return IssueSearchService()


@pytest.fixture
def seed_issues(db_session):
    issues = [
        Issue(
            id=uuid.uuid4(),
            title="Bug in auth",
            description="Login broken",
            status=IssueStatus.OPEN,
            priority=IssuePriority.HIGH,
            issue_type=IssueType.BUG,
            assignee="alice",
            labels=["backend", "auth"],
        ),
        Issue(
            id=uuid.uuid4(),
            title="Add search",
            description="Search feature",
            status=IssueStatus.IN_PROGRESS,
            priority=IssuePriority.MEDIUM,
            issue_type=IssueType.FEATURE,
            assignee="bob",
            labels=["backend"],
        ),
    ]
    for issue in issues:
        db_session.add(issue)
    db_session.commit()
    return issues


class TestIssueSearchParams:
    def test_default_values(self):
        params = IssueSearchParams()
        assert params.offset == 0
        assert params.limit == 20
        assert params.sort_by == "created_at"
        assert params.sort_order == "desc"
        assert params.status is None
        assert params.priority is None
        assert params.assignee is None
        assert params.label is None
        assert params.q is None

    def test_limit_clamped_to_max(self):
        params = IssueSearchParams(limit=500)
        assert params.limit == 100

    def test_valid_sort_fields(self):
        for field in ["created_at", "updated_at", "priority", "title", "status"]:
            params = IssueSearchParams(sort_by=field)
            assert params.sort_by == field

    def test_invalid_sort_field_raises(self):
        with pytest.raises(ValueError):
            IssueSearchParams(sort_by="invalid")


class TestIssueSearchService:
    def test_search_no_filters(self, service, db_session, seed_issues):
        params = IssueSearchParams()
        result = service.search(db_session, params)
        assert result.total == 2
        assert len(result.items) == 2

    def test_search_by_status(self, service, db_session, seed_issues):
        params = IssueSearchParams(status=[IssueStatus.OPEN])
        result = service.search(db_session, params)
        assert result.total == 1
        assert result.items[0].status == IssueStatus.OPEN

    def test_search_by_assignee(self, service, db_session, seed_issues):
        params = IssueSearchParams(assignee="alice")
        result = service.search(db_session, params)
        assert result.total == 1
        assert result.items[0].assignee == "alice"

    def test_search_by_keyword(self, service, db_session, seed_issues):
        params = IssueSearchParams(q="auth")
        result = service.search(db_session, params)
        assert result.total == 1

    def test_search_pagination(self, service, db_session, seed_issues):
        params = IssueSearchParams(offset=0, limit=1)
        result = service.search(db_session, params)
        assert len(result.items) == 1
        assert result.total == 2

    def test_search_sort_asc(self, service, db_session, seed_issues):
        params = IssueSearchParams(sort_by="title", sort_order="asc")
        result = service.search(db_session, params)
        titles = [i.title for i in result.items]
        assert titles == sorted(titles)
