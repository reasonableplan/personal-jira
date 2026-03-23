import uuid
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.personal_jira.database import Base, get_db
from src.personal_jira.main import app
from src.personal_jira.models.enums import IssuePriority, IssueStatus, IssueType
from src.personal_jira.models.issue import Issue

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def sample_epic(db_session: AsyncSession) -> Issue:
    epic = Issue(
        id=uuid.uuid4(),
        title="Epic Issue",
        description="Top-level epic",
        issue_type=IssueType.EPIC,
        status=IssueStatus.TODO,
        priority=IssuePriority.HIGH,
    )
    db_session.add(epic)
    await db_session.commit()
    await db_session.refresh(epic)
    return epic


@pytest.fixture
async def sample_story(db_session: AsyncSession, sample_epic: Issue) -> Issue:
    story = Issue(
        id=uuid.uuid4(),
        title="Story Issue",
        description="Child story of epic",
        issue_type=IssueType.STORY,
        status=IssueStatus.TODO,
        priority=IssuePriority.MEDIUM,
        parent_id=sample_epic.id,
    )
    db_session.add(story)
    await db_session.commit()
    await db_session.refresh(story)
    return story


@pytest.fixture
async def sample_task(db_session: AsyncSession, sample_story: Issue) -> Issue:
    task = Issue(
        id=uuid.uuid4(),
        title="Task Issue",
        description="Child task of story",
        issue_type=IssueType.TASK,
        status=IssueStatus.BACKLOG,
        priority=IssuePriority.LOW,
        parent_id=sample_story.id,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task
