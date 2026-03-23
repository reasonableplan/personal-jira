import json
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.template import IssueTemplate
from personal_jira.models.issue import Issue


class DuplicateTemplateNameError(Exception):
    pass


class TemplateService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        name: str,
        title_pattern: str,
        description: str | None = None,
        priority: str | None = None,
        labels: list[str] | None = None,
    ) -> IssueTemplate:
        template = IssueTemplate(
            name=name,
            title_pattern=title_pattern,
            description=description,
            priority=priority,
            labels=json.dumps(labels or []),
        )
        self._session.add(template)
        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise DuplicateTemplateNameError(f"Template '{name}' already exists")
        await self._session.refresh(template)
        return template

    async def list_all(self) -> list[IssueTemplate]:
        result = await self._session.execute(select(IssueTemplate))
        return list(result.scalars().all())

    async def get(self, template_id: uuid.UUID) -> IssueTemplate | None:
        return await self._session.get(IssueTemplate, template_id)

    async def delete(self, template_id: uuid.UUID) -> bool:
        template = await self._session.get(IssueTemplate, template_id)
        if not template:
            return False
        await self._session.delete(template)
        await self._session.commit()
        return True

    async def create_issue_from_template(
        self, template_id: uuid.UUID, summary: str
    ) -> Issue | None:
        template = await self._session.get(IssueTemplate, template_id)
        if not template:
            return None
        title = template.title_pattern.replace("{summary}", summary)
        labels_list: list[str] = json.loads(template.labels)
        issue = Issue(
            title=title,
            description=template.description,
            priority=template.priority or "medium",
            labels=json.dumps(labels_list) if labels_list else None,
        )
        self._session.add(issue)
        await self._session.commit()
        await self._session.refresh(issue)
        return issue

    async def clone_issue(
        self, issue_id: uuid.UUID, title_override: str | None = None
    ) -> Issue | None:
        original = await self._session.get(Issue, issue_id)
        if not original:
            return None
        clone = Issue(
            title=title_override or f"[CLONE] {original.title}",
            description=original.description,
            priority=original.priority,
            labels=original.labels,
            parent_id=original.parent_id,
        )
        self._session.add(clone)
        await self._session.commit()
        await self._session.refresh(clone)
        return clone

    def _to_response(self, template: IssueTemplate) -> dict[str, Any]:
        return {
            "id": str(template.id),
            "name": template.name,
            "title_pattern": template.title_pattern,
            "description": template.description,
            "priority": template.priority,
            "labels": json.loads(template.labels),
            "created_at": str(template.created_at),
            "updated_at": str(template.updated_at),
        }
