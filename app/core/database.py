"""
Database connection and session management for ScholarGrid Backend API

This module provides SQLAlchemy engine configuration, session management,
and the declarative base class for ORM models.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from typing import Generator

from app.core.config import settings

engine_kwargs = {
    "pool_pre_ping": True,
    "echo": False,
}

if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update(
        {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 3600,
            "connect_args": {"connect_timeout": 3},
        }
    )

# Create SQLAlchemy engine with connection pooling
# Pool configuration is optimized for PostgreSQL in production and
# relaxed for SQLite during tests.
engine = create_engine(settings.database_url, **engine_kwargs)

# Create SessionLocal class for database sessions
# Each instance of SessionLocal will be a database session
SessionLocal = sessionmaker(
    autocommit=False,  # Explicit transaction control
    autoflush=False,  # Manual flush control for better performance
    bind=engine
)


# Create declarative base class for ORM models using SQLAlchemy 2.0 style
# All database models will inherit from this base
class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI routes.
    
    Provides a SQLAlchemy session that automatically handles:
    - Session creation
    - Transaction management
    - Proper cleanup and connection release
    
    Usage in FastAPI routes:
        @app.get("/example")
        def example_route(db: Session = Depends(get_db)):
            # Use db session here
            pass
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    
    Creates all tables defined by SQLAlchemy models that inherit from Base.
    This function should be called during application startup.
    
    Note: In production, use Alembic migrations instead of this function
    to manage schema changes with proper version control.
    """
    Base.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Used by health check endpoints to verify database availability.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        # Attempt to create a connection and execute a simple query
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
