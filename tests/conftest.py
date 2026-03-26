"""
Shared pytest fixtures for ScholarGrid Backend API tests.

Provides PostgreSQL test database sessions, sample data fixtures,
and FastAPI TestClient with auth bypass for integration tests.
"""

import uuid
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import os

from app.core.database import Base, get_db
from app.models.user import User
from app.models.note import Note
from app.models.chat import ChatGroup, ChatMembership
from app.models.complaint import Complaint


def _clear_rate_limit_state():
    try:
        from app.services.redis_service import invalidate_pattern

        invalidate_pattern("rate_limit:*")
    except Exception:
        pass


# ─── Database Fixtures ────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def test_engine():
    """Create a single session-scoped PostgreSQL test database engine."""
    # Use test database URL from environment - PostgreSQL only, no SQLite fallback
    test_db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://postgres:Aryan@localhost:5432/scholargrid_test"
    )
    
    engine = create_engine(test_db_url, pool_pre_ping=True)
    
    # Create all tables
    Base.metadata.create_all(engine)
    yield engine
    
    # Drop all tables after tests
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(test_engine):
    """
    Function-scoped DB session with full transaction isolation.

    SQLAlchemy 2.0-compatible approach: creates a connection, begins an
    outer transaction, creates a session joined to that connection, starts
    a nested savepoint. After the test, rolls back the outer transaction so
    all committed rows from the test are undone — keeping the session-scoped
    engine clean across all test files.
    """
    from sqlalchemy.orm import Session

    connection = test_engine.connect()
    trans = connection.begin()

    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    session.begin_nested()

    yield session

    session.close()
    trans.rollback()
    connection.close()


# ─── User Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def student_user(db_session):
    user = User(
        firebase_uid=f"student_{uuid.uuid4().hex}",
        email=f"student_{uuid.uuid4().hex[:8]}@test.com",
        name="Test Student",
        role="student",
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_user(db_session):
    user = User(
        firebase_uid=f"admin_{uuid.uuid4().hex}",
        email=f"admin_{uuid.uuid4().hex[:8]}@test.com",
        name="Test Admin",
        role="admin",
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def second_student(db_session):
    user = User(
        firebase_uid=f"student2_{uuid.uuid4().hex}",
        email=f"student2_{uuid.uuid4().hex[:8]}@test.com",
        name="Second Student",
        role="student",
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    return user


# ─── Note Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def approved_note(db_session, student_user):
    note = Note(
        title="Introduction to Calculus",
        description="Comprehensive calculus notes",
        subject="Mathematics",
        tags=["calculus", "derivatives"],
        file_url="https://storage.example.com/notes/uuid.pdf",
        file_name="calculus.pdf",
        file_size=1024 * 512,
        file_type="pdf",
        uploader_id=student_user.id,
        status="approved",
    )
    db_session.add(note)
    db_session.commit()
    return note


@pytest.fixture
def pending_note(db_session, student_user):
    note = Note(
        title="Pending Note",
        description="Awaiting approval",
        subject="Physics",
        tags=[],
        file_url="https://storage.example.com/notes/pending.pdf",
        file_name="pending.pdf",
        file_size=1024 * 256,
        file_type="pdf",
        uploader_id=student_user.id,
        status="pending",
    )
    db_session.add(note)
    db_session.commit()
    return note


# ─── Chat Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def chat_group(db_session, student_user):
    group = ChatGroup(
        name="Study Group",
        description="Physics study group",
        join_code=uuid.uuid4().hex[:8].upper(),  # Generate unique join code per test
        creator_id=student_user.id,
        member_count=1,
    )
    db_session.add(group)
    db_session.flush()
    membership = ChatMembership(group_id=group.id, user_id=student_user.id)
    db_session.add(membership)
    db_session.commit()
    return group


# ─── Complaint Fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def open_complaint(db_session, student_user):
    complaint = Complaint(
        title="App is slow",
        description="Pages take too long to load.",
        category="technical",
        status="open",
        priority="medium",
        submitter_id=student_user.id,
    )
    db_session.add(complaint)
    db_session.commit()
    return complaint


# ─── FastAPI TestClient ────────────────────────────────────────────────────────

@pytest.fixture
def client(db_session, student_user):
    """TestClient with DB override and Firebase auth bypassed for the student user."""
    from fastapi.testclient import TestClient
    from app.main import app

    def override_get_db():
        yield db_session

    async def override_get_current_user():
        return student_user

    app.dependency_overrides[get_db] = override_get_db

    from app.core.auth import get_current_user
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        _clear_rate_limit_state()
        yield c

    _clear_rate_limit_state()
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(db_session, admin_user):
    """TestClient authenticated as admin."""
    from fastapi.testclient import TestClient
    from app.main import app

    def override_get_db():
        yield db_session

    async def override_get_current_user():
        return admin_user

    app.dependency_overrides[get_db] = override_get_db

    from app.core.auth import get_current_user
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        _clear_rate_limit_state()
        yield c

    _clear_rate_limit_state()
    app.dependency_overrides.clear()
