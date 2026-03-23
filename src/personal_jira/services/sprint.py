import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.sprint import Sprint, SprintStatus
from personal_jira.schemas.sprint import SprintCreate, SprintUpdate


class SprintService:
    async def create(self, db: AsyncSession, data: SprintCreate) -> Sprint:
        sprint = Sprint(
            name=data.name,
            goal=data.goal,
            start_date=data.start_date,
            end_date=data.end_date,
            status=SprintStatus.PLANNING,
        )
        db.add(sprint)
        await db.commit()
        await db.refresh(sprint)
        return sprint

    async def get_by_id(self, db: AsyncSession, sprint_id: uuid.UUID) -> Sprint | None:
        stmt = select(Sprint).where(Sprint.id == sprint_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, db: AsyncSession) -> list[Sprint]:
        stmt = select(Sprint).order_by(Sprint.start_date.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, sprint_id: uuid.UUID, data: SprintUpdate
    ) -> Sprint | None:
        sprint = await self.get_by_id(db, sprint_id)
        if sprint is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sprint, field, value)

        await db.commit()
        await db.refresh(sprint)
        return sprint

    async def delete(self, db: AsyncSession, sprint_id: uuid.UUID) -> bool:
        sprint = await self.get_by_id(db, sprint_id)
        if sprint is None:
            return False

        await db.delete(sprint)
        await db.commit()
        return True
