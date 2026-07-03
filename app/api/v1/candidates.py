from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_admin, get_current_user
from app.core.exceptions import DuplicateException, NotFoundException
from app.database import get_db
from app.models.user import User
from app.schemas.candidate import (
    CandidateCreate,
    CandidateListResponse,
    CandidateResponse,
    CandidateUpdate,
)
from app.services.candidate_service import CandidateService

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.post("/", response_model=CandidateResponse, status_code=201, summary="Register a new candidate")
async def create_candidate(
    data: CandidateCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return await CandidateService(db).create(data)
    except DuplicateException as exc:
        raise HTTPException(status_code=409, detail=exc.message)


@router.get("/", response_model=CandidateListResponse, summary="List / search candidates")
async def list_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    skills: list[str] = Query(None, description="Filter by one or more skills"),
    min_experience: float = Query(None, ge=0, description="Minimum years of experience"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    candidates, total = await CandidateService(db).search(
        skills=skills, min_experience=min_experience, page=page, page_size=page_size
    )
    return CandidateListResponse(total=total, page=page, page_size=page_size, candidates=candidates)


@router.get("/{candidate_id}", response_model=CandidateResponse, summary="Get a candidate by ID")
async def get_candidate(candidate_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    candidate = await CandidateService(db).get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse, summary="Update candidate profile")
async def update_candidate(candidate_id: int, data: CandidateUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    try:
        return await CandidateService(db).update(candidate_id, data)
    except NotFoundException as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@router.delete("/{candidate_id}", status_code=204, summary="Delete a candidate (admin only)")
async def delete_candidate(candidate_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin)):
    deleted = await CandidateService(db).delete(candidate_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
