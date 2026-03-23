import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue
from personal_jira.models.template import IssueTemplate
from personal_jira.schemas.template import CloneIssueRequest, TemplateCreate

DEFAULT_STATUS = "backlog"


class TemplateService:
    async def create(self, db: AsyncSession, data: TemplateCreate) -> IssueTemplate:
        template = IssueTemplate(
            name=data.name,
            title_pattern=data.title_pattern,
            description_template=data.description_template,
            default_priority=data.default_priority,
            default_issue_type=data.default_issue_type,
            default_labels=data.default_labels,
        )
        db.add(template)
        await db.commit()
        await db.refresh(template)
        return template

    async def get_by_id(
        self, db: AsyncSession, template_id: uuid.UUID
    ) -> IssueTemplate | None:
        stmt = select(IssueTemplate).where(IssueTemplate.id == template_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, db: AsyncSession) -> list[IssueTemplate]:
        stmt = select(IssueTemplate).order_by(IssueTemplate.name)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_issue_from_template(
        self,
        db: AsyncSession,
        template_id: uuid.UUID,
        variables: dict[str, str],
    ) -> Issue:
        template = await self.get_by_id(db, template_id)
        if template is None:
            raise ValueError("Template not found")

        title = template.title_pattern.format_map(variables)
        description = None
        if template.description_template:
            description = template.description_template.format_map(variables)

        issue = Issue(
            title=title,
            description=description,
            priority=template.default_priority,
            issue_type=template.default_issue_type,
            status=DEFAULT_STATUS,
        )
        db.add(issue)
        await db.commit()
        await db.refresh(issue)
        return issue

    async def clone_issue(
        self,
        db: AsyncSession,
        issue_id: uuid.UUID,
        request: CloneIssueRequest,
    ) -> Issue:
        stmt = select(Issue).where(Issue.id == issue_id)
        result = await db.execute(stmt)
        original = result.scalar_one_or_none()
        if original is None:
            raise ValueError("Issue not found")

        title = original.title
        if request.title_prefix:
            title = f"{request.title_prefix} {original.title}"

        status = DEFAULT_STATUS if request.reset_status else original.status

        cloned = Issue(
            title=title,
            description=original.description,
            priority=original.priority,
            issue_type=original.issue_type,
            status=status,
        )
        db.add(cloned)
        await db.commit()
        await db.refresh(cloned)
        return cloned
