"""
Unit tests for Note model

Tests the Note SQLAlchemy model including field validation,
constraints, defaults, foreign key relationships, and database operations.

Note: SQLite doesn't support ARRAY types, so tags are stored as JSON strings in tests.
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
import uuid
import json

from app.core.database import Base
from app.models import User, Note


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    
    # SQLite doesn't support ARRAY types, so we need to handle tags as JSON
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user for foreign key relationships"""
    user = User(
        firebase_uid="test_uploader_uid",
        email="uploader@example.com",
        name="Test Uploader"
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_note_creation_with_required_fields(db_session, test_user):
    """Test creating a note with only required fields"""
    note = Note(
        title="Introduction to Python",
        description="Comprehensive guide to Python programming",
        subject="Computer Science",
        file_url="https://storage.example.com/notes/abc123.pdf",
        file_name="python_intro.pdf",
        file_size=1024000,
        file_type="application/pdf",
        uploader_id=test_user.id
    )
    db_session.add(note)
    db_session.commit()
    
    assert note.id is not None
    assert note.title == "Introduction to Python"
    assert note.description == "Comprehensive guide to Python programming"
    assert note.subject == "Computer Science"
    assert note.file_url == "https://storage.example.com/notes/abc123.pdf"
    assert note.file_name == "python_intro.pdf"
    assert note.file_size == 1024000
    assert note.file_type == "application/pdf"
    assert note.uploader_id == test_user.id
    assert note.status == "pending"  # Default value
    assert note.download_count == 0  # Default value
    assert note.rating_count == 0  # Default value
    assert note.average_rating is None  # Default value
    assert note.rejection_reason is None
    assert note.upload_date is not None
    assert note.updated_at is not None


def test_note_creation_with_all_fields(db_session, test_user):
    """Test creating a note with all fields specified"""
    note = Note(
        title="Advanced Calculus",
        description="Advanced topics in calculus",
        subject="Mathematics",
        tags=["calculus", "derivatives", "integrals"],
        file_url="https://storage.example.com/notes/xyz789.pdf",
        file_name="calculus_advanced.pdf",
        file_size=2048000,
        file_type="application/pdf",
        uploader_id=test_user.id,
        status="approved",
        download_count=50,
        average_rating=Decimal("4.50"),
        rating_count=10
    )
    db_session.add(note)
    db_session.commit()
    
    assert note.tags == ["calculus", "derivatives", "integrals"]
    assert note.status == "approved"
    assert note.download_count == 50
    assert note.average_rating == Decimal("4.50")
    assert note.rating_count == 10


def test_note_foreign_key_to_user(db_session, test_user):
    """Test that note has valid foreign key relationship to user"""
    note = Note(
        title="Test Note",
        description="Test description",
        subject="Test Subject",
        file_url="https://example.com/file.pdf",
        file_name="test.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id
    )
    db_session.add(note)
    db_session.commit()
    
    # Query note and verify uploader_id matches
    found_note = db_session.query(Note).filter_by(id=note.id).first()
    assert found_note.uploader_id == test_user.id


def test_note_status_values(db_session, test_user):
    """Test that status accepts valid values"""
    statuses = ["pending", "approved", "rejected"]
    
    for status in statuses:
        note = Note(
            title=f"{status.capitalize()} Note",
            description=f"Note with {status} status",
            subject="Test",
            file_url=f"https://example.com/{status}.pdf",
            file_name=f"{status}.pdf",
            file_size=1000,
            file_type="application/pdf",
            uploader_id=test_user.id,
            status=status
        )
        db_session.add(note)
    
    db_session.commit()
    
    for status in statuses:
        found_note = db_session.query(Note).filter_by(status=status).first()
        assert found_note is not None
        assert found_note.status == status


def test_note_with_rejection_reason(db_session, test_user):
    """Test that rejected notes can have rejection reasons"""
    note = Note(
        title="Rejected Note",
        description="This note was rejected",
        subject="Test",
        file_url="https://example.com/rejected.pdf",
        file_name="rejected.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id,
        status="rejected",
        rejection_reason="Content does not meet quality standards"
    )
    db_session.add(note)
    db_session.commit()
    
    assert note.status == "rejected"
    assert note.rejection_reason == "Content does not meet quality standards"


def test_note_with_tags_array(db_session, test_user):
    """Test that tags can be stored as an array"""
    note = Note(
        title="Tagged Note",
        description="Note with multiple tags",
        subject="Computer Science",
        tags=["python", "programming", "tutorial", "beginner"],
        file_url="https://example.com/tagged.pdf",
        file_name="tagged.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id
    )
    db_session.add(note)
    db_session.commit()
    
    assert len(note.tags) == 4
    assert "python" in note.tags
    assert "programming" in note.tags


def test_note_without_tags(db_session, test_user):
    """Test that tags field can be None"""
    note = Note(
        title="Untagged Note",
        description="Note without tags",
        subject="Test",
        file_url="https://example.com/untagged.pdf",
        file_name="untagged.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id,
        tags=None
    )
    db_session.add(note)
    db_session.commit()
    
    assert note.tags is None


def test_note_query_by_subject(db_session, test_user):
    """Test querying notes by subject"""
    note1 = Note(
        title="Math Note 1",
        description="First math note",
        subject="Mathematics",
        file_url="https://example.com/math1.pdf",
        file_name="math1.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id
    )
    note2 = Note(
        title="Math Note 2",
        description="Second math note",
        subject="Mathematics",
        file_url="https://example.com/math2.pdf",
        file_name="math2.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id
    )
    db_session.add(note1)
    db_session.add(note2)
    db_session.commit()
    
    math_notes = db_session.query(Note).filter_by(subject="Mathematics").all()
    assert len(math_notes) == 2


def test_note_query_by_status(db_session, test_user):
    """Test querying notes by status"""
    approved_note = Note(
        title="Approved Note",
        description="This is approved",
        subject="Test",
        file_url="https://example.com/approved.pdf",
        file_name="approved.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id,
        status="approved"
    )
    pending_note = Note(
        title="Pending Note",
        description="This is pending",
        subject="Test",
        file_url="https://example.com/pending.pdf",
        file_name="pending.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id,
        status="pending"
    )
    db_session.add(approved_note)
    db_session.add(pending_note)
    db_session.commit()
    
    approved_notes = db_session.query(Note).filter_by(status="approved").all()
    assert len(approved_notes) == 1
    assert approved_notes[0].title == "Approved Note"


def test_note_average_rating_precision(db_session, test_user):
    """Test that average_rating stores decimal values with correct precision"""
    note = Note(
        title="Rated Note",
        description="Note with rating",
        subject="Test",
        file_url="https://example.com/rated.pdf",
        file_name="rated.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id,
        average_rating=Decimal("3.75")
    )
    db_session.add(note)
    db_session.commit()
    
    found_note = db_session.query(Note).filter_by(id=note.id).first()
    assert found_note.average_rating == Decimal("3.75")


def test_note_file_size_large_value(db_session, test_user):
    """Test that file_size can store large values (BigInteger)"""
    large_size = 50 * 1024 * 1024  # 50 MB in bytes
    note = Note(
        title="Large File",
        description="Note with large file",
        subject="Test",
        file_url="https://example.com/large.pdf",
        file_name="large.pdf",
        file_size=large_size,
        file_type="application/pdf",
        uploader_id=test_user.id
    )
    db_session.add(note)
    db_session.commit()
    
    assert note.file_size == large_size


def test_note_repr(db_session, test_user):
    """Test the string representation of Note"""
    note = Note(
        title="Repr Test Note",
        description="Testing repr",
        subject="Test",
        file_url="https://example.com/repr.pdf",
        file_name="repr.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id,
        status="approved"
    )
    db_session.add(note)
    db_session.commit()
    
    repr_str = repr(note)
    assert "Note" in repr_str
    assert "Repr Test Note" in repr_str
    assert "approved" in repr_str
    assert str(test_user.id) in repr_str


def test_note_timestamps_auto_set(db_session, test_user):
    """Test that timestamps are automatically set"""
    note = Note(
        title="Timestamp Test",
        description="Testing timestamps",
        subject="Test",
        file_url="https://example.com/timestamp.pdf",
        file_name="timestamp.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id
    )
    db_session.add(note)
    db_session.commit()
    
    assert note.upload_date is not None
    assert note.updated_at is not None
    assert note.status_updated_at is None  # Should be None initially


def test_note_query_by_uploader(db_session, test_user):
    """Test querying notes by uploader_id"""
    note1 = Note(
        title="User Note 1",
        description="First note by user",
        subject="Test",
        file_url="https://example.com/user1.pdf",
        file_name="user1.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id
    )
    note2 = Note(
        title="User Note 2",
        description="Second note by user",
        subject="Test",
        file_url="https://example.com/user2.pdf",
        file_name="user2.pdf",
        file_size=1000,
        file_type="application/pdf",
        uploader_id=test_user.id
    )
    db_session.add(note1)
    db_session.add(note2)
    db_session.commit()
    
    user_notes = db_session.query(Note).filter_by(uploader_id=test_user.id).all()
    assert len(user_notes) == 2
