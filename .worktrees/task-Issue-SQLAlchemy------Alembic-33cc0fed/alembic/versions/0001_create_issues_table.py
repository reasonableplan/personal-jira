"""create_issues_table

Revision ID: 0001
Revises:
Create Date: 2026-03-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "issues",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "status IN ('todo', 'in_progress', 'done')", name="ck_issues_status"
        ),
        sa.CheckConstraint(
            "priority >= 1 AND priority <= 5", name="ck_issues_priority"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_issues_priority"), "issues", ["priority"], unique=False)
    op.create_index(op.f("ix_issues_status"), "issues", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_issues_status"), table_name="issues")
    op.drop_index(op.f("ix_issues_priority"), table_name="issues")
    op.drop_table("issues")
