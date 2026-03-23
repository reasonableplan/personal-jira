import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_db
from personal_jira.schemas.context_bundle import (
    ContextBundleCreate,
    ContextBundleResponse,
)
from personal_jira.services.context_bundle import ContextBundleService

router = APIRouter(tags=["context-bundles"])

context_bundle_service = ContextBundleService()


@router.post(
    "/issues/{issue_id}/bundles",
    response_model=ContextBundleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_bundle(
    issue_id: uuid.UUID,
    payload: ContextBundleCreate,
    db: AsyncSession = Depends(get_db),
) -> ContextBundleResponse:
    bundle = await context_bundle_service.create_bundle(db, issue_id, payload)
    return ContextBundleResponse.model_validate(bundle)


@router.get(
    "/issues/{issue_id}/bundles",
    response_model=list[ContextBundleResponse],
)
async def list_bundles(
    issue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[ContextBundleResponse]:
    bundles = await context_bundle_service.list_bundles(db, issue_id)
    return [ContextBundleResponse.model_validate(b) for b in bundles]


@router.get(
    "/issues/{issue_id}/bundles/{bundle_id}",
    response_model=ContextBundleResponse,
)
async def get_bundle(
    issue_id: uuid.UUID,
    bundle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ContextBundleResponse:
    bundle = await context_bundle_service.get_bundle(db, issue_id, bundle_id)
    return ContextBundleResponse.model_validate(bundle)


@router.delete(
    "/issues/{issue_id}/bundles/{bundle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_bundle(
    issue_id: uuid.UUID,
    bundle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    await context_bundle_service.delete_bundle(db, issue_id, bundle_id)
