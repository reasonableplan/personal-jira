import uuid
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.events.activity_handlers import (
    handle_issue_created,
    handle_issue_status_changed,
    handle_issue_updated,
    handle_issue_deleted,
)
from personal_jira.models.activity import ActivityLog, ActivityType
from personal_jira.services.activity_service import ActivityService


class TestHandleIssueCreated:
    @pytest.mark.asyncio
    async def test_records_created_activity(self, db_session: AsyncSession) -> None:
        issue_id = uuid.uuid4()
        await handle_issue_created(
            db_session, issue_id=issue_id, title="New Task", actor="user-1"
        )

        service = ActivityService(db_session)
        logs = await service.get_timeline(issue_id)
        assert len(logs) == 1
        assert logs[0].activity_type == ActivityType.CREATED
        assert logs[0].new_value == "New Task"
        assert logs[0].actor == "user-1"


class TestHandleIssueStatusChanged:
    @pytest.mark.asyncio
    async def test_records_status_change(self, db_session: AsyncSession) -> None:
        issue_id = uuid.uuid4()
        await handle_issue_status_changed(
            db_session,
            issue_id=issue_id,
            old_status="Backlog",
            new_status="Ready",
            actor="system",
        )

        service = ActivityService(db_session)
        logs = await service.get_timeline(issue_id)
        assert len(logs) == 1
        assert logs[0].activity_type == ActivityType.STATUS_CHANGED
        assert logs[0].old_value == "Backlog"
        assert logs[0].new_value == "Ready"


class TestHandleIssueUpdated:
    @pytest.mark.asyncio
    async def test_records_title_change(self, db_session: AsyncSession) -> None:
        issue_id = uuid.uuid4()
        await handle_issue_updated(
            db_session,
            issue_id=issue_id,
            field="title",
            old_value="Old Title",
            new_value="New Title",
            actor="user-1",
        )

        service = ActivityService(db_session)
        logs = await service.get_timeline(issue_id)
        assert len(logs) == 1
        assert logs[0].activity_type == ActivityType.TITLE_CHANGED

    @pytest.mark.asyncio
    async def test_records_priority_change(self, db_session: AsyncSession) -> None:
        issue_id = uuid.uuid4()
        await handle_issue_updated(
            db_session,
            issue_id=issue_id,
            field="priority",
            old_value="Low",
            new_value="High",
            actor="user-1",
        )

        service = ActivityService(db_session)
        logs = await service.get_timeline(issue_id)
        assert len(logs) == 1
        assert logs[0].activity_type == ActivityType.PRIORITY_CHANGED

    @pytest.mark.asyncio
    async def test_records_description_change(self, db_session: AsyncSession) -> None:
        issue_id = uuid.uuid4()
        await handle_issue_updated(
            db_session,
            issue_id=issue_id,
            field="description",
            old_value="old desc",
            new_value="new desc",
            actor="user-1",
        )

        service = ActivityService(db_session)
        logs = await service.get_timeline(issue_id)
        assert len(logs) == 1
        assert logs[0].activity_type == ActivityType.DESCRIPTION_CHANGED

    @pytest.mark.asyncio
    async def test_records_assignee_change(self, db_session: AsyncSession) -> None:
        issue_id = uuid.uuid4()
        await handle_issue_updated(
            db_session,
            issue_id=issue_id,
            field="assignee",
            old_value=None,
            new_value="user-2",
            actor="user-1",
        )

        service = ActivityService(db_session)
        logs = await service.get_timeline(issue_id)
        assert len(logs) == 1
        assert logs[0].activity_type == ActivityType.ASSIGNEE_CHANGED

    @pytest.mark.asyncio
    async def test_ignores_unknown_field(self, db_session: AsyncSession) -> None:
        issue_id = uuid.uuid4()
        await handle_issue_updated(
            db_session,
            issue_id=issue_id,
            field="unknown_field",
            old_value="a",
            new_value="b",
            actor="user-1",
        )

        service = ActivityService(db_session)
        logs = await service.get_timeline(issue_id)
        assert len(logs) == 0


class TestHandleIssueDeleted:
    @pytest.mark.asyncio
    async def test_records_deleted_activity(self, db_session: AsyncSession) -> None:
        issue_id = uuid.uuid4()
        await handle_issue_deleted(
            db_session, issue_id=issue_id, title="Deleted Task", actor="user-1"
        )

        service = ActivityService(db_session)
        logs = await service.get_timeline(issue_id)
        assert len(logs) == 1
        assert logs[0].activity_type == ActivityType.DELETED
        assert logs[0].old_value == "Deleted Task"
