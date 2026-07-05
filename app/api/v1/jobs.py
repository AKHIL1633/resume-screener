from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_admin, get_current_user
from app.core.exceptions import NotFoundException
from app.database import get_db
from app.models.user import User
from app.schemas.job import JobCreate, JobListResponse, JobResponse, JobUpdate
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobResponse, status_code=201, summary="Create a job posting")
async def create_job(
    data: JobCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    return await JobService(db).create(data)


@router.get("/", response_model=JobListResponse, summary="List all job postings")
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    jobs, total = await JobService(db).get_all(page=page, page_size=page_size)
    return JobListResponse(total=total, page=page, page_size=page_size, jobs=jobs)


@router.get("/active", response_model=list[JobResponse], summary="List active job postings")
async def get_active_jobs(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    return await JobService(db).get_active()


@router.get("/{job_id}", response_model=JobResponse, summary="Get a job by ID")
async def get_job(
    job_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    job = await JobService(db).get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@router.put("/{job_id}", response_model=JobResponse, summary="Update a job posting")
async def update_job(
    job_id: int,
    data: JobUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return await JobService(db).update(job_id, data)
    except NotFoundException as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@router.delete("/{job_id}", status_code=204, summary="Delete a job posting (admin only)")
async def delete_job(
    job_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin)
):
    deleted = await JobService(db).delete(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
