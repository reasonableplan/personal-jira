import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.activity import ActivityLog, ActivityType
from personal_jira.services.activity_service import ActivityService


class TestRecordActivity:
    @pytest.mark.asyncio
    async def test_record_status_change(self, db_session: AsyncSession) -> None:
        service = ActivityService(db_session)
        issue_id = uuid.uuid4()

        log = await service.record(
            issue_id=issue_id,
            activity_type=ActivityType.STATUS_CHANGED,
            actor="system",
            old_value="Backlog",
            new_value="Ready",
        )

        assert log.issue_id == issue_id
        assert log.activity_type == ActivityType.STATUS_CHANGED
        assert log.old_value == "Backlog"
        assert log.new_value == "Ready"

    @pytest.mark.asyncio
    async def test_record_comment_added(self, db_session: AsyncSession) -> None:
        service = ActivityService(db_session)
        issue_id = uuid.uuid4()

        log = await service.record(
            issue_id=issue_id,
            activity_type=ActivityType.COMMENT_ADDED,
            actor="user-1",
            detail="New comment body",
        )

        assert log.activity_type == ActivityType.COMMENT_ADDED
        assert log.detail == "New comment body"
        assert log.old_value is None
        assert log.new_value is None

    @pytest.mark.asyncio
    async def test_record_priority_change(self, db_session: AsyncSession) -> None:
        service = ActivityService(db_session)
        issue_id = uuid.uuid4()

        log = await service.record(
            issue_id=issue_id,
            activity_type=ActivityType.PRIORITY_CHANGED,
            actor="user-1",
            old_value="Low",
            new_value="High",
        )

        assert log.old_value == "Low"
        assert log.new_value == "High"

    @pytest.mark.asyncio
    async def test_record_created(self, db_session: AsyncSession) -> None:
        service = ActivityService(db_session)
        issue_id = uuid.uuid4()

        log = await service.record(
            issue_id=issue_id,
            activity_type=ActivityType.CREATED,
            actor="user-1",
            new_value="New Issue Title",
        )

        assert log.activity_type == ActivityType.CREATED
        assert log.new_value == "New Issue Title"


class TestGetTimeline:
    @pytest.mark.asyncio
    async def test_empty_timeline(self, db_session: AsyncSession) -> None:
        service = ActivityService(db_session)
        issue_id = uuid.uuid4()

        logs = await service.get_timeline(issue_id)
        assert logs == []

    @pytest.mark.asyncio
    async def test_timeline_returns_activities(self, db_session: AsyncSession) -> None:
        service = ActivityService(db_session)
        issue_id = uuid.uuid4()

        await service.record(
            issue_id=issue_id,
            activity_type=ActivityType.CREATED,
            actor="user-1",
        )
        await service.record(
            issue_id=issue_id,
            activity_type=ActivityType.STATUS_CHANGED,
            actor="user-1",
            old_value="Backlog",
            new_value="Ready",
        )

        logs = await service.get_timeline(issue_id)
        assert len(logs) == 2

    @pytest.mark.asyncio
    async def test_timeline_ordered_by_created_at_desc(self, db_session: AsyncSession) -> None:
        service = ActivityService(db_session)
        issue_id = uuid.uuid4()

        await service.record(
            issue_id=issue_id,
            activity_type=ActivityType.CREATED,
            actor="user-1",
        )
        await service.record(
            issue_id=issue_id,
            activity_type=ActivityType.STATUS_CHANGED,
            actor="user-1",
            old_value="Backlog",
            new_value="Ready",
        )

        logs = await service.get_timeline(issue_id)
        assert logs[0].activity_type == ActivityType.STATUS_CHANGED
        assert logs[1].activity_type == ActivityType.CREATED

    @pytest.mark.asyncio
    async def test_timeline_pagination(self, db_session: AsyncSession) -> None:
        service = ActivityService(db_session)
        issue_id = uuid.uuid4()

        for i in range(5):
            await service.record(
                issue_id=issue_id,
                activity_type=ActivityType.STATUS_CHANGED,
                actor="user-1",
                old_value=f"state_{i}",
                new_value=f"state_{i + 1}",
            )

        logs = await service.get_timeline(issue_id, offset=0, limit=2)
        assert len(logs) == 2

        logs_page2 = await service.get_timeline(issue_id, offset=2, limit=2)
        assert len(logs_page2) == 2

    @pytest.mark.asyncio
    async def test_timeline_filter_by_type(self, db_session: AsyncSession) -> None:
        service = ActivityService(db_session)
        issue_id = uuid.uuid4()

        await service.record(
            issue_id=issue_id,
            activity_type=ActivityType.CREATED,
            actor="user-1",
        )
        await service.record(
            issue_id=issue_id,
            activity_type=ActivityType.STATUS_CHANGED,
            actor="user-1",
            old_value="Backlog",
            new_value="Ready",
        )
        await service.record(
            issue_id=issue_id,
            activity_type=ActivityType.COMMENT_ADDED,
            actor="user-2",
            detail="Hello",
        )

        logs = await service.get_timeline(
            issue_id, activity_type=ActivityType.STATUS_CHANGED
        )
        assert len(logs) == 1
        assert logs[0].activity_type == ActivityType.STATUS_CHANGED

    @pytest.mark.asyncio
    async def test_timeline_does_not_return_other_issue(self, db_session: AsyncSession) -> None:
        service = ActivityService(db_session)
        issue_a = uuid.uuid4()
        issue_b = uuid.uuid4()

        await service.record(
            issue_id=issue_a,
            activity_type=ActivityType.CREATED,
            actor="user-1",
        )
        await service.record(
            issue_id=issue_b,
            activity_type=ActivityType.CREATED,
            actor="user-2",
        )

        logs = await service.get_timeline(issue_a)
        assert len(logs) == 1
        assert logs[0].issue_id == issue_a
