from app.models.issue import Label, task_labels
from app.schemas.label import LabelCreate, LabelUpdate
from app.services.base import GenericCRUDService
from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class LabelService(GenericCRUDService[Label, LabelCreate, LabelUpdate]):
    model = Label

    async def get_by_name(self, session: AsyncSession, name: str) -> Label | None:
        stmt = select(Label).where(Label.name == name)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, session: AsyncSession) -> list[Label]:
        stmt = select(Label).order_by(Label.name)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def attach_labels_to_task(
        self, session: AsyncSession, task_id: str, label_ids: list[str]
    ) -> list[str]:
        stmt = select(task_labels.c.label_id).where(
            task_labels.c.task_id == task_id
        )
        result = await session.execute(stmt)
        existing = {row[0] for row in result.fetchall()}
        new_ids = [lid for lid in label_ids if lid not in existing]
        for lid in new_ids:
            await session.execute(
                task_labels.insert().values(task_id=task_id, label_id=lid)
            )
        await session.flush()
        stmt = select(task_labels.c.label_id).where(
            task_labels.c.task_id == task_id
        )
        result = await session.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def detach_label_from_task(
        self, session: AsyncSession, task_id: str, label_id: str
    ) -> bool:
        stmt = sa_delete(task_labels).where(
            task_labels.c.task_id == task_id,
            task_labels.c.label_id == label_id,
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount > 0


label_service = LabelService()
