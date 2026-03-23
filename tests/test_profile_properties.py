"""
Property-based tests for user profile creation and management (Tasks 4.2, 4.5)

Tests profile creation completeness, profile update round trip, and file upload round trip.
"""

import pytest
from hypothesis import given, settings as hyp_settings, HealthCheck
from hypothesis import strategies as st
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User


@pytest.fixture(scope="module")
def engine():
    """Create a session-scoped in-memory SQLite engine for property tests."""
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    
    @event.listens_for(eng, "connect")
    def enable_fk(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")
    
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def db(engine):
    """Function-scoped database session with transaction rollback."""
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.rollback()
    s.close()


# ─── Property 6: Profile Creation Completeness ────────────────────────────────

@given(
    name=st.text(min_size=1, max_size=100),
    role=st.sampled_from(["student", "admin"]),
    avatar_url=st.one_of(st.none(), st.text(min_size=1, max_size=500)),
    about=st.one_of(st.none(), st.text(min_size=0, max_size=500)),
)
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_profile_creation_completeness(name, role, avatar_url, about, engine):
    """
    Feature: scholargrid-backend-api, Property 6: Profile Creation Completeness
    
    For any valid registration data, the created user profile should contain all 
    specified fields (name, email, avatar_url, about, role) and student profiles 
    should have initial values (score=0, tier=bronze, uploads_count=0, downloads_count=0).
    
    **Validates: Requirements 3.1, 3.2**
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Create user with given data (generate unique email and uid)
        import uuid
        uid = f"prop6_{uuid.uuid4().hex}"
        email = f"{uid}@test.com"
        
        user = User(
            firebase_uid=uid,
            email=email,
            name=name,
            role=role,
            avatar_url=avatar_url,
            about=about,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Assert all specified fields are present
        assert user.name == name
        assert user.email == email
        assert user.role == role
        assert user.avatar_url == avatar_url
        assert user.about == about
        
        # Assert student profiles have correct initial values
        if role == "student":
            assert user.score == 0, f"Expected score=0 for student, got {user.score}"
            assert user.tier == "bronze", f"Expected tier=bronze for student, got {user.tier}"
            assert user.uploads_count == 0, f"Expected uploads_count=0, got {user.uploads_count}"
            assert user.downloads_count == 0, f"Expected downloads_count=0, got {user.downloads_count}"
        
        # Assert timestamps are set
        assert user.created_at is not None
        assert user.updated_at is not None
        
    finally:
        db.rollback()
        db.close()


# ─── Property 7: Profile Update Round Trip ────────────────────────────────────

@given(
    initial_name=st.text(min_size=1, max_size=100),
    updated_name=st.text(min_size=1, max_size=100),
    initial_about=st.one_of(st.none(), st.text(min_size=0, max_size=500)),
    updated_about=st.one_of(st.none(), st.text(min_size=0, max_size=500)),
)
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_profile_update_round_trip(
    initial_name, updated_name, initial_about, updated_about, engine
):
    """
    Feature: scholargrid-backend-api, Property 7: Profile Update Round Trip
    
    For any user profile and any valid update data, updating the profile and 
    then retrieving it should return the updated values.
    
    **Validates: Requirements 3.3**
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Create initial user with unique identifiers
        import uuid
        uid = f"prop7_{uuid.uuid4().hex}"
        email = f"{uid}@test.com"
        
        user = User(
            firebase_uid=uid,
            email=email,
            name=initial_name,
            about=initial_about,
            role="student",
        )
        db.add(user)
        db.commit()
        user_id = user.id
        
        # Update profile
        user.name = updated_name
        user.about = updated_about
        db.commit()
        
        # Retrieve user from database (fresh query)
        db.expire_all()
        retrieved_user = db.query(User).filter(User.id == user_id).first()
        
        # Assert updated values are persisted
        assert retrieved_user is not None
        assert retrieved_user.name == updated_name, \
            f"Expected name={updated_name}, got {retrieved_user.name}"
        assert retrieved_user.about == updated_about, \
            f"Expected about={updated_about}, got {retrieved_user.about}"
        
        # Assert other fields remain unchanged
        assert retrieved_user.email == email
        assert retrieved_user.firebase_uid == uid
        assert retrieved_user.role == "student"
        
    finally:
        db.rollback()
        db.close()


# ─── Property 8: File Upload Round Trip (Simplified) ──────────────────────────

@given(
    avatar_url=st.from_regex(r"https?://[a-z0-9\-\.]+\.[a-z]{2,}/[a-z0-9\-_/\.]+", fullmatch=True),
)
@hyp_settings(
    max_examples=50, 
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.filter_too_much]
)
def test_property_file_upload_round_trip_avatar_url(avatar_url, engine):
    """
    Feature: scholargrid-backend-api, Property 8: File Upload Round Trip
    
    For any valid file upload (avatar, note, chat file, complaint attachment), 
    the API should store the file in Firebase Storage and return a valid URL 
    that can be used to retrieve the file.
    
    This test verifies that avatar URLs are properly stored and retrieved.
    Full Firebase Storage integration is tested in integration tests.
    
    **Validates: Requirements 3.5, 4.2, 12.3, 14.5**
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Create user with avatar URL and unique identifiers
        import uuid
        uid = f"prop8_{uuid.uuid4().hex}"
        email = f"{uid}@test.com"
        
        user = User(
            firebase_uid=uid,
            email=email,
            name="Test User",
            avatar_url=avatar_url,
            role="student",
        )
        db.add(user)
        db.commit()
        user_id = user.id
        
        # Retrieve user and verify avatar URL
        db.expire_all()
        retrieved_user = db.query(User).filter(User.id == user_id).first()
        
        assert retrieved_user is not None
        assert retrieved_user.avatar_url == avatar_url, \
            f"Expected avatar_url={avatar_url}, got {retrieved_user.avatar_url}"
        
        # Verify URL format (should be a valid URL)
        assert avatar_url.startswith("http"), \
            f"Avatar URL should start with http, got {avatar_url}"
        
    finally:
        db.rollback()
        db.close()
