"""Unit tests for the scoring engine — no DB required."""

from unittest.mock import MagicMock

import pytest

from app.models.candidate import Candidate
from app.models.job import Job
from app.services.scoring_service import (
    ScoringServiceFactory,
    WeightedScoringStrategy,
)


def _candidate(skills: list[str], years: float, resume: str = "") -> Candidate:
    c = MagicMock(spec=Candidate)
    c.id = 1
    c.skills = skills
    c.years_of_experience = years
    c.resume_text = resume
    return c


def _job(
    required: list[str],
    preferred: list[str],
    min_exp: float = 0.0,
    max_exp: float | None = None,
    description: str = "",
) -> Job:
    j = MagicMock(spec=Job)
    j.id = 1
    j.required_skills = required
    j.preferred_skills = preferred
    j.min_experience_years = min_exp
    j.max_experience_years = max_exp
    j.description = description
    return j


strategy = WeightedScoringStrategy()


def test_perfect_skill_match():
    c = _candidate(["python", "fastapi", "sqlalchemy"], 5.0)
    j = _job(["python", "fastapi", "sqlalchemy"], [], min_exp=3.0)
    result = strategy.score(c, j)
    assert result.required_skills_score == 100.0
    assert result.experience_score == 100.0
    assert result.total_score > 90


def test_partial_skill_match():
    c = _candidate(["python"], 5.0)
    j = _job(["python", "fastapi", "sqlalchemy", "oracle"], [], min_exp=3.0)
    result = strategy.score(c, j)
    assert result.required_skills_score == 25.0
    assert len(result.missing_required_skills) == 3


def test_underexperienced_candidate():
    c = _candidate(["python"], 1.0)
    j = _job(["python"], [], min_exp=5.0)
    result = strategy.score(c, j)
    assert result.experience_score == pytest.approx(20.0)
    # Experience (20% weight) = 20*0.2=4
    # required(100*0.5=50) + preferred(100*0.2=20) + keyword(50*0.1=5) = 79
    assert result.total_score == pytest.approx(79.0)
    # But underexperienced candidate scores lower than a qualified peer
    qualified = _candidate(["python"], 5.0)
    assert result.total_score < strategy.score(qualified, j).total_score


def test_overqualified_slight_penalty():
    c = _candidate(["python"], 15.0)
    j = _job(["python"], [], min_exp=3.0, max_exp=8.0)
    result = strategy.score(c, j)
    assert result.experience_score < 100.0
    assert result.experience_score >= 70.0


def test_preferred_skills_boost():
    c1 = _candidate(["python"], 5.0)
    c2 = _candidate(["python", "docker", "redis"], 5.0)
    j = _job(["python"], ["docker", "redis"], min_exp=3.0)
    r1 = strategy.score(c1, j)
    r2 = strategy.score(c2, j)
    assert r2.total_score > r1.total_score
    assert r2.preferred_skills_score == 100.0


def test_resume_keyword_boost():
    rich_resume = "FastAPI SQLAlchemy Pydantic async Python Oracle REST API OOP design patterns"
    c1 = _candidate(["python"], 5.0, resume="")
    c2 = _candidate(["python"], 5.0, resume=rich_resume)
    j = _job(["python"], [], min_exp=3.0, description="FastAPI SQLAlchemy Pydantic async Python")
    r1 = strategy.score(c1, j)
    r2 = strategy.score(c2, j)
    assert r2.keyword_score > r1.keyword_score


def test_no_required_skills_gives_full_score():
    c = _candidate([], 5.0)
    j = _job([], [], min_exp=0.0)
    result = strategy.score(c, j)
    assert result.required_skills_score == 100.0


def test_factory_creates_weighted_strategy():
    scorer = ScoringServiceFactory.create("weighted")
    assert isinstance(scorer, WeightedScoringStrategy)


def test_factory_unknown_strategy_raises():
    with pytest.raises(ValueError, match="Unknown scoring strategy"):
        ScoringServiceFactory.create("nonexistent")


def test_rank_candidates_ordered():
    strong = _candidate(["python", "fastapi", "sqlalchemy", "oracle"], 6.0)
    weak = _candidate(["java"], 1.0)
    j = _job(["python", "fastapi", "sqlalchemy"], [], min_exp=3.0)

    from app.services.scoring_service import ScoringService

    svc = ScoringService()
    ranked = svc.rank_candidates([weak, strong], j)

    assert ranked[0][0] is strong
    assert ranked[0][1].total_score > ranked[1][1].total_score
