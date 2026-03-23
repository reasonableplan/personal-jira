from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.claim import ClaimRequest, ClaimResponse
from app.services.claim import ClaimService
from app.services.exceptions import AgentNotFoundError, AgentSkillMismatchError

router = APIRouter(prefix="/api/v1/issues", tags=["claim"])


@router.post("/claim", responses={200: {"model": ClaimResponse}, 204: {"description": "No claimable issue"}})
async def claim_issue(req: ClaimRequest, db: AsyncSession = Depends(get_db)):
    svc = ClaimService(db)
    try:
        issue = await svc.claim(req)
    except AgentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AgentSkillMismatchError as e:
        raise HTTPException(status_code=409, detail=str(e))

    if issue is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return ClaimResponse.model_validate(issue)
