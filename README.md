# ResumeIQ — AI-Powered Resume Screening API

![CI](https://github.com/AKHIL1633/resume-screener/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![License](https://img.shields.io/badge/license-MIT-green)

A production-quality Python backend that automatically scores and ranks candidates against job requirements — so hiring teams spend time on the best fits, not manual shortlisting.

---

## Highlights

What this project demonstrates for a Python backend role:

- **Async Python at the core** — FastAPI + SQLAlchemy 2.0 async ORM, not just sync views bolted onto async routes
- **Real auth, not a toy example** — JWT access/refresh rotation, hashed opaque refresh tokens, role-based access control
- **Tested** — 35 pytest-asyncio tests (service-layer unit tests + API integration tests), enforced in CI
- **CI/CD** — GitHub Actions matrix across Python 3.11/3.12, ruff lint, Docker build verification
- **Schema managed properly** — Alembic migrations versioned in git, no `create_all()` in production
- **Applied OOP/design patterns** — Strategy + Factory for scoring, generic `BaseService[T]`, dependency injection throughout
- **Containerized** — multi-stage Docker build, non-root user, healthcheck, one-command `docker-compose up`
- **Full-stack context** — React/TypeScript frontend included, showing comfort working across the API boundary

---

## Features

- **JWT Authentication** — register, login, access + refresh token pair, role-based access (admin / recruiter / viewer)
- **Refresh token rotation** — opaque tokens hashed in DB, rotated on every use, server-side logout
- **Rate limiting** — 200 requests/minute per IP via `slowapi`
- **Request correlation IDs** — every response carries `X-Request-ID` for end-to-end tracing
- **Candidate management** — create profiles with skills, experience, resume text, LinkedIn
- **Job postings** — required & preferred skills, experience range, department, status lifecycle
- **Automatic scoring** — every application is scored instantly on submission
- **Ranked leaderboard** — `GET /applications/job/{id}` returns candidates ordered by match score
- **Bulk scoring** — score all candidates against a job in one async background call
- **DB-level skill search** — candidate search filters by skill at the database layer (no post-filtering in Python)
- **Alembic migrations** — schema versioned in git, zero `create_all()` in production
- **React frontend** — TypeScript + Vite + Tailwind, with toast notifications and auto-refresh-on-401
- **Docker ready** — multi-stage build, non-root user, healthcheck, `docker-compose up` in one step
- **CI/CD** — GitHub Actions runs tests on Python 3.11 & 3.12, lints with ruff, verifies Docker build
- **Makefile** — `make run`, `make test`, `make migrate`, `make docker-up` shortcuts
- **Pre-commit hooks** — ruff lint + format enforced before every commit

---

## Scoring Algorithm

Each application receives a weighted match score out of 100:

```
Match Score = 50% × Required Skills Match
            + 20% × Experience (years vs. job range)
            + 20% × Preferred Skills Match
            + 10% × Keyword Density in Resume Text
```

The engine uses the **Strategy pattern** — new algorithms can be plugged in without changing any route or service code.

```python
# Register a custom scoring strategy at runtime
ScoringServiceFactory.register("semantic", MySemanticScorer)
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Application                     │
│                                                         │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────────┐ │
│  │  /auth   │  │/candidates│  │ /jobs  /applications  │ │
│  └────┬─────┘  └─────┬─────┘  └──────────┬───────────┘ │
│       │              │                    │             │
│  ─────────────── Depends() ───────────────────────────  │
│       │  get_current_user / get_current_admin           │
│       ▼              ▼                    ▼             │
│  ┌────────────────────────────────────────────────────┐ │
│  │                  Service Layer                     │ │
│  │  AuthService │ CandidateService │ JobService       │ │
│  │              │ ApplicationService                  │ │
│  │              │ ScoringService (Strategy + Factory) │ │
│  └──────────────────────┬─────────────────────────────┘ │
│                         │ async SQLAlchemy 2.0           │
│  ┌──────────────────────▼─────────────────────────────┐ │
│  │        ORM Models (Base + TimestampMixin)          │ │
│  │  User │ RefreshToken │ Candidate │ Job │ Application│ │
│  └──────────────────────┬─────────────────────────────┘ │
└─────────────────────────┼───────────────────────────────┘
                          │
              ┌───────────▼────────────┐
              │   SQLite (dev/test)    │
              │   Oracle DB (prod)     │
              └────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 (async) |
| Validation | Pydantic v2 |
| Auth | JWT (`python-jose`) + `passlib[bcrypt]` + opaque refresh tokens |
| Rate limiting | `slowapi` |
| DB (dev) | SQLite + `aiosqlite` |
| DB (prod) | Oracle DB via `cx_Oracle` / `oracledb` |
| Migrations | Alembic |
| Testing | pytest-asyncio + httpx (35 tests) |
| Container | Docker multi-stage + docker-compose |
| CI | GitHub Actions (3.11 + 3.12 matrix) |
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Frontend data | TanStack Query + Axios |

---

## Project Structure

```
resume_screener/
├── app/
│   ├── main.py                 # App factory, rate limiter, request ID middleware, lifespan
│   ├── config.py               # Pydantic BaseSettings (.env driven, SECRET_KEY validated)
│   ├── database.py             # Async engine + get_db dependency
│   ├── api/v1/
│   │   ├── auth.py             # /register  /login  /refresh  /logout  /me
│   │   ├── candidates.py       # CRUD for candidate profiles
│   │   ├── jobs.py             # CRUD for job postings
│   │   └── applications.py     # Apply, rank, bulk-score
│   ├── models/
│   │   ├── user.py             # User + UserRole enum
│   │   ├── token.py            # RefreshToken (hashed, expires_at, is_revoked)
│   │   ├── candidate.py
│   │   ├── job.py
│   │   └── application.py
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/
│   │   ├── base.py             # Generic BaseService[T] — DRY CRUD
│   │   ├── scoring_service.py  # Strategy + Factory pattern
│   │   ├── auth_service.py     # register, login, refresh, logout
│   │   ├── candidate_service.py
│   │   ├── job_service.py
│   │   └── application_service.py
│   └── core/
│       ├── security.py         # JWT encode/decode, bcrypt, refresh token helpers
│       ├── dependencies.py     # get_current_user, get_current_admin
│       ├── exceptions.py       # Typed exception hierarchy
│       └── logging_config.py   # Structured logging
├── alembic/
│   └── versions/
│       ├── 0001_initial_schema.py
│       └── 0002_refresh_tokens.py
├── tests/                      # 35 async tests
│   ├── conftest.py             # Fixtures, auth bypass for unit tests
│   ├── test_auth.py
│   ├── test_candidates.py
│   ├── test_jobs.py
│   ├── test_applications.py
│   └── test_scoring.py         # Pure unit tests (no DB)
├── frontend/
│   ├── src/
│   │   ├── api/                # Axios client (auto-refresh on 401), auth.ts
│   │   ├── components/         # Modal, SkillTag, ScoreBar, Pagination, ...
│   │   ├── context/            # AuthContext (login, logout, refresh token)
│   │   ├── pages/              # Dashboard, Jobs, Candidates, JobRankings
│   │   └── types/              # Shared TypeScript interfaces
│   └── nginx.conf              # SPA routing + /api proxy
├── Makefile                    # Developer shortcuts
├── .pre-commit-config.yaml     # ruff lint/format + standard hooks
├── Dockerfile                  # Multi-stage build
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── .env.example
```

---

## Quick Start

### Option 1 — Make (recommended)

```bash
git clone https://github.com/AKHIL1633/resume-screener.git
cd resume-screener
cp .env.example .env          # edit SECRET_KEY at minimum
make install                  # pip install -r requirements.txt
make migrate                  # alembic upgrade head
make run                      # uvicorn on :8000
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

### Option 2 — Manual

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

### Option 3 — Docker

```bash
cp .env.example .env
make docker-up                # or: docker-compose up --build
```

API at **http://localhost:8000**, frontend at **http://localhost:3000**.

### Frontend development

```bash
make frontend-dev             # installs deps + runs Vite dev server on :5173
```

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Required — must be ≥ 32 characters
SECRET_KEY=your-very-secret-key-generated-with-openssl-rand-hex-32

# Optional overrides (defaults shown)
DATABASE_URL=sqlite+aiosqlite:///./resume_screener.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
LOG_LEVEL=INFO
DEBUG=false
```

Generate a secure key:
```bash
openssl rand -hex 32
```

---

## API Reference

### Auth

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/register` | — | Create user account |
| POST | `/api/v1/auth/login` | — | Get access + refresh token |
| POST | `/api/v1/auth/refresh` | — | Rotate refresh token |
| POST | `/api/v1/auth/logout` | — | Revoke refresh token |
| GET | `/api/v1/auth/me` | Bearer | Current user info |

### Candidates

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST | `/api/v1/candidates/` | Recruiter+ | Register candidate |
| GET | `/api/v1/candidates/` | Recruiter+ | Search (filter by skills, experience) |
| GET | `/api/v1/candidates/{id}` | Recruiter+ | Get candidate |
| PUT | `/api/v1/candidates/{id}` | Recruiter+ | Update profile |
| DELETE | `/api/v1/candidates/{id}` | **Admin** | Delete candidate |

### Jobs

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST | `/api/v1/jobs/` | Recruiter+ | Create job posting |
| GET | `/api/v1/jobs/` | Recruiter+ | List all jobs |
| GET | `/api/v1/jobs/active` | Recruiter+ | Active jobs only |
| PUT | `/api/v1/jobs/{id}` | Recruiter+ | Update job |
| DELETE | `/api/v1/jobs/{id}` | **Admin** | Delete job |

### Applications

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST | `/api/v1/applications/` | Recruiter+ | Apply + auto-score |
| GET | `/api/v1/applications/job/{id}` | Recruiter+ | **Ranked candidates for a job** |
| PATCH | `/api/v1/applications/{id}` | Recruiter+ | Update status |
| DELETE | `/api/v1/applications/{id}` | **Admin** | Delete application |
| POST | `/api/v1/applications/bulk-score` | Recruiter+ | Score all candidates async (202) |

### Example: submit and rank candidates

```bash
# 1. Register and login
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"hr@company.com","full_name":"HR Manager","password":"Str0ng!Pass"}'

TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"hr@company.com","password":"Str0ng!Pass"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. Create a job
JOB_ID=$(curl -s -X POST http://localhost:8000/api/v1/jobs/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"Python Backend Developer","description":"FastAPI SQLAlchemy async Python Oracle","required_skills":["python","fastapi","sqlalchemy"],"preferred_skills":["oracle","docker"],"min_experience_years":3}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 3. Add a candidate and apply
CAND_ID=$(curl -s -X POST http://localhost:8000/api/v1/candidates/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@dev.com","skills":["python","fastapi","sqlalchemy","docker"],"years_of_experience":5}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['id'])")

curl -X POST http://localhost:8000/api/v1/applications/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"candidate_id\":$CAND_ID,\"job_id\":$JOB_ID}"

# 4. Get ranked candidates
curl "http://localhost:8000/api/v1/applications/job/$JOB_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Running Tests

```bash
make test                              # all 35 tests
pytest tests/test_scoring.py -v       # unit tests only (no DB)
pytest --tb=short -q                   # compact output
```

Tests use an in-memory SQLite DB and bypass auth via `dependency_overrides` — no real tokens needed.

---

## Switching to Oracle DB

Change one line in `.env`:

```env
DATABASE_URL=oracle+cx_oracle://username:password@hostname:1521/ORCL
```

Uncomment `cx-Oracle` or `oracledb` in `requirements.txt`, then re-run migrations:

```bash
alembic upgrade head
```

No application code changes required.

---

## OOP & Design Patterns Used

| Pattern | Where |
|---|---|
| **Strategy** | `ScoringStrategy` ABC → `WeightedScoringStrategy` |
| **Factory** | `ScoringServiceFactory.create("weighted")` |
| **Generic Base** | `BaseService[T]` — inherited by all 4 services |
| **Repository** | Service layer abstracts all DB queries from routes |
| **Dependency Injection** | FastAPI `Depends()` for DB session and auth |
| **Mixin** | `TimestampMixin` adds `created_at`/`updated_at` to every model |

---

## License

MIT — free to use, modify, and distribute.
