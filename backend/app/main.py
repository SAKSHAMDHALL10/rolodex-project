"""
FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.startup_checks import validate_gemini_models
from app.routers import contacts, dashboard, search

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("rolodex")


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_gemini_models()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered searchable rolodex: turns LinkedIn profiles into "
    "structured, semantically searchable professional-relevance entries.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.get("/health", tags=["meta"])
def health():
    """
    Pure liveness check - always 200 if the process can serve requests at
    all. Deliberately does not touch the database, so a transient Supabase
    blip doesn't cause Render to treat the whole service as crashed and
    restart it. Use /health/ready to check actual database connectivity.
    """
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/health/ready", tags=["meta"])
def health_ready(db: Session = Depends(get_db)):
    """
    Readiness check: confirms the database is actually reachable. Point
    deployment smoke tests / manual verification here, not just /health -
    a service can be "alive" while completely unable to reach Supabase.
    """
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        # Log full detail server-side for debugging, but don't echo raw driver
        # internals back in this public, unauthenticated response - some
        # database errors can include connection parameters in their message.
        logger.error("Readiness check failed: database unreachable: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unavailable",
                "database": "unreachable",
                "detail": "Database connection failed. Check server logs for details.",
            },
        )
    return {"status": "ok", "database": "connected"}


app.include_router(contacts.router, prefix=settings.API_V1_PREFIX)
app.include_router(search.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)
