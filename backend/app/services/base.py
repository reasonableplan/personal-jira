from typing import Any

from app.models import Base
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20


class GenericCRUDService[ModelT: Base, CreateSchemaT: BaseModel, UpdateSchemaT: BaseModel]:
    model: type[ModelT]

    async def get_by_id(self, session: AsyncSession, entity_id: str) -> ModelT | None:
        stmt = select(self.model).where(self.model.id == entity_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        session: AsyncSession,
        *,
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE,
        filters: list[Any] | None = None,
    ) -> tuple[list[ModelT], int]:
        base = select(self.model)
        if filters:
            for f in filters:
                base = base.where(f)
        count_stmt = select(func.count()).select_from(base.subquery())
        count_result = await session.execute(count_stmt)
        total = count_result.scalar_one()
        offset = (page - 1) * per_page
        items_stmt = base.offset(offset).limit(per_page)
        items_result = await session.execute(items_stmt)
        items = list(items_result.scalars().all())
        return items, total

    async def create(self, session: AsyncSession, schema: CreateSchemaT) -> ModelT:
        data = schema.model_dump(exclude_unset=True)
        instance = self.model(**data)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    async def update(
        self, session: AsyncSession, entity_id: str, schema: UpdateSchemaT
    ) -> ModelT | None:
        instance = await self.get_by_id(session, entity_id)
        if instance is None:
            return None
        data = schema.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(instance, key, value)
        await session.flush()
        await session.refresh(instance)
        return instance

    async def delete(self, session: AsyncSession, entity_id: str) -> bool:
        instance = await self.get_by_id(session, entity_id)
        if instance is None:
            return False
        await session.delete(instance)
        await session.flush()
        return True
