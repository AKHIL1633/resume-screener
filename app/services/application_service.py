from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import DuplicateException, NotFoundException
from app.core.logging_config import logger
from app.models.application import Application
from app.models.candidate import Candidate
from app.models.job import Job
from app.schemas.application import ApplicationCreate, ApplicationUpdate, BulkScoreRequest
from app.services.base import BaseService
from app.services.scoring_service import ScoringService


class ApplicationService(BaseService[Application]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Application, db)
        self._scoring = ScoringService()

    # ------------------------------------------------------------------
    # Create / apply
    # ------------------------------------------------------------------

    async def create(self, data: ApplicationCreate) -> Application:
        candidate = await self.db.get(Candidate, data.candidate_id)
        if not candidate:
            raise NotFoundException("Candidate", data.candidate_id)

        job = await self.db.get(Job, data.job_id)
        if not job:
            raise NotFoundException("Job", data.job_id)

        existing = await self._get_existing(data.candidate_id, data.job_id)
        if existing:
            raise DuplicateException(
                "Application", "candidate_id+job_id", f"{data.candidate_id}+{data.job_id}"
            )

        score_result = self._scoring.score_candidate(candidate, job)

        application = Application(
            candidate_id=data.candidate_id,
            job_id=data.job_id,
            notes=data.notes,
            match_score=score_result.total_score,
            score_breakdown=score_result.to_dict(),
        )
        self.db.add(application)
        await self.db.commit()
        # Re-fetch with relationships eagerly loaded so serialization works
        result = await self.db.execute(
            select(Application)
            .options(selectinload(Application.candidate), selectinload(Application.job))
            .where(Application.id == application.id)
        )
        application = result.scalar_one()
        logger.info(
            "Application created id=%d candidate=%d job=%d score=%.1f",
            application.id,
            data.candidate_id,
            data.job_id,
            score_result.total_score,
        )
        return application

    # ------------------------------------------------------------------
    # Update status
    # ------------------------------------------------------------------

    async def update_status(self, id: int, data: ApplicationUpdate) -> Application:
        app = await self.get_by_id(id)
        if not app:
            raise NotFoundException("Application", id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(app, field, value)

        await self.db.commit()
        result = await self.db.execute(
            select(Application)
            .options(selectinload(Application.candidate), selectinload(Application.job))
            .where(Application.id == id)
        )
        return result.scalar_one()

    # ------------------------------------------------------------------
    # Ranked listing for a job
    # ------------------------------------------------------------------

    async def get_ranked_for_job(
        self,
        job_id: int,
        min_score: float = 0.0,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Application], int]:
        base_filter = (Application.job_id == job_id, Application.match_score >= min_score)

        count_result = await self.db.execute(
            select(func.count()).select_from(Application).where(*base_filter)
        )
        total: int = count_result.scalar_one()

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Application)
            .options(selectinload(Application.candidate), selectinload(Application.job))
            .where(*base_filter)
            .order_by(Application.match_score.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    # ------------------------------------------------------------------
    # Bulk scoring (runs in background via FastAPI BackgroundTasks)
    # ------------------------------------------------------------------

    async def bulk_score(self, data: BulkScoreRequest) -> int:
        job = await self.db.get(Job, data.job_id)
        if not job:
            raise NotFoundException("Job", data.job_id)

        if data.candidate_ids:
            rows = await self.db.execute(
                select(Candidate).where(Candidate.id.in_(data.candidate_ids))
            )
        else:
            rows = await self.db.execute(select(Candidate))
        candidates = list(rows.scalars().all())

        ranked = self._scoring.rank_candidates(candidates, job)

        for candidate, score_result in ranked:
            app = await self._get_existing(candidate.id, data.job_id)
            if app:
                app.match_score = score_result.total_score
                app.score_breakdown = score_result.to_dict()
            else:
                self.db.add(
                    Application(
                        candidate_id=candidate.id,
                        job_id=data.job_id,
                        match_score=score_result.total_score,
                        score_breakdown=score_result.to_dict(),
                    )
                )

        await self.db.commit()
        logger.info("Bulk score complete: %d candidates for job=%d", len(ranked), data.job_id)
        return len(ranked)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _get_existing(self, candidate_id: int, job_id: int) -> Application | None:
        result = await self.db.execute(
            select(Application).where(
                Application.candidate_id == candidate_id,
                Application.job_id == job_id,
            )
        )
        return result.scalar_one_or_none()
