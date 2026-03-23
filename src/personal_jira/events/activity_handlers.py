import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.activity import ActivityType
from personal_jira.services.activity_service import ActivityService

FIELD_TO_ACTIVITY_TYPE: dict[str, ActivityType] = {
    "status": ActivityType.STATUS_CHANGED,
    "assignee": ActivityType.ASSIGNEE_CHANGED,
    "priority": ActivityType.PRIORITY_CHANGED,
    "title": ActivityType.TITLE_CHANGED,
    "description": ActivityType.DESCRIPTION_CHANGED,
}


async def handle_issue_created(
    session: AsyncSession,
    *,
    issue_id: uuid.UUID,
    title: str,
    actor: str = "system",
) -> None:
    service = ActivityService(session)
    await service.record(
        issue_id=issue_id,
        activity_type=ActivityType.CREATED,
        actor=actor,
        new_value=title,
    )


async def handle_issue_status_changed(
    session: AsyncSession,
    *,
    issue_id: uuid.UUID,
    old_status: str,
    new_status: str,
    actor: str = "system",
) -> None:
    service = ActivityService(session)
    await service.record(
        issue_id=issue_id,
        activity_type=ActivityType.STATUS_CHANGED,
        actor=actor,
        old_value=old_status,
        new_value=new_status,
    )


async def handle_issue_updated(
    session: AsyncSession,
    *,
    issue_id: uuid.UUID,
    field: str,
    old_value: Optional[str],
    new_value: Optional[str],
    actor: str = "system",
) -> None:
    activity_type = FIELD_TO_ACTIVITY_TYPE.get(field)
    if activity_type is None:
        return
    service = ActivityService(session)
    await service.record(
        issue_id=issue_id,
        activity_type=activity_type,
        actor=actor,
        old_value=old_value,
        new_value=new_value,
    )


async def handle_issue_deleted(
    session: AsyncSession,
    *,
    issue_id: uuid.UUID,
    title: str,
    actor: str = "system",
) -> None:
    service = ActivityService(session)
    await service.record(
        issue_id=issue_id,
        activity_type=ActivityType.DELETED,
        actor=actor,
        old_value=title,
    )
