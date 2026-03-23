import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.activity import ActivityLog, ActivityType


class TestActivityType:
    def test_has_status_changed(self) -> None:
        assert ActivityType.STATUS_CHANGED == "status_changed"

    def test_has_assignee_changed(self) -> None:
        assert ActivityType.ASSIGNEE_CHANGED == "assignee_changed"

    def test_has_comment_added(self) -> None:
        assert ActivityType.COMMENT_ADDED == "comment_added"

    def test_has_priority_changed(self) -> None:
        assert ActivityType.PRIORITY_CHANGED == "priority_changed"

    def test_has_title_changed(self) -> None:
        assert ActivityType.TITLE_CHANGED == "title_changed"

    def test_has_description_changed(self) -> None:
        assert ActivityType.DESCRIPTION_CHANGED == "description_changed"

    def test_has_dependency_added(self) -> None:
        assert ActivityType.DEPENDENCY_ADDED == "dependency_added"

    def test_has_dependency_removed(self) -> None:
        assert ActivityType.DEPENDENCY_REMOVED == "dependency_removed"

    def test_has_created(self) -> None:
        assert ActivityType.CREATED == "created"

    def test_has_deleted(self) -> None:
        assert ActivityType.DELETED == "deleted"


class TestActivityLogSchema:
    def test_table_name(self) -> None:
        assert ActivityLog.__tablename__ == "activity_logs"

    def test_has_id_column(self) -> None:
        mapper = inspect(ActivityLog)
        assert "id" in mapper.columns.keys()

    def test_has_issue_id_column(self) -> None:
        mapper = inspect(ActivityLog)
        assert "issue_id" in mapper.columns.keys()

    def test_has_activity_type_column(self) -> None:
        mapper = inspect(ActivityLog)
        assert "activity_type" in mapper.columns.keys()

    def test_has_actor_column(self) -> None:
        mapper = inspect(ActivityLog)
        assert "actor" in mapper.columns.keys()

    def test_has_old_value_column(self) -> None:
        mapper = inspect(ActivityLog)
        assert "old_value" in mapper.columns.keys()

    def test_has_new_value_column(self) -> None:
        mapper = inspect(ActivityLog)
        assert "new_value" in mapper.columns.keys()

    def test_has_detail_column(self) -> None:
        mapper = inspect(ActivityLog)
        assert "detail" in mapper.columns.keys()

    def test_has_created_at_column(self) -> None:
        mapper = inspect(ActivityLog)
        assert "created_at" in mapper.columns.keys()

    def test_id_is_primary_key(self) -> None:
        mapper = inspect(ActivityLog)
        pk_cols = [col.name for col in mapper.primary_key]
        assert "id" in pk_cols

    def test_issue_id_not_nullable(self) -> None:
        mapper = inspect(ActivityLog)
        assert mapper.columns["issue_id"].nullable is False

    def test_activity_type_not_nullable(self) -> None:
        mapper = inspect(ActivityLog)
        assert mapper.columns["activity_type"].nullable is False

    def test_old_value_nullable(self) -> None:
        mapper = inspect(ActivityLog)
        assert mapper.columns["old_value"].nullable is True

    def test_new_value_nullable(self) -> None:
        mapper = inspect(ActivityLog)
        assert mapper.columns["new_value"].nullable is True

    def test_detail_nullable(self) -> None:
        mapper = inspect(ActivityLog)
        assert mapper.columns["detail"].nullable is True


class TestActivityLogCRUD:
    @pytest.mark.asyncio
    async def test_create_activity_log(self, db_session: AsyncSession) -> None:
        issue_id = uuid.uuid4()
        log = ActivityLog(
            id=uuid.uuid4(),
            issue_id=issue_id,
            activity_type=ActivityType.STATUS_CHANGED,
            actor="system",
            old_value="Backlog",
            new_value="Ready",
        )
        db_session.add(log)
        await db_session.commit()

        result = await db_session.execute(
            select(ActivityLog).where(ActivityLog.issue_id == issue_id)
        )
        saved = result.scalar_one()
        assert saved.activity_type == ActivityType.STATUS_CHANGED
        assert saved.old_value == "Backlog"
        assert saved.new_value == "Ready"
        assert saved.actor == "system"

    @pytest.mark.asyncio
    async def test_create_activity_with_detail(self, db_session: AsyncSession) -> None:
        issue_id = uuid.uuid4()
        log = ActivityLog(
            id=uuid.uuid4(),
            issue_id=issue_id,
            activity_type=ActivityType.COMMENT_ADDED,
            actor="user-1",
            detail="First comment on this issue",
        )
        db_session.add(log)
        await db_session.commit()

        result = await db_session.execute(
            select(ActivityLog).where(ActivityLog.issue_id == issue_id)
        )
        saved = result.scalar_one()
        assert saved.detail == "First comment on this issue"
        assert saved.old_value is None
        assert saved.new_value is None

    @pytest.mark.asyncio
    async def test_multiple_activities_for_issue(self, db_session: AsyncSession) -> None:
        issue_id = uuid.uuid4()
        for i in range(3):
            log = ActivityLog(
                id=uuid.uuid4(),
                issue_id=issue_id,
                activity_type=ActivityType.STATUS_CHANGED,
                actor="system",
                old_value=f"state_{i}",
                new_value=f"state_{i + 1}",
            )
            db_session.add(log)
        await db_session.commit()

        result = await db_session.execute(
            select(ActivityLog).where(ActivityLog.issue_id == issue_id)
        )
        logs = result.scalars().all()
        assert len(logs) == 3

    @pytest.mark.asyncio
    async def test_created_at_auto_set(self, db_session: AsyncSession) -> None:
        log = ActivityLog(
            id=uuid.uuid4(),
            issue_id=uuid.uuid4(),
            activity_type=ActivityType.CREATED,
            actor="system",
        )
        db_session.add(log)
        await db_session.commit()
        await db_session.refresh(log)
        assert log.created_at is not None
