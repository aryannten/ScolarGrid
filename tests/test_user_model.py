"""
Unit tests for User model

Tests the User SQLAlchemy model including field validation,
constraints, defaults, and database operations.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import uuid

from app.core.database import Base
from app.models import User


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_user_creation_with_required_fields(db_session):
    """Test creating a user with only required fields"""
    user = User(
        firebase_uid="test_firebase_uid_123",
        email="test@example.com",
        name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.firebase_uid == "test_firebase_uid_123"
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.role == "student"  # Default value
    assert user.status == "active"  # Default value
    assert user.score == 0  # Default value
    assert user.tier == "bronze"  # Default value
    assert user.uploads_count == 0  # Default value
    assert user.downloads_count == 0  # Default value
    assert user.created_at is not None
    assert user.updated_at is not None


def test_user_creation_with_all_fields(db_session):
    """Test creating a user with all fields specified"""
    user = User(
        firebase_uid="admin_firebase_uid_456",
        email="admin@example.com",
        name="Admin User",
        role="admin",
        avatar_url="https://example.com/avatar.jpg",
        about="I am an admin",
        status="active",
        score=1500,
        tier="silver",
        uploads_count=10,
        downloads_count=5
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.role == "admin"
    assert user.avatar_url == "https://example.com/avatar.jpg"
    assert user.about == "I am an admin"
    assert user.score == 1500
    assert user.tier == "silver"
    assert user.uploads_count == 10
    assert user.downloads_count == 5


def test_user_unique_email_constraint(db_session):
    """Test that email must be unique"""
    user1 = User(
        firebase_uid="uid1",
        email="duplicate@example.com",
        name="User 1"
    )
    db_session.add(user1)
    db_session.commit()
    
    user2 = User(
        firebase_uid="uid2",
        email="duplicate@example.com",  # Duplicate email
        name="User 2"
    )
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_unique_firebase_uid_constraint(db_session):
    """Test that firebase_uid must be unique"""
    user1 = User(
        firebase_uid="duplicate_uid",
        email="user1@example.com",
        name="User 1"
    )
    db_session.add(user1)
    db_session.commit()
    
    user2 = User(
        firebase_uid="duplicate_uid",  # Duplicate firebase_uid
        email="user2@example.com",
        name="User 2"
    )
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_optional_fields_can_be_none(db_session):
    """Test that optional fields (avatar_url, about) can be None"""
    user = User(
        firebase_uid="test_uid",
        email="test@example.com",
        name="Test User",
        avatar_url=None,
        about=None
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.avatar_url is None
    assert user.about is None


def test_user_query_by_email(db_session):
    """Test querying user by email"""
    user = User(
        firebase_uid="query_test_uid",
        email="query@example.com",
        name="Query Test"
    )
    db_session.add(user)
    db_session.commit()
    
    found_user = db_session.query(User).filter_by(email="query@example.com").first()
    assert found_user is not None
    assert found_user.name == "Query Test"


def test_user_query_by_firebase_uid(db_session):
    """Test querying user by firebase_uid"""
    user = User(
        firebase_uid="firebase_query_uid",
        email="firebase@example.com",
        name="Firebase Test"
    )
    db_session.add(user)
    db_session.commit()
    
    found_user = db_session.query(User).filter_by(firebase_uid="firebase_query_uid").first()
    assert found_user is not None
    assert found_user.email == "firebase@example.com"


def test_user_tier_values(db_session):
    """Test that tier accepts valid values"""
    tiers = ["bronze", "silver", "gold", "elite"]
    
    for tier in tiers:
        user = User(
            firebase_uid=f"tier_test_{tier}",
            email=f"{tier}@example.com",
            name=f"{tier.capitalize()} User",
            tier=tier
        )
        db_session.add(user)
    
    db_session.commit()
    
    for tier in tiers:
        found_user = db_session.query(User).filter_by(tier=tier).first()
        assert found_user is not None


def test_user_role_values(db_session):
    """Test that role accepts valid values"""
    student = User(
        firebase_uid="student_uid",
        email="student@example.com",
        name="Student User",
        role="student"
    )
    admin = User(
        firebase_uid="admin_uid",
        email="admin@example.com",
        name="Admin User",
        role="admin"
    )
    
    db_session.add(student)
    db_session.add(admin)
    db_session.commit()
    
    assert student.role == "student"
    assert admin.role == "admin"


def test_user_status_values(db_session):
    """Test that status accepts valid values"""
    active_user = User(
        firebase_uid="active_uid",
        email="active@example.com",
        name="Active User",
        status="active"
    )
    suspended_user = User(
        firebase_uid="suspended_uid",
        email="suspended@example.com",
        name="Suspended User",
        status="suspended"
    )
    
    db_session.add(active_user)
    db_session.add(suspended_user)
    db_session.commit()
    
    assert active_user.status == "active"
    assert suspended_user.status == "suspended"


def test_user_repr(db_session):
    """Test the string representation of User"""
    user = User(
        firebase_uid="repr_test_uid",
        email="repr@example.com",
        name="Repr Test",
        role="student",
        tier="gold"
    )
    db_session.add(user)
    db_session.commit()
    
    repr_str = repr(user)
    assert "User" in repr_str
    assert "repr@example.com" in repr_str
    assert "student" in repr_str
    assert "gold" in repr_str
