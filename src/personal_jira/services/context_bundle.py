import logging
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.context_bundle import BundleItem, ContextBundle
from personal_jira.models.issue import Issue
from personal_jira.schemas.context_bundle import ContextBundleCreate

logger = logging.getLogger(__name__)


class ContextBundleService:
    async def _get_issue_or_404(
        self, db: AsyncSession, issue_id: uuid.UUID
    ) -> Issue:
        result = await db.execute(select(Issue).where(Issue.id == issue_id))
        issue = result.scalar_one_or_none()
        if issue is None:
            raise HTTPException(status_code=404, detail="Issue not found")
        return issue

    async def create_bundle(
        self,
        db: AsyncSession,
        issue_id: uuid.UUID,
        payload: ContextBundleCreate,
    ) -> ContextBundle:
        await self._get_issue_or_404(db, issue_id)

        bundle = ContextBundle(issue_id=issue_id)
        for item_data in payload.items:
            bundle.items.append(
                BundleItem(
                    item_type=item_data.item_type,
                    path=item_data.path,
                    content=item_data.content,
                    line_start=item_data.line_start,
                    line_end=item_data.line_end,
                )
            )

        db.add(bundle)
        await db.commit()
        await db.refresh(bundle)
        logger.info("Created context bundle %s for issue %s", bundle.id, issue_id)
        return bundle

    async def get_bundle(
        self,
        db: AsyncSession,
        issue_id: uuid.UUID,
        bundle_id: uuid.UUID,
    ) -> ContextBundle:
        result = await db.execute(
            select(ContextBundle).where(
                ContextBundle.id == bundle_id,
                ContextBundle.issue_id == issue_id,
            )
        )
        bundle = result.scalar_one_or_none()
        if bundle is None:
            raise HTTPException(status_code=404, detail="Bundle not found")
        return bundle

    async def list_bundles(
        self,
        db: AsyncSession,
        issue_id: uuid.UUID,
    ) -> list[ContextBundle]:
        result = await db.execute(
            select(ContextBundle).where(ContextBundle.issue_id == issue_id)
        )
        return list(result.scalars().all())

    async def delete_bundle(
        self,
        db: AsyncSession,
        issue_id: uuid.UUID,
        bundle_id: uuid.UUID,
    ) -> None:
        bundle = await self.get_bundle(db, issue_id, bundle_id)
        await db.delete(bundle)
        await db.commit()
        logger.info("Deleted context bundle %s for issue %s", bundle_id, issue_id)
