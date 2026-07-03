from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.logging_config import logger
from app.models.job import Job, JobStatus
from app.schemas.job import JobCreate, JobUpdate
from app.services.base import BaseService


class JobService(BaseService[Job]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Job, db)

    async def create(self, data: JobCreate) -> Job:
        job = Job(**data.model_dump())
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        logger.info("Created job id=%d title=%r", job.id, job.title)
        return job

    async def update(self, id: int, data: JobUpdate) -> Job:
        job = await self.get_by_id(id)
        if not job:
            raise NotFoundException("Job", id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(job, field, value)

        await self.db.commit()
        await self.db.refresh(job)
        logger.info("Updated job id=%d", id)
        return job

    async def get_active(self) -> list[Job]:
        result = await self.db.execute(select(Job).where(Job.status == JobStatus.ACTIVE))
        return list(result.scalars().all())
