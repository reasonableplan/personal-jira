import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.code_artifact import CodeArtifactCreate, CodeArtifactResponse
from services.code_artifact import CodeArtifactService

router = APIRouter(
    prefix="/api/v1/issues/{issue_id}/artifacts",
    tags=["code-artifacts"],
)


@router.post(
    "",
    response_model=CodeArtifactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_artifact(
    issue_id: uuid.UUID,
    body: CodeArtifactCreate,
    db: AsyncSession = Depends(get_db),
) -> CodeArtifactResponse:
    service = CodeArtifactService(db)
    try:
        artifact = await service.create(issue_id=issue_id, data=body)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return CodeArtifactResponse.model_validate(artifact)


@router.get("", response_model=list[CodeArtifactResponse])
async def list_artifacts(
    issue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[CodeArtifactResponse]:
    service = CodeArtifactService(db)
    artifacts = await service.list_by_issue(issue_id)
    return [CodeArtifactResponse.model_validate(a) for a in artifacts]


@router.get("/{artifact_id}", response_model=CodeArtifactResponse)
async def get_artifact(
    issue_id: uuid.UUID,
    artifact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CodeArtifactResponse:
    service = CodeArtifactService(db)
    artifact = await service.get(artifact_id)
    if artifact is None or artifact.issue_id != issue_id:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return CodeArtifactResponse.model_validate(artifact)


@router.delete("/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artifact(
    issue_id: uuid.UUID,
    artifact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    service = CodeArtifactService(db)
    artifact = await service.get(artifact_id)
    if artifact is None or artifact.issue_id != issue_id:
        raise HTTPException(status_code=404, detail="Artifact not found")
    await service.delete(artifact_id)
