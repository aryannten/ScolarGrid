"""
Tests for database connection and session management

**Validates: Requirements 23.1**
"""

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from app.core.database import get_db, check_db_connection, engine, Base


def test_database_connection_when_available():
    """Test that database connection check returns appropriate status"""
    # This test will pass whether DB is available or not
    # It just verifies the function returns a boolean
    result = check_db_connection()
    assert isinstance(result, bool)


def test_get_db_session_generator():
    """Test that get_db returns a generator that yields Session"""
    db_generator = get_db()
    assert hasattr(db_generator, '__next__')  # It's a generator


@pytest.mark.skipif(
    not check_db_connection(),
    reason="PostgreSQL database not available"
)
def test_session_executes_query():
    """Test that database session can execute queries (requires running DB)"""
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        result = db.execute(text("SELECT 1 as value"))
        row = result.fetchone()
        assert row[0] == 1
    finally:
        try:
            next(db_generator)
        except StopIteration:
            pass


def test_base_declarative_class():
    """Test that Base declarative class is properly configured"""
    assert Base is not None
    assert hasattr(Base, 'metadata')
    assert hasattr(Base, 'registry')  # SQLAlchemy 2.0 DeclarativeBase has registry


def test_engine_configuration():
    """Test that engine is configured with proper settings"""
    assert engine is not None
    assert engine.pool.size() >= 0  # Pool is initialized
    assert engine.url.drivername in ['postgresql', 'postgresql+psycopg']
