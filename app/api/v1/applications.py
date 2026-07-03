from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_admin, get_current_user
from app.core.exceptions import DuplicateException, NotFoundException
from app.core.logging_config import logger
from app.database import get_db
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationUpdate,
    BulkScoreRequest,
)
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/", response_model=ApplicationResponse, status_code=201, summary="Submit an application")
async def create_application(data: ApplicationCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    try:
        return await ApplicationService(db).create(data)
    except NotFoundException as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    except DuplicateException as exc:
        raise HTTPException(status_code=409, detail=exc.message)


@router.get(
    "/job/{job_id}",
    response_model=ApplicationListResponse,
    summary="Get ranked candidates for a job",
)
async def get_ranked_candidates(
    job_id: int,
    min_score: float = Query(0.0, ge=0, le=100, description="Minimum match score threshold"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    applications, total = await ApplicationService(db).get_ranked_for_job(
        job_id=job_id, min_score=min_score, page=page, page_size=page_size
    )
    return ApplicationListResponse(total=total, page=page, page_size=page_size, applications=applications)


@router.patch("/{application_id}", response_model=ApplicationResponse, summary="Update application status")
async def update_application(
    application_id: int, data: ApplicationUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    try:
        return await ApplicationService(db).update_status(application_id, data)
    except NotFoundException as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@router.delete("/{application_id}", status_code=204, summary="Delete an application (admin only)")
async def delete_application(application_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_admin)):
    deleted = await ApplicationService(db).delete(application_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Application {application_id} not found")


@router.post(
    "/bulk-score",
    status_code=202,
    summary="Bulk-score all candidates for a job (async background task)",
)
async def bulk_score(
    data: BulkScoreRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Fires scoring in the background using FastAPI BackgroundTasks so the
    endpoint returns immediately while processing continues asynchronously.
    """

    async def _run():
        try:
            count = await ApplicationService(db).bulk_score(data)
            logger.info("Bulk score done: %d results for job=%d", count, data.job_id)
        except Exception as exc:
            logger.error("Bulk score failed for job=%d: %s", data.job_id, exc, exc_info=True)

    background_tasks.add_task(_run)
    return {"message": "Bulk scoring started", "job_id": data.job_id}
