"""
Resume scoring engine.

Design patterns used:
  - Strategy   : ScoringStrategy ABC + WeightedScoringStrategy implementation
  - Factory    : ScoringServiceFactory creates strategies by name
  - Data class : ScoreResult carries all scoring metadata
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import ClassVar

from app.models.candidate import Candidate
from app.models.job import Job
from app.core.logging_config import logger


@dataclass
class ScoreResult:
    total_score: float
    required_skills_score: float
    preferred_skills_score: float
    experience_score: float
    keyword_score: float
    matched_required_skills: list[str]
    matched_preferred_skills: list[str]
    missing_required_skills: list[str]

    def to_dict(self) -> dict:
        return {k: round(v, 2) if isinstance(v, float) else v for k, v in asdict(self).items()}


# ---------------------------------------------------------------------------
# Strategy ABC
# ---------------------------------------------------------------------------

class ScoringStrategy(ABC):
    @abstractmethod
    def score(self, candidate: Candidate, job: Job) -> ScoreResult:
        ...


# ---------------------------------------------------------------------------
# Concrete strategy
# ---------------------------------------------------------------------------

_STOP_WORDS: frozenset[str] = frozenset(
    "the a an and or but in on at to for of with is are was were be been "
    "have has had do does did will would could should may might shall can "
    "this that these those we you he she it they our your".split()
)


class WeightedScoringStrategy(ScoringStrategy):
    """
    Score = 50 % required skills
           + 20 % experience
           + 20 % preferred skills
           + 10 % keyword density in resume text
    """

    WEIGHTS: ClassVar[dict[str, float]] = {
        "required_skills": 0.50,
        "experience": 0.20,
        "preferred_skills": 0.20,
        "keywords": 0.10,
    }

    def score(self, candidate: Candidate, job: Job) -> ScoreResult:
        c_skills = {s.lower() for s in (candidate.skills or [])}
        req = {s.lower() for s in (job.required_skills or [])}
        pref = {s.lower() for s in (job.preferred_skills or [])}

        matched_req = sorted(req & c_skills)
        missing_req = sorted(req - c_skills)
        matched_pref = sorted(pref & c_skills)

        req_score = (len(matched_req) / len(req) * 100) if req else 100.0
        pref_score = (len(matched_pref) / len(pref) * 100) if pref else 100.0
        exp_score = self._experience_score(candidate.years_of_experience, job.min_experience_years, job.max_experience_years)
        kw_score = self._keyword_score(candidate.resume_text, job.description, job.required_skills)

        total = (
            req_score * self.WEIGHTS["required_skills"]
            + exp_score * self.WEIGHTS["experience"]
            + pref_score * self.WEIGHTS["preferred_skills"]
            + kw_score * self.WEIGHTS["keywords"]
        )

        return ScoreResult(
            total_score=round(total, 2),
            required_skills_score=round(req_score, 2),
            preferred_skills_score=round(pref_score, 2),
            experience_score=round(exp_score, 2),
            keyword_score=round(kw_score, 2),
            matched_required_skills=matched_req,
            matched_preferred_skills=matched_pref,
            missing_required_skills=missing_req,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _experience_score(years: float, min_years: float, max_years: float | None) -> float:
        if min_years == 0:
            return 100.0
        if years >= min_years:
            if max_years and years > max_years:
                # Slightly overqualified — small penalty (minimum 70)
                return max(70.0, 100.0 - (years - max_years) * 5)
            return 100.0
        return round((years / min_years) * 100, 2)

    @staticmethod
    def _keyword_score(resume_text: str | None, job_desc: str, required_skills: list[str]) -> float:
        if not resume_text:
            return 50.0

        resume_lower = resume_text.lower()
        keywords = WeightedScoringStrategy._extract_keywords(job_desc) | {s.lower() for s in required_skills}
        if not keywords:
            return 50.0

        matched = sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", resume_lower))
        return round(matched / len(keywords) * 100, 2)

    @staticmethod
    def _extract_keywords(text: str) -> set[str]:
        words = re.findall(r"\b[a-z]{3,}\b", text.lower())
        return {w for w in words if w not in _STOP_WORDS}


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class ScoringServiceFactory:
    _registry: ClassVar[dict[str, type[ScoringStrategy]]] = {
        "weighted": WeightedScoringStrategy,
    }

    @classmethod
    def create(cls, strategy: str = "weighted") -> ScoringStrategy:
        klass = cls._registry.get(strategy)
        if klass is None:
            raise ValueError(f"Unknown scoring strategy '{strategy}'. Available: {list(cls._registry)}")
        return klass()

    @classmethod
    def register(cls, name: str, strategy_class: type[ScoringStrategy]) -> None:
        cls._registry[name] = strategy_class


# ---------------------------------------------------------------------------
# Public facade
# ---------------------------------------------------------------------------

class ScoringService:
    def __init__(self, strategy: str = "weighted") -> None:
        self._strategy = ScoringServiceFactory.create(strategy)
        logger.info("ScoringService ready (strategy=%s)", strategy)

    def score_candidate(self, candidate: Candidate, job: Job) -> ScoreResult:
        result = self._strategy.score(candidate, job)
        logger.debug("score candidate=%d job=%d → %.1f", candidate.id, job.id, result.total_score)
        return result

    def rank_candidates(self, candidates: list[Candidate], job: Job) -> list[tuple[Candidate, ScoreResult]]:
        scored = [(c, self._strategy.score(c, job)) for c in candidates]
        return sorted(scored, key=lambda pair: pair[1].total_score, reverse=True)
