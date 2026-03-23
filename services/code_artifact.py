import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.code_artifact import CodeArtifact, ArtifactType
from models.issue import Issue
from schemas.code_artifact import CodeArtifactCreate
from workflows.issue_status import IssueStatus, is_valid_transition

AUTO_REVIEW_TRIGGER_TYPES: set[ArtifactType] = {ArtifactType.COMMIT}


class CodeArtifactService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, *, issue_id: uuid.UUID, data: CodeArtifactCreate
    ) -> CodeArtifact:
        result = await self._session.execute(
            select(Issue).where(Issue.id == issue_id)
        )
        issue = result.scalar_one_or_none()
        if issue is None:
            raise ValueError("Issue not found")

        artifact = CodeArtifact(
            issue_id=issue_id,
            artifact_type=data.artifact_type,
            identifier=data.identifier,
            metadata_=data.metadata_,
        )
        self._session.add(artifact)

        if data.artifact_type in AUTO_REVIEW_TRIGGER_TYPES:
            if is_valid_transition(issue.status, IssueStatus.IN_REVIEW):
                issue.status = IssueStatus.IN_REVIEW

        await self._session.commit()
        await self._session.refresh(artifact)
        return artifact

    async def list_by_issue(self, issue_id: uuid.UUID) -> list[CodeArtifact]:
        result = await self._session.execute(
            select(CodeArtifact)
            .where(CodeArtifact.issue_id == issue_id)
            .order_by(CodeArtifact.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, artifact_id: uuid.UUID) -> CodeArtifact | None:
        result = await self._session.execute(
            select(CodeArtifact).where(CodeArtifact.id == artifact_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, artifact_id: uuid.UUID) -> bool:
        artifact = await self.get(artifact_id)
        if artifact is None:
            return False
        await self._session.delete(artifact)
        await self._session.commit()
        return True
