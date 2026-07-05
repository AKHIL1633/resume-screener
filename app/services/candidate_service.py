from sqlalchemy import String, bindparam, cast, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateException, NotFoundException
from app.core.logging_config import logger
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate
from app.services.base import BaseService


class CandidateService(BaseService[Candidate]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Candidate, db)

    async def create(self, data: CandidateCreate) -> Candidate:
        if await self.get_by_email(data.email):
            raise DuplicateException("Candidate", "email", data.email)

        candidate = Candidate(**data.model_dump())
        self.db.add(candidate)
        await self.db.commit()
        await self.db.refresh(candidate)
        logger.info("Created candidate id=%d email=%s", candidate.id, candidate.email)
        return candidate

    async def update(self, id: int, data: CandidateUpdate) -> Candidate:
        candidate = await self.get_by_id(id)
        if not candidate:
            raise NotFoundException("Candidate", id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(candidate, field, value)

        await self.db.commit()
        await self.db.refresh(candidate)
        logger.info("Updated candidate id=%d", id)
        return candidate

    async def get_by_email(self, email: str) -> Candidate | None:
        result = await self.db.execute(select(Candidate).where(Candidate.email == email))
        return result.scalar_one_or_none()

    async def search(
        self,
        skills: list[str] | None = None,
        min_experience: float | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Candidate], int]:
        query = select(Candidate)
        count_query = select(func.count()).select_from(Candidate)

        if min_experience is not None:
            query = query.where(Candidate.years_of_experience >= min_experience)
            count_query = count_query.where(Candidate.years_of_experience >= min_experience)

        # DB-level JSON skill search. On SQLite/PostgreSQL the JSON column casts
        # to text cleanly, so a quoted-substring ILIKE avoids false-prefix matches.
        # Oracle stores JSON as CLOB — a text cast either fails or forces a full
        # table scan there, so JSON_EXISTS is used instead (Oracle 12c+).
        dialect = self.db.bind.dialect.name if self.db.bind else "sqlite"
        if skills:
            for skill in skills:
                if dialect == "oracle":
                    condition = text(
                        'JSON_EXISTS(skills, \'$[*]?(@ == $skill)\' PASSING :skill_val AS "skill")'
                    ).bindparams(bindparam("skill_val", value=skill.lower(), type_=String))
                else:
                    pattern = f'%"{skill.lower()}"%'
                    condition = cast(Candidate.skills, String).ilike(pattern)
                query = query.where(condition)
                count_query = count_query.where(condition)

        total: int = (await self.db.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        rows = await self.db.execute(query.offset(offset).limit(page_size))
        return list(rows.scalars().all()), total
