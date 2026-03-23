"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "issues",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("parent_id", sa.String(36), sa.ForeignKey("issues.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "work_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("issue_id", sa.String(36), sa.ForeignKey("issues.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.String(100), nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("llm_calls", sa.Integer, nullable=False, server_default="0"),
        sa.Column("tokens_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_work_logs_issue_id", "work_logs", ["issue_id"])
    op.create_index("ix_work_logs_agent_id", "work_logs", ["agent_id"])

    op.create_table(
        "code_artifacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("work_log_id", sa.String(36), sa.ForeignKey("work_logs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("artifact_type", sa.String(50), nullable=False, server_default="file"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_code_artifacts_work_log_id", "code_artifacts", ["work_log_id"])


def downgrade() -> None:
    op.drop_table("code_artifacts")
    op.drop_table("work_logs")
    op.drop_table("issues")
