from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.job import JobStatus


class JobBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=300, examples=["Python Backend Developer"])
    description: str = Field(..., min_length=10, examples=["We are seeking a Python developer..."])
    department: Optional[str] = Field(None, max_length=200, examples=["Engineering"])
    required_skills: list[str] = Field(
        default_factory=list, examples=[["python", "fastapi", "sqlalchemy"]]
    )
    preferred_skills: list[str] = Field(default_factory=list, examples=[["oracle", "docker"]])
    min_experience_years: float = Field(0.0, ge=0, examples=[3.0])
    max_experience_years: Optional[float] = Field(None, ge=0, examples=[8.0])

    @field_validator("required_skills", "preferred_skills", mode="before")
    @classmethod
    def normalize_skills(cls, v: list[str]) -> list[str]:
        return [s.strip().lower() for s in v if s.strip()]

    @model_validator(mode="after")
    def check_exp_range(self) -> "JobBase":
        if (
            self.max_experience_years is not None
            and self.max_experience_years < self.min_experience_years
        ):
            raise ValueError("max_experience_years must be >= min_experience_years")
        return self


class JobCreate(JobBase):
    status: JobStatus = JobStatus.ACTIVE


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    required_skills: Optional[list[str]] = None
    preferred_skills: Optional[list[str]] = None
    min_experience_years: Optional[float] = Field(None, ge=0)
    max_experience_years: Optional[float] = Field(None, ge=0)
    status: Optional[JobStatus] = None


class JobResponse(JobBase):
    id: int
    status: JobStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    jobs: list[JobResponse]
