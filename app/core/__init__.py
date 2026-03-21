"""
Core module for ScholarGrid Backend API

Contains configuration, database, and dependency injection utilities.
"""

from app.core.config import settings, validate_configuration
from app.core.database import (
    Base,
    engine,
    SessionLocal,
    get_db,
    init_db,
    check_db_connection
)

__all__ = [
    "settings",
    "validate_configuration",
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "check_db_connection",
]
