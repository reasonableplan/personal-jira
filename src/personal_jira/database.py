"""Database engine and session factory.

Engine is created lazily via get_engine() so that importing this module
does not attempt a real DB connection at module load time (critical for tests).
"""
from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Internal singletons – populated on first call to get_engine()
# ---------------------------------------------------------------------------

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _get_database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./personal_jira.db")


def get_engine(url: str | None = None) -> AsyncEngine:
    """Return the shared async engine, creating it on first call."""
    global _engine, _session_factory
    if _engine is None:
        _engine = create_async_engine(url or _get_database_url(), echo=False)
        _session_factory = async_sessionmaker(
            _engine, class_=AsyncSession, expire_on_commit=False
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the shared session factory, initialising engine if needed."""
    global _session_factory
    if _session_factory is None:
        get_engine()
    assert _session_factory is not None
    return _session_factory


# ---------------------------------------------------------------------------
# Aliases expected by various parts of the codebase
# ---------------------------------------------------------------------------

# Lazy property shims so that code doing ``from personal_jira.database import engine``
# gets the lazily-initialised engine rather than None.
class _LazyEngine:
    """Proxy that forwards attribute access to the real engine."""
    def __getattr__(self, name: str):  # noqa: ANN001
        return getattr(get_engine(), name)

    def __repr__(self) -> str:
        return repr(get_engine())


# Keep module-level names for backwards-compat imports
engine = _LazyEngine()

# async_session_factory is referenced by some tests directly
def _get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    return get_session_factory()

async_session_factory = property(_get_async_session_factory)  # type: ignore[assignment]

SessionLocal = get_session_factory  # callable → call it to get a factory


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yield an AsyncSession."""
    async with get_session_factory()() as session:
        yield session


# Alias used by conftest.py
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_factory()() as session:
        yield session


# Sync-style alias used by older tests
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_factory()() as session:
        yield session
