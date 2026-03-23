import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue
from personal_jira.models.issue_template import IssueTemplate
from personal_jira.schemas.issue_template import (
    IssueCloneRequest,
    IssueFromTemplateRequest,
    IssueTemplateCreate,
    IssueTemplateUpdate,
)

logger = logging.getLogger(__name__)

DEFAULT_CLONE_STATUS = "open"


class TemplateService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_template(
        self, data: IssueTemplateCreate
    ) -> IssueTemplate:
        template = IssueTemplate(**data.model_dump())
        self._db.add(template)
        await self._db.commit()
        await self._db.refresh(template)
        return template

    async def get_template(
        self, template_id: uuid.UUID
    ) -> Optional[IssueTemplate]:
        stmt = select(IssueTemplate).where(IssueTemplate.id == template_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_templates(
        self, skip: int = 0, limit: int = 50
    ) -> list[IssueTemplate]:
        stmt = (
            select(IssueTemplate)
            .order_by(IssueTemplate.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def update_template(
        self, template_id: uuid.UUID, data: IssueTemplateUpdate
    ) -> Optional[IssueTemplate]:
        template = await self.get_template(template_id)
        if template is None:
            return None

        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(template, field, value)

        template.updated_at = datetime.now(timezone.utc)
        await self._db.commit()
        await self._db.refresh(template)
        return template

    async def delete_template(self, template_id: uuid.UUID) -> bool:
        template = await self.get_template(template_id)
        if template is None:
            return False

        await self._db.delete(template)
        await self._db.commit()
        return True

    async def create_issue_from_template(
        self, req: IssueFromTemplateRequest
    ) -> Issue:
        template = await self.get_template(req.template_id)
        if template is None:
            raise ValueError(f"Template not found: {req.template_id}")

        issue = Issue(
            title=req.title_override or template.default_title or "",
            description=req.description_override or template.default_description,
            priority=req.priority_override or template.default_priority,
            issue_type=template.default_issue_type,
            status=DEFAULT_CLONE_STATUS,
            parent_id=req.parent_id,
            assignee=req.assignee,
        )
        self._db.add(issue)
        await self._db.commit()
        await self._db.refresh(issue)
        logger.info(
            "Created issue %s from template %s", issue.id, template.id
        )
        return issue

    async def clone_issue(
        self, issue_id: uuid.UUID, req: IssueCloneRequest
    ) -> Issue:
        stmt = select(Issue).where(Issue.id == issue_id)
        result = await self._db.execute(stmt)
        original = result.scalar_one_or_none()
        if original is None:
            raise ValueError(f"Issue not found: {issue_id}")

        cloned = Issue(
            title=f"{req.title_prefix}{original.title}",
            description=original.description,
            priority=original.priority,
            issue_type=original.issue_type,
            status=DEFAULT_CLONE_STATUS,
            parent_id=original.parent_id,
        )
        self._db.add(cloned)
        await self._db.commit()
        await self._db.refresh(cloned)

        if req.include_comments:
            await self._clone_comments(issue_id, cloned.id)

        if req.include_work_logs:
            await self._clone_work_logs(issue_id, cloned.id)

        if req.include_children:
            await self._clone_children(issue_id, cloned.id, req)

        logger.info("Cloned issue %s -> %s", issue_id, cloned.id)
        return cloned

    async def _clone_comments(
        self, source_id: uuid.UUID, target_id: uuid.UUID
    ) -> None:
        from personal_jira.models.comment import Comment

        stmt = select(Comment).where(Comment.issue_id == source_id)
        result = await self._db.execute(stmt)
        comments = result.scalars().all()

        for comment in comments:
            cloned_comment = Comment(
                issue_id=target_id,
                author=comment.author,
                content=comment.content,
            )
            self._db.add(cloned_comment)

        if comments:
            await self._db.commit()

    async def _clone_work_logs(
        self, source_id: uuid.UUID, target_id: uuid.UUID
    ) -> None:
        from personal_jira.models.work_log import WorkLog

        stmt = select(WorkLog).where(WorkLog.issue_id == source_id)
        result = await self._db.execute(stmt)
        logs = result.scalars().all()

        for log in logs:
            cloned_log = WorkLog(
                issue_id=target_id,
                agent_id=log.agent_id,
                description=log.description,
                duration_minutes=log.duration_minutes,
            )
            self._db.add(cloned_log)

        if logs:
            await self._db.commit()

    async def _clone_children(
        self,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        req: IssueCloneRequest,
    ) -> None:
        stmt = select(Issue).where(Issue.parent_id == source_id)
        result = await self._db.execute(stmt)
        children = result.scalars().all()

        for child in children:
            child_clone = Issue(
                title=f"{req.title_prefix}{child.title}",
                description=child.description,
                priority=child.priority,
                issue_type=child.issue_type,
                status=DEFAULT_CLONE_STATUS,
                parent_id=target_id,
            )
            self._db.add(child_clone)

        if children:
            await self._db.commit()
