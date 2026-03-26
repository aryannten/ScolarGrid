"""
FastAPI dependency injection functions

This module contains dependency functions for FastAPI routes including
database session management, authentication, and authorization.
"""

from typing import Generator
from sqlalchemy.orm import Session

from app.core.database import SessionLocal


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
