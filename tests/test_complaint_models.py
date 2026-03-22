"""
Unit tests for complaint and activity models.

Tests the Complaint, ComplaintResponse, and Activity SQLAlchemy models
including defaults, constraints, foreign keys, and database operations.
"""

from datetime import datetime
import uuid

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Activity, Complaint, ComplaintResponse, User


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")

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
    """Create a sample student user for testing."""
    user = User(
        firebase_uid="student_uid",
        email="student@example.com",
        name="Student User",
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_admin(db_session):
    """Create a sample admin user for testing."""
    admin = User(
        firebase_uid="admin_uid",
        email="admin@example.com",
        name="Admin User",
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def sample_complaint(db_session, sample_user):
    """Create a sample complaint for response and cascade tests."""
    complaint = Complaint(
        title="Search results are broken",
        description="Search returns empty results for valid tags.",
        category="technical",
        submitter_id=sample_user.id,
    )
    db_session.add(complaint)
    db_session.commit()
    return complaint


def test_complaint_creation_with_required_fields(db_session, sample_user):
    """Test creating a complaint with only required fields."""
    complaint = Complaint(
        title="App crash",
        description="The app crashes when uploading a file.",
        category="technical",
        submitter_id=sample_user.id,
    )
    db_session.add(complaint)
    db_session.commit()

    assert complaint.id is not None
    assert complaint.status == "open"
    assert complaint.priority == "medium"
    assert complaint.screenshot_url is None
    assert complaint.resolution_note is None
    assert complaint.created_at is not None
    assert complaint.updated_at is not None


def test_complaint_creation_with_all_fields(db_session, sample_user):
    """Test creating a complaint with all fields specified."""
    complaint = Complaint(
        title="Feature request",
        description="Add dark mode to the dashboard.",
        category="feature_request",
        status="in_progress",
        priority="high",
        screenshot_url="https://example.com/complaints/screenshot.png",
        resolution_note="Queued for design review.",
        submitter_id=sample_user.id,
    )
    db_session.add(complaint)
    db_session.commit()

    assert complaint.category == "feature_request"
    assert complaint.status == "in_progress"
    assert complaint.priority == "high"
    assert complaint.screenshot_url is not None
    assert complaint.resolution_note == "Queued for design review."


def test_complaint_valid_category_values(db_session, sample_user):
    """Test that complaints accept all valid category values."""
    categories = ["technical", "content", "account", "feature_request", "other"]

    for category in categories:
        complaint = Complaint(
            title=f"{category} complaint",
            description=f"Description for {category}",
            category=category,
            submitter_id=sample_user.id,
        )
        db_session.add(complaint)

    db_session.commit()

    for category in categories:
        assert db_session.query(Complaint).filter_by(category=category).first() is not None


def test_complaint_valid_status_and_priority_values(db_session, sample_user):
    """Test that complaints accept all valid status and priority values."""
    complaint = Complaint(
        title="Status and priority test",
        description="Testing enum-like complaint fields.",
        category="other",
        status="resolved",
        priority="critical",
        resolution_note="Resolved during testing.",
        submitter_id=sample_user.id,
    )
    db_session.add(complaint)
    db_session.commit()

    assert complaint.status == "resolved"
    assert complaint.priority == "critical"


def test_complaint_invalid_category_fails(db_session, sample_user):
    """Test that invalid complaint categories violate the check constraint."""
    complaint = Complaint(
        title="Invalid category",
        description="This should fail.",
        category="billing",
        submitter_id=sample_user.id,
    )
    db_session.add(complaint)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_complaint_cascade_delete_on_submitter_deletion(db_session, sample_user):
    """Test that complaints are deleted when the submitter is deleted."""
    complaint = Complaint(
        title="Delete cascade",
        description="Testing submitter delete cascade.",
        category="account",
        submitter_id=sample_user.id,
    )
    db_session.add(complaint)
    db_session.commit()

    complaint_id = complaint.id
    db_session.delete(sample_user)
    db_session.commit()

    assert db_session.query(Complaint).filter_by(id=complaint_id).first() is None


def test_complaint_response_creation(db_session, sample_admin, sample_complaint):
    """Test creating an admin response for a complaint."""
    response = ComplaintResponse(
        complaint_id=sample_complaint.id,
        admin_id=sample_admin.id,
        text="We have identified the issue and deployed a fix.",
    )
    db_session.add(response)
    db_session.commit()

    assert response.id is not None
    assert response.complaint_id == sample_complaint.id
    assert response.admin_id == sample_admin.id
    assert response.created_at is not None


def test_complaint_response_cascade_delete_on_complaint_deletion(
    db_session, sample_admin, sample_complaint
):
    """Test that complaint responses are deleted when the complaint is deleted."""
    response = ComplaintResponse(
        complaint_id=sample_complaint.id,
        admin_id=sample_admin.id,
        text="Investigating.",
    )
    db_session.add(response)
    db_session.commit()

    response_id = response.id
    db_session.delete(sample_complaint)
    db_session.commit()

    assert db_session.query(ComplaintResponse).filter_by(id=response_id).first() is None


def test_complaint_response_cascade_delete_on_admin_deletion(
    db_session, sample_admin, sample_complaint
):
    """Test that complaint responses are deleted when the admin is deleted."""
    response = ComplaintResponse(
        complaint_id=sample_complaint.id,
        admin_id=sample_admin.id,
        text="Resolved and closing.",
    )
    db_session.add(response)
    db_session.commit()

    response_id = response.id
    db_session.delete(sample_admin)
    db_session.commit()

    assert db_session.query(ComplaintResponse).filter_by(id=response_id).first() is None


def test_activity_creation_with_metadata(db_session, sample_user):
    """Test creating an activity event with metadata."""
    entity_id = uuid.uuid4()
    activity = Activity(
        type="note_upload",
        user_id=sample_user.id,
        entity_id=entity_id,
        metadata_={"title": "Linear Algebra Notes", "subject": "Mathematics"},
    )
    db_session.add(activity)
    db_session.commit()

    assert activity.id is not None
    assert activity.type == "note_upload"
    assert activity.user_id == sample_user.id
    assert activity.entity_id == entity_id
    assert activity.metadata_ == {"title": "Linear Algebra Notes", "subject": "Mathematics"}
    assert activity.created_at is not None
    assert isinstance(activity.created_at, datetime)


def test_activity_valid_type_values(db_session, sample_user):
    """Test that activities accept all valid event types."""
    valid_types = ["note_upload", "user_registration", "high_rating"]

    for activity_type in valid_types:
        activity = Activity(
            type=activity_type,
            user_id=sample_user.id,
        )
        db_session.add(activity)

    db_session.commit()

    for activity_type in valid_types:
        assert db_session.query(Activity).filter_by(type=activity_type).first() is not None


def test_activity_invalid_type_fails(db_session, sample_user):
    """Test that invalid activity types violate the check constraint."""
    activity = Activity(
        type="login",
        user_id=sample_user.id,
    )
    db_session.add(activity)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_activity_cascade_delete_on_user_deletion(db_session, sample_user):
    """Test that activities are deleted when the related user is deleted."""
    activity = Activity(
        type="high_rating",
        user_id=sample_user.id,
        metadata_={"rating": 5},
    )
    db_session.add(activity)
    db_session.commit()

    activity_id = activity.id
    db_session.delete(sample_user)
    db_session.commit()

    assert db_session.query(Activity).filter_by(id=activity_id).first() is None


def test_complaint_and_activity_repr(db_session, sample_user, sample_admin, sample_complaint):
    """Test repr output for complaint-related and activity models."""
    response = ComplaintResponse(
        complaint_id=sample_complaint.id,
        admin_id=sample_admin.id,
        text="Response for repr testing.",
    )
    activity = Activity(
        type="user_registration",
        user_id=sample_user.id,
    )
    db_session.add(response)
    db_session.add(activity)
    db_session.commit()

    assert "Complaint" in repr(sample_complaint)
    assert "ComplaintResponse" in repr(response)
    assert "Activity" in repr(activity)
