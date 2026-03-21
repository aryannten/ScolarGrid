"""
Unit tests for Download model

Tests the Download SQLAlchemy model including field validation,
constraints, defaults, and database operations.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.core.database import Base
from app.models import User, Note, Download


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    
    # Enable foreign key constraints in SQLite
    from sqlalchemy import event
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
def sample_user(db_session):
    """Create a sample user for testing"""
    user = User(
        firebase_uid="test_user_uid",
        email="user@example.com",
        name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_note(db_session, sample_user):
    """Create a sample note for testing"""
    note = Note(
        title="Test Note",
        description="Test Description",
        subject="Mathematics",
        file_url="https://example.com/note.pdf",
        file_name="note.pdf",
        file_size=1024,
        file_type="application/pdf",
        uploader_id=sample_user.id
    )
    db_session.add(note)
    db_session.commit()
    return note


def test_download_creation_with_required_fields(db_session, sample_user, sample_note):
    """Test creating a download record with required fields"""
    download = Download(
        note_id=sample_note.id,
        user_id=sample_user.id
    )
    db_session.add(download)
    db_session.commit()
    
    assert download.id is not None
    assert download.note_id == sample_note.id
    assert download.user_id == sample_user.id
    assert download.downloaded_at is not None
    assert isinstance(download.downloaded_at, datetime)


def test_download_multiple_downloads_allowed(db_session, sample_user, sample_note):
    """Test that a user can download the same note multiple times"""
    download1 = Download(
        note_id=sample_note.id,
        user_id=sample_user.id
    )
    db_session.add(download1)
    db_session.commit()
    
    # Create another download for the same note and user
    download2 = Download(
        note_id=sample_note.id,
        user_id=sample_user.id
    )
    db_session.add(download2)
    db_session.commit()
    
    # Both downloads should exist
    downloads = db_session.query(Download).filter_by(
        note_id=sample_note.id,
        user_id=sample_user.id
    ).all()
    assert len(downloads) == 2


def test_download_cascade_delete_on_note_deletion(db_session, sample_user, sample_note):
    """Test that downloads are deleted when note is deleted"""
    download = Download(
        note_id=sample_note.id,
        user_id=sample_user.id
    )
    db_session.add(download)
    db_session.commit()
    
    download_id = download.id
    
    # Delete the note
    db_session.delete(sample_note)
    db_session.commit()
    
    # Download should be deleted
    found_download = db_session.query(Download).filter_by(id=download_id).first()
    assert found_download is None


def test_download_cascade_delete_on_user_deletion(db_session, sample_user, sample_note):
    """Test that downloads are deleted when user is deleted"""
    download = Download(
        note_id=sample_note.id,
        user_id=sample_user.id
    )
    db_session.add(download)
    db_session.commit()
    
    download_id = download.id
    
    # Delete the user
    db_session.delete(sample_user)
    db_session.commit()
    
    # Download should be deleted
    found_download = db_session.query(Download).filter_by(id=download_id).first()
    assert found_download is None


def test_download_query_by_note(db_session, sample_user, sample_note):
    """Test querying downloads by note_id"""
    download = Download(
        note_id=sample_note.id,
        user_id=sample_user.id
    )
    db_session.add(download)
    db_session.commit()
    
    found_downloads = db_session.query(Download).filter_by(note_id=sample_note.id).all()
    assert len(found_downloads) == 1
    assert found_downloads[0].user_id == sample_user.id


def test_download_query_by_user(db_session, sample_user, sample_note):
    """Test querying downloads by user_id"""
    download = Download(
        note_id=sample_note.id,
        user_id=sample_user.id
    )
    db_session.add(download)
    db_session.commit()
    
    found_downloads = db_session.query(Download).filter_by(user_id=sample_user.id).all()
    assert len(found_downloads) == 1
    assert found_downloads[0].note_id == sample_note.id


def test_download_count_for_note(db_session, sample_note):
    """Test counting downloads for a specific note"""
    # Create multiple users and downloads
    for i in range(3):
        user = User(
            firebase_uid=f"user_{i}",
            email=f"user{i}@example.com",
            name=f"User {i}"
        )
        db_session.add(user)
        db_session.commit()
        
        download = Download(
            note_id=sample_note.id,
            user_id=user.id
        )
        db_session.add(download)
    
    db_session.commit()
    
    download_count = db_session.query(Download).filter_by(note_id=sample_note.id).count()
    assert download_count == 3


def test_download_repr(db_session, sample_user, sample_note):
    """Test the string representation of Download"""
    download = Download(
        note_id=sample_note.id,
        user_id=sample_user.id
    )
    db_session.add(download)
    db_session.commit()
    
    repr_str = repr(download)
    assert "Download" in repr_str
    assert str(sample_note.id) in repr_str
    assert str(sample_user.id) in repr_str
