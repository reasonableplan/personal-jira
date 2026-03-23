"""add issue_templates table

Revision ID: 003
Revises: 002
Create Date: 2026-03-23
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, UUID

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "issue_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("default_title", sa.String(500), nullable=True),
        sa.Column("default_description", sa.Text, nullable=True),
        sa.Column("default_priority", sa.String(50), nullable=True),
        sa.Column("default_issue_type", sa.String(50), nullable=True),
        sa.Column(
            "default_labels",
            ARRAY(sa.String),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("issue_templates")
