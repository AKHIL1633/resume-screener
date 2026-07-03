from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class CandidateBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, examples=["Alice Johnson"])
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30, examples=["+91-9876543210"])
    years_of_experience: float = Field(0.0, ge=0, le=50, examples=[5.0])
    education: Optional[str] = Field(None, max_length=500, examples=["B.Tech Computer Science, IIT Delhi"])
    linkedin_url: Optional[str] = Field(None, examples=["https://linkedin.com/in/alice"])


class CandidateCreate(CandidateBase):
    resume_text: Optional[str] = Field(None, examples=["Experienced Python developer..."])
    skills: list[str] = Field(default_factory=list, examples=[["python", "fastapi", "sqlalchemy"]])

    @field_validator("skills", mode="before")
    @classmethod
    def normalize_skills(cls, v: list[str]) -> list[str]:
        return [s.strip().lower() for s in v if s.strip()]


class CandidateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    phone: Optional[str] = None
    resume_text: Optional[str] = None
    skills: Optional[list[str]] = None
    years_of_experience: Optional[float] = Field(None, ge=0, le=50)
    education: Optional[str] = None
    linkedin_url: Optional[str] = None

    @field_validator("skills", mode="before")
    @classmethod
    def normalize_skills(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        return [s.strip().lower() for s in v if s.strip()]


class CandidateResponse(CandidateBase):
    id: int
    skills: list[str]
    resume_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CandidateListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    candidates: list[CandidateResponse]
