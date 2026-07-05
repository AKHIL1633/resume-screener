import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import router
from app.config import _INSECURE_DEFAULT, get_settings
from app.core.logging_config import logger
from app.database import AsyncSessionLocal as async_session_maker
from app.database import init_db

settings = get_settings()

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.secret_key == _INSECURE_DEFAULT:
        logger.warning(
            "SECRET_KEY is using the insecure default. "
            "Set SECRET_KEY in .env before deploying to production."
        )
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    await init_db()
    logger.info("Database tables ready")
    yield
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "**ResumeIQ** — automated resume screening and candidate ranking system.\n\n"
        "Automatically scores candidates against job requirements using a weighted "
        "algorithm that considers skills, experience, and keyword density."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "%s %s -> %d (%.1f ms) [%s]",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
        request_id,
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, (HTTPException, StarletteHTTPException, RequestValidationError)):
        raise exc
    logger.error(
        "Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router)


@app.get("/health", tags=["Health"], summary="Health check with DB ping")
async def health_check():
    from sqlalchemy import text

    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        logger.error("Health check DB ping failed: %s", exc)
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "db": db_status,
        "version": settings.app_version,
        "app": settings.app_name,
    }
