from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from personal_jira.app import create_app
from personal_jira.database import Base, get_db
from personal_jira.models.issue import Issue, IssueStatus

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db: Session) -> TestClient:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def sample_issue(db: Session) -> Issue:
    issue = Issue(title="Sample Issue", status=IssueStatus.BACKLOG)
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@pytest.fixture
def blocker_issue(db: Session) -> Issue:
    issue = Issue(title="Blocker Issue", status=IssueStatus.BACKLOG)
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@pytest.fixture
def done_issue(db: Session) -> Issue:
    issue = Issue(title="Done Issue", status=IssueStatus.DONE)
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def create_issue(db: Session, title: str = "Test Issue", status: IssueStatus = IssueStatus.BACKLOG) -> Issue:
    issue = Issue(title=title, status=status)
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue
