from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .core.config import settings
from .core.redis import redis_service
from .core.middleware import RateLimitMiddleware
from .db.database import sync_engine, Base
from .api.v1.auth import router as auth_router
from .api.v1.workouts import router as workout_router
from .api.v1.users import router as profile_router
from .api.v1.plans import router as plan_router
from .api.v1.routines import router as routine_router
from .api.v1.social import router as social_router
from .api.v1.stats import router as stats_router
from .api.v1.dashboard import router as dashboard_router
from .api.v1.voice_commands import router as voice_router
from .api.v1.websockets import router as ws_router
from .api.v1.water import router as water_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

# Exception handler for database integrity errors (e.g. unique constraints)
@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    logger.error(f"Integrity error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Database integrity error. This usually means a unique constraint failed (e.g. username or email already exists)."},
    )

# General exception handler to ensure CORS headers on 500s
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please check server logs."},
    )

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        loc = error.get("loc")
        msg = error.get("msg")
        # Simplify error message for frontend
        field = loc[-1] if loc else "field"
        errors.append(f"{field}: {msg}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": ", ".join(errors)},
    )

# Create database tables (Sync for startup, better to use Alembic in prod)
# Only run this if not using migrations
# Base.metadata.create_all(bind=sync_engine)

@app.on_event("startup")
async def startup_event():
    await redis_service.connect()
    # If using postgres, we might want to ensure connection here

@app.on_event("shutdown")
async def shutdown_event():
    await redis_service.disconnect()

# Security headers middleware
# @app.middleware("http")
# async def add_security_headers(request: Request, call_next):
#    ... (rest of the code)

@app.get("/api/v1/test")
async def test_endpoint():
    return {"status": "ok"}

# Include API routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(workout_router, prefix=settings.API_V1_STR)
app.include_router(profile_router, prefix=settings.API_V1_STR)
app.include_router(plan_router, prefix=settings.API_V1_STR)
app.include_router(routine_router, prefix=settings.API_V1_STR)
app.include_router(social_router, prefix=settings.API_V1_STR)
app.include_router(stats_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(voice_router, prefix=settings.API_V1_STR)
app.include_router(ws_router, prefix=settings.API_V1_STR)
app.include_router(water_router, prefix=settings.API_V1_STR)

# Add RateLimitMiddleware
app.add_middleware(RateLimitMiddleware, redis_service=redis_service, limit=100, window=60)

# CORS configuration (Added LAST so it wraps everything else and runs FIRST for requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "Backend running", 
        "docs_url": "/docs"
    }
