from fastapi import APIRouter

from app.api.v1 import applications, auth, candidates, jobs

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(candidates.router)
router.include_router(jobs.router)
router.include_router(applications.router)
