import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.dependencies import get_current_user
from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_resume_iq.db"

# A mock user returned by the overridden auth dependency in most tests
_MOCK_USER = User(id=1, email="recruiter@test.com", full_name="Test Recruiter", role=UserRole.RECRUITER, is_active=True)
_MOCK_ADMIN = User(id=2, email="admin@test.com", full_name="Test Admin", role=UserRole.ADMIN, is_active=True)


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db(test_engine):
    factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db: AsyncSession):
    """Authenticated as a recruiter — auth dependency is bypassed."""
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_client(db: AsyncSession):
    """Authenticated as an admin — used for DELETE endpoint tests."""
    from app.core.dependencies import get_current_admin
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: _MOCK_ADMIN
    app.dependency_overrides[get_current_admin] = lambda: _MOCK_ADMIN
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauthed_client(db: AsyncSession):
    """No auth override — used for testing the real auth flow."""
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


# ------------------------------------------------------------------
# Shared payload factories
# ------------------------------------------------------------------

def candidate_payload(**overrides) -> dict:
    base = {
        "name": "Test Candidate",
        "email": "test@example.com",
        "years_of_experience": 5.0,
        "skills": ["python", "fastapi", "sqlalchemy", "pydantic"],
        "resume_text": (
            "Experienced Python developer with strong skills in FastAPI, SQLAlchemy, "
            "Pydantic, async programming, REST API design, and Oracle database."
        ),
        "education": "B.Tech Computer Science",
    }
    base.update(overrides)
    return base


def job_payload(**overrides) -> dict:
    base = {
        "title": "Python Backend Developer",
        "description": (
            "We need a Python developer with FastAPI, SQLAlchemy, Pydantic, async "
            "programming, OOP, REST API, and Oracle experience."
        ),
        "required_skills": ["python", "fastapi", "sqlalchemy", "pydantic"],
        "preferred_skills": ["oracle", "docker", "redis"],
        "min_experience_years": 3.0,
        "max_experience_years": 8.0,
        "department": "Engineering",
    }
    base.update(overrides)
    return base
