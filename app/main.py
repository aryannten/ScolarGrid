"""
ScholarGrid Backend API - Main Application Entry Point

This module initializes the FastAPI application with CORS middleware
and serves as the entry point for the ScholarGrid backend API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

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
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "database": "not_configured",
        "redis": "not_configured"
    }
