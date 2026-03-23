import sys
import os

# Ensure src/ is first in sys.path so src/personal_jira takes precedence
# over the root-level personal_jira/ package.
_SRC = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import uuid
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from personal_jira.database import Base
from personal_jira.main import app
from personal_jira.dependencies import get_session


TEST_DATABASE_URL = "sqlite+aiosqlite://"

_test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)


# Override the app's session dependency to use the in-memory test DB
async def _override_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = _override_session


@pytest_asyncio.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as s:
        yield s


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Alias for session, used by some tests."""
    async with TestSessionLocal() as s:
        yield s


@pytest_asyncio.fixture
async def sample_issue(client: AsyncClient) -> dict[str, Any]:
    resp = await client.post("/api/v1/issues", json={
        "title": "Sample Issue",
        "description": "For testing",
        "priority": "medium",
    })
    assert resp.status_code == 201
    return resp.json()
