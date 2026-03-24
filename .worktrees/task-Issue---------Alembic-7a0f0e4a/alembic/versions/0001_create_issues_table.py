"""create_issues_table

Revision ID: 0001
Revises:
Create Date: 2026-03-24
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "issues",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="todo", nullable=False),
        sa.Column("priority", sa.String(length=20), server_default="medium", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_issues")),
    )
    op.create_index(op.f("ix_issues_status"), "issues", ["status"])
    op.create_index(op.f("ix_issues_priority"), "issues", ["priority"])


def downgrade() -> None:
    op.drop_index(op.f("ix_issues_priority"), table_name="issues")
    op.drop_index(op.f("ix_issues_status"), table_name="issues")
    op.drop_table("issues")
