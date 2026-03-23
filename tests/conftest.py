import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from personal_jira.database import Base, get_db
from personal_jira.app import create_app

TEST_DATABASE_URL = "sqlite://"


@pytest.fixture()
def engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db(engine) -> Session:
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_local()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(engine) -> TestClient:
    app = create_app()
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def _override_get_db():
        session = session_local()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app)
