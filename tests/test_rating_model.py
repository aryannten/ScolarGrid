"""
Unit tests for Rating model

Tests the Rating SQLAlchemy model including field validation,
constraints, defaults, and database operations.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.core.database import Base
from app.models import User, Note, Rating


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


def test_rating_creation_with_required_fields(db_session, sample_user, sample_note):
    """Test creating a rating with required fields"""
    rating = Rating(
        note_id=sample_note.id,
        user_id=sample_user.id,
        rating=5
    )
    db_session.add(rating)
    db_session.commit()
    
    assert rating.id is not None
    assert rating.note_id == sample_note.id
    assert rating.user_id == sample_user.id
    assert rating.rating == 5
    assert rating.created_at is not None
    assert rating.updated_at is not None


def test_rating_valid_values(db_session, sample_user, sample_note):
    """Test that rating accepts values 1-5"""
    for value in [1, 2, 3, 4, 5]:
        # Create a new user for each rating to avoid unique constraint
        user = User(
            firebase_uid=f"user_{value}",
            email=f"user{value}@example.com",
            name=f"User {value}"
        )
        db_session.add(user)
        db_session.commit()
        
        rating = Rating(
            note_id=sample_note.id,
            user_id=user.id,
            rating=value
        )
        db_session.add(rating)
        db_session.commit()
        
        assert rating.rating == value


def test_rating_unique_constraint(db_session, sample_user, sample_note):
    """Test that a user can only rate a note once"""
    rating1 = Rating(
        note_id=sample_note.id,
        user_id=sample_user.id,
        rating=4
    )
    db_session.add(rating1)
    db_session.commit()
    
    # Try to create another rating for the same note and user
    rating2 = Rating(
        note_id=sample_note.id,
        user_id=sample_user.id,
        rating=5
    )
    db_session.add(rating2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_rating_cascade_delete_on_note_deletion(db_session, sample_user, sample_note):
    """Test that ratings are deleted when note is deleted"""
    rating = Rating(
        note_id=sample_note.id,
        user_id=sample_user.id,
        rating=5
    )
    db_session.add(rating)
    db_session.commit()
    
    rating_id = rating.id
    
    # Delete the note
    db_session.delete(sample_note)
    db_session.commit()
    
    # Rating should be deleted
    found_rating = db_session.query(Rating).filter_by(id=rating_id).first()
    assert found_rating is None


def test_rating_cascade_delete_on_user_deletion(db_session, sample_user, sample_note):
    """Test that ratings are deleted when user is deleted"""
    rating = Rating(
        note_id=sample_note.id,
        user_id=sample_user.id,
        rating=4
    )
    db_session.add(rating)
    db_session.commit()
    
    rating_id = rating.id
    
    # Delete the user
    db_session.delete(sample_user)
    db_session.commit()
    
    # Rating should be deleted
    found_rating = db_session.query(Rating).filter_by(id=rating_id).first()
    assert found_rating is None


def test_rating_query_by_note(db_session, sample_user, sample_note):
    """Test querying ratings by note_id"""
    rating = Rating(
        note_id=sample_note.id,
        user_id=sample_user.id,
        rating=3
    )
    db_session.add(rating)
    db_session.commit()
    
    found_ratings = db_session.query(Rating).filter_by(note_id=sample_note.id).all()
    assert len(found_ratings) == 1
    assert found_ratings[0].rating == 3


def test_rating_query_by_user(db_session, sample_user, sample_note):
    """Test querying ratings by user_id"""
    rating = Rating(
        note_id=sample_note.id,
        user_id=sample_user.id,
        rating=2
    )
    db_session.add(rating)
    db_session.commit()
    
    found_ratings = db_session.query(Rating).filter_by(user_id=sample_user.id).all()
    assert len(found_ratings) == 1
    assert found_ratings[0].rating == 2


def test_rating_repr(db_session, sample_user, sample_note):
    """Test the string representation of Rating"""
    rating = Rating(
        note_id=sample_note.id,
        user_id=sample_user.id,
        rating=5
    )
    db_session.add(rating)
    db_session.commit()
    
    repr_str = repr(rating)
    assert "Rating" in repr_str
    assert str(sample_note.id) in repr_str
    assert str(sample_user.id) in repr_str
    assert "5" in repr_str
