from __future__ import annotations

import enum

from sqlalchemy import JSON, Enum, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class JobStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    department: Mapped[str | None] = mapped_column(String(200))
    required_skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    preferred_skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    min_experience_years: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    max_experience_years: Mapped[float | None] = mapped_column(Float)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), default=JobStatus.ACTIVE, nullable=False
    )

    applications: Mapped[list[Application]] = relationship(  # noqa: F821
        "Application", back_populates="job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title!r} status={self.status}>"
