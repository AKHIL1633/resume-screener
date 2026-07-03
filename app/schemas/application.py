from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.application import ApplicationStatus
from app.schemas.candidate import CandidateResponse
from app.schemas.job import JobResponse


class ApplicationCreate(BaseModel):
    candidate_id: int = Field(..., examples=[1])
    job_id: int = Field(..., examples=[1])
    notes: Optional[str] = Field(None, examples=["Strong Python background; recommended by HR"])


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None


class ScoreBreakdown(BaseModel):
    total_score: float
    required_skills_score: float
    preferred_skills_score: float
    experience_score: float
    keyword_score: float
    matched_required_skills: list[str]
    matched_preferred_skills: list[str]
    missing_required_skills: list[str]


class ApplicationResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    status: ApplicationStatus
    match_score: float
    score_breakdown: dict
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    candidate: Optional[CandidateResponse] = None
    job: Optional[JobResponse] = None

    model_config = {"from_attributes": True}


class ApplicationListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    applications: list[ApplicationResponse]


class BulkScoreRequest(BaseModel):
    job_id: int = Field(..., examples=[1])
    candidate_ids: Optional[list[int]] = Field(
        None, examples=[[1, 2, 3]], description="Omit to score ALL candidates"
    )
