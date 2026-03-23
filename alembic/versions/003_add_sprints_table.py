"""add sprints table

Revision ID: 003
Revises: 002
Create Date: 2026-03-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sprints",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("goal", sa.Text, nullable=True),
        sa.Column(
            "status",
            sa.Enum("planning", "active", "completed", "cancelled", name="sprint_status"),
            nullable=False,
            server_default="planning",
        ),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column(
        "issues",
        sa.Column("sprint_id", UUID(as_uuid=True), sa.ForeignKey("sprints.id"), nullable=True),
    )
    op.create_index("ix_issues_sprint_id", "issues", ["sprint_id"])


def downgrade() -> None:
    op.drop_index("ix_issues_sprint_id", table_name="issues")
    op.drop_column("issues", "sprint_id")
    op.drop_table("sprints")
    op.execute("DROP TYPE IF EXISTS sprint_status")
