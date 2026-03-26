"""SQLAlchemy models package.

Import all model modules here so that ``Base.metadata`` is populated
when Alembic (or any other tool) does ``import app.models``.
"""

from app.core.database import Base

__all__ = ["Base"]
