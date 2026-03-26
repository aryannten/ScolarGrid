"""
ScholarGrid Backend API

Main application package with organized structure:
- core: Configuration, database, and dependencies
- models: SQLAlchemy ORM models
- schemas: Pydantic request/response models
- services: Business logic and external integrations
- api: API route handlers
- utils: Utility functions
- middleware: Custom middleware components
"""

# Export key components for easy imports
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal, init_db, check_db_connection, get_db

__all__ = [
    "settings",
    "Base",
    "engine",
    "SessionLocal",
    "init_db",
    "check_db_connection",
    "get_db",
]
