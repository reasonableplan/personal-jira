from uuid import UUID
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.sprint import Sprint, SprintStatus
from personal_jira.models.issue import Issue
from personal_jira.schemas.sprint import SprintCreate, SprintUpdate


class SprintService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, data: SprintCreate) -> Sprint:
        sprint = Sprint(
            name=data.name,
            goal=data.goal,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        self._db.add(sprint)
        await self._db.commit()
        await self._db.refresh(sprint)
        return sprint

    async def get_by_id(self, sprint_id: UUID) -> Optional[Sprint]:
        result = await self._db.execute(
            select(Sprint).where(Sprint.id == sprint_id)
        )
        return result.scalar_one_or_none()

    async def list_sprints(
        self,
        offset: int = 0,
        limit: int = 20,
        status: Optional[SprintStatus] = None,
    ) -> tuple[list[Sprint], int]:
        query = select(Sprint)
        count_query = select(func.count()).select_from(Sprint)

        if status is not None:
            query = query.where(Sprint.status == status)
            count_query = count_query.where(Sprint.status == status)

        query = query.offset(offset).limit(limit).order_by(Sprint.created_at.desc())

        result = await self._db.execute(query)
        sprints = list(result.scalars().all())

        count_result = await self._db.execute(count_query)
        total = count_result.scalar_one()

        return sprints, total

    async def update(
        self, sprint_id: UUID, data: SprintUpdate
    ) -> Optional[Sprint]:
        sprint = await self.get_by_id(sprint_id)
        if sprint is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sprint, field, value)

        await self._db.commit()
        await self._db.refresh(sprint)
        return sprint

    async def delete(self, sprint_id: UUID) -> bool:
        sprint = await self.get_by_id(sprint_id)
        if sprint is None:
            return False

        await self._db.delete(sprint)
        await self._db.commit()
        return True

    async def add_issue(
        self, sprint_id: UUID, issue_id: UUID
    ) -> Optional[bool]:
        sprint = await self.get_by_id(sprint_id)
        if sprint is None:
            return None

        result = await self._db.execute(
            select(Issue).where(Issue.id == issue_id)
        )
        issue = result.scalar_one_or_none()
        if issue is None:
            return False

        issue.sprint_id = sprint_id
        await self._db.commit()
        return True

    async def remove_issue(
        self, sprint_id: UUID, issue_id: UUID
    ) -> bool:
        result = await self._db.execute(
            select(Issue).where(
                Issue.id == issue_id,
                Issue.sprint_id == sprint_id,
            )
        )
        issue = result.scalar_one_or_none()
        if issue is None:
            return False

        issue.sprint_id = None
        await self._db.commit()
        return True

    async def get_sprint_issues(
        self, sprint_id: UUID
    ) -> Optional[list[Issue]]:
        sprint = await self.get_by_id(sprint_id)
        if sprint is None:
            return None

        result = await self._db.execute(
            select(Issue).where(Issue.sprint_id == sprint_id)
        )
        return list(result.scalars().all())
