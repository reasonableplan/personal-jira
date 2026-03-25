from typing import Optional

from app.models.base import Label, TaskLabel
from app.schemas.label import LabelCreate, LabelUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class LabelService:
    async def create(self, session: AsyncSession, body: LabelCreate) -> Label:
        label = Label(name=body.name, color=body.color)
        session.add(label)
        await session.commit()
        await session.refresh(label)
        return label

    async def get_by_name(
        self, session: AsyncSession, name: str
    ) -> Optional[Label]:
        stmt = select(Label).where(Label.name == name)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, session: AsyncSession) -> list[Label]:
        stmt = select(Label).order_by(Label.name)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        session: AsyncSession,
        label_id: str,
        body: LabelUpdate,
    ) -> Optional[Label]:
        stmt = select(Label).where(Label.id == label_id)
        result = await session.execute(stmt)
        label = result.scalar_one_or_none()
        if not label:
            return None
        update_data = body.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(label, key, value)
        await session.commit()
        await session.refresh(label)
        return label

    async def delete(self, session: AsyncSession, label_id: str) -> bool:
        stmt = select(Label).where(Label.id == label_id)
        result = await session.execute(stmt)
        label = result.scalar_one_or_none()
        if not label:
            return False
        await session.delete(label)
        await session.commit()
        return True

    async def attach_labels_to_task(
        self,
        session: AsyncSession,
        task_id: str,
        label_ids: list[str],
    ) -> list[str]:
        stmt = select(TaskLabel.label_id).where(TaskLabel.task_id == task_id)
        result = await session.execute(stmt)
        existing = set(result.scalars().all())
        for lid in label_ids:
            if lid not in existing:
                session.add(TaskLabel(task_id=task_id, label_id=lid))
        await session.commit()
        stmt2 = select(TaskLabel.label_id).where(TaskLabel.task_id == task_id)
        result2 = await session.execute(stmt2)
        return list(result2.scalars().all())

    async def detach_label_from_task(
        self,
        session: AsyncSession,
        task_id: str,
        label_id: str,
    ) -> bool:
        stmt = select(TaskLabel).where(
            TaskLabel.task_id == task_id, TaskLabel.label_id == label_id
        )
        result = await session.execute(stmt)
        link = result.scalar_one_or_none()
        if not link:
            return False
        await session.delete(link)
        await session.commit()
        return True


label_service = LabelService()
