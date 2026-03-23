"""
ScholarGrid Backend API - Main Application Entry Point

Initializes FastAPI, registers all routers, middleware, exception handlers,
and mounts the Socket.io real-time server.
"""

from datetime import datetime, timezone

from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.exception_handlers import (
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)

# ─── FastAPI App ──────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    description=(
        "ScholarGrid Backend API — academic note-sharing platform with "
        "real-time chat, AI assistance, and comprehensive admin tools."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Authentication", "description": "User registration and profile management"},
        {"name": "Notes", "description": "Note upload, search, download, rating, and moderation"},
        {"name": "Leaderboard", "description": "Student rankings by score"},
        {"name": "Chat", "description": "Real-time chat group management and message history"},
        {"name": "Complaints", "description": "User complaint submission and admin management"},
        {"name": "Activity Feed", "description": "Recent platform activity"},
        {"name": "AI Chatbot", "description": "Google Gemini-powered academic assistant"},
        {"name": "Admin", "description": "Platform analytics and user management"},
        {"name": "Health", "description": "Service health and monitoring"},
    ],
)

# ─── Exception Handlers ───────────────────────────────────────────────────────

from fastapi import HTTPException
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ─── Middleware ───────────────────────────────────────────────────────────────

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Rate limiting
from app.middleware.rate_limiter import RateLimiterMiddleware
app.add_middleware(RateLimiterMiddleware)


# Request logging middleware
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scholargrid")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} → {response.status_code} [{duration_ms}ms]"
    )
    return response


# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# ─── API Routers ──────────────────────────────────────────────────────────────

from app.api.v1 import auth, notes, leaderboard, chat, complaints, admin, ai_chatbot, activity

API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(notes.router, prefix=API_PREFIX)
app.include_router(leaderboard.router, prefix=API_PREFIX)
app.include_router(chat.router, prefix=API_PREFIX)
app.include_router(complaints.router, prefix=API_PREFIX)
app.include_router(admin.router, prefix=API_PREFIX)
app.include_router(ai_chatbot.router, prefix=API_PREFIX)
app.include_router(activity.router, prefix=API_PREFIX)


# ─── Socket.io ────────────────────────────────────────────────────────────────

from app.socket_server import socket_app
from starlette.routing import Mount

app.mount("/socket.io", socket_app)


# ─── Root & Health Endpoints ──────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """API root — basic info."""
    return {
        "service": "ScholarGrid Backend API",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check(response: Response):
    """Health check — verifies DB and Redis connectivity."""
    from app.core.database import check_db_connection
    from app.services.redis_service import check_redis_connection

    db_ok = check_db_connection()
    redis_ok = check_redis_connection()
    healthy = db_ok and redis_ok

    if not healthy:
        response.status_code = 503

    return {
        "status": "healthy" if healthy else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "redis": "connected" if redis_ok else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/metrics", tags=["Health"])
async def metrics():
    """Basic application metrics placeholder."""
    return {
        "status": "ok",
        "message": "Metrics endpoint — integrate Prometheus for full metrics.",
    }


# ─── Startup / Shutdown ───────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    """Connect Redis, initialize Cloudinary and Firebase on startup."""
    try:
        from app.services.redis_service import redis_client
        redis_client.connect()
        logger.info("Redis connected.")
    except Exception as e:
        logger.warning(f"Redis connection failed on startup: {e}")
    
    try:
        from app.services.cloudinary_storage import initialize_cloudinary
        initialize_cloudinary()
        logger.info("Cloudinary initialized.")
    except Exception as e:
        logger.warning(f"Cloudinary initialization failed on startup: {e}")
    
    try:
        from app.services.firebase_service import initialize_firebase
        initialize_firebase()
        logger.info("Firebase initialized.")
    except Exception as e:
        logger.warning(f"Firebase initialization failed on startup: {e}")


@app.on_event("shutdown")
async def shutdown():
    """Disconnect Redis on shutdown."""
    try:
        from app.services.redis_service import redis_client
        redis_client.disconnect()
        logger.info("Redis disconnected.")
    except Exception:
        pass
