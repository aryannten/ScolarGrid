"""
ScholarGrid Backend API - Main Application Entry Point

This module initializes the FastAPI application with CORS middleware
and serves as the entry point for the ScholarGrid backend API.
"""

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Academic note-sharing platform with real-time chat and AI assistance",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
# Loads allowed origins from environment configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "ScholarGrid Backend API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check(response: Response):
    """Health check endpoint for monitoring"""
    from app.core.database import check_db_connection
    from app.services.redis_service import check_redis_connection
    
    db_status = "connected" if check_db_connection() else "disconnected"
    redis_status = "connected" if check_redis_connection() else "disconnected"
    
    # Return 503 if any critical service is down
    is_healthy = db_status == "connected" and redis_status == "connected"
    
    if not is_healthy:
        response.status_code = 503
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": db_status,
        "redis": redis_status
    }
