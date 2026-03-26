"""
Property-based tests for complaint and activity models.

**Validates: Requirements 14.2, 14.3, 15.3, 17.1, 23.4, 23.5**

Tests universal properties that should hold for all valid inputs:
- Property 37: Complaint Category Validation
- Property 38: Complaint Default Values
- Property 39: Complaint Status Validation
- Property 40: Complaint Priority Validation
- Property 45: Activity Feed Event Types
- Property 57: Foreign Key Cascade Behavior
"""

from datetime import datetime
import uuid

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Activity, Complaint, ComplaintResponse, User


# Hypothesis strategies for domain objects
valid_complaint_categories = st.sampled_from([
    "technical", "content", "account", "feature_request", "other"
])

invalid_complaint_categories = st.text(min_size=1, max_size=50).filter(
    lambda x: x not in ["technical", "content", "account", "feature_request", "other"]
)

valid_complaint_statuses = st.sampled_from([
    "open", "in_progress", "resolved", "closed"
])

invalid_complaint_statuses = st.text(min_size=1, max_size=20).filter(
    lambda x: x not in ["open", "in_progress", "resolved", "closed"]
)

valid_complaint_priorities = st.sampled_from([
    "low", "medium", "high", "critical"
])

invalid_complaint_priorities = st.text(min_size=1, max_size=20).filter(
    lambda x: x not in ["low", "medium", "high", "critical"]
)

valid_activity_types = st.sampled_from([
    "note_upload", "user_registration", "high_rating"
])

invalid_activity_types = st.text(min_size=1, max_size=50).filter(
    lambda x: x not in ["note_upload", "user_registration", "high_rating"]
)

complaint_titles = st.text(min_size=1, max_size=200)
complaint_descriptions = st.text(min_size=1, max_size=2000)


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
    """Create a sample user for testing."""
    user = User(
        firebase_uid="test_uid",
        email="test@example.com",
        name="Test User",
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


class TestComplaintCategoryValidation:
    """
    **Property 37: Complaint Category Validation**
    **Validates: Requirement 14.1**
    
    For any complaint submission, category values in the set 
    {technical, content, account, feature_request, other} should succeed.
    Any other category value should be rejected with status code 422.
    """
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        title=complaint_titles,
        description=complaint_descriptions,
        category=valid_complaint_categories
    )
    def test_valid_complaint_categories_succeed(
        self, db_session, sample_user, title, description, category
    ):
        """Test that all valid complaint categories are accepted."""
        complaint = Complaint(
            title=title,
            description=description,
            category=category,
            submitter_id=sample_user.id,
        )
        db_session.add(complaint)
        db_session.commit()
        
        # Verify complaint was created successfully
        assert complaint.id is not None
        assert complaint.category == category
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        title=complaint_titles,
        description=complaint_descriptions,
        category=invalid_complaint_categories
    )
    def test_invalid_complaint_categories_fail(
        self, db_session, sample_user, title, description, category
    ):
        """Test that invalid complaint categories are rejected."""
        complaint = Complaint(
            title=title,
            description=description,
            category=category,
            submitter_id=sample_user.id,
        )
        db_session.add(complaint)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()


class TestComplaintDefaultValues:
    """
    **Property 38: Complaint Default Values**
    **Validates: Requirement 14.3**
    
    For any newly created complaint, status should be 'open' and 
    priority should be 'medium' unless explicitly specified otherwise.
    """
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        title=complaint_titles,
        description=complaint_descriptions,
        category=valid_complaint_categories
    )
    def test_complaint_default_status_and_priority(
        self, db_session, sample_user, title, description, category
    ):
        """Test that complaints have correct default values."""
        complaint = Complaint(
            title=title,
            description=description,
            category=category,
            submitter_id=sample_user.id,
        )
        db_session.add(complaint)
        db_session.commit()
        
        # Verify default values
        assert complaint.status == "open"
        assert complaint.priority == "medium"
        assert complaint.screenshot_url is None
        assert complaint.resolution_note is None
        assert complaint.created_at is not None
        assert complaint.updated_at is not None


class TestComplaintStatusValidation:
    """
    **Property 39: Complaint Status Validation**
    **Validates: Requirement 15.1**
    
    For any complaint status update by an admin, status values in the set 
    {open, in_progress, resolved, closed} should succeed. Any other status 
    value should be rejected with status code 422.
    """
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        status=valid_complaint_statuses
    )
    def test_valid_complaint_statuses_succeed(
        self, db_session, sample_user, status
    ):
        """Test that all valid complaint statuses are accepted."""
        complaint = Complaint(
            title="Test complaint",
            description="Test description",
            category="technical",
            status=status,
            submitter_id=sample_user.id,
        )
        db_session.add(complaint)
        db_session.commit()
        
        # Verify status was set correctly
        assert complaint.status == status
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        status=invalid_complaint_statuses
    )
    def test_invalid_complaint_statuses_fail(
        self, db_session, sample_user, status
    ):
        """Test that invalid complaint statuses are rejected."""
        complaint = Complaint(
            title="Test complaint",
            description="Test description",
            category="technical",
            status=status,
            submitter_id=sample_user.id,
        )
        db_session.add(complaint)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()


class TestComplaintPriorityValidation:
    """
    **Property 40: Complaint Priority Validation**
    **Validates: Requirement 15.2**
    
    For any complaint priority update by an admin, priority values in the set 
    {low, medium, high, critical} should succeed. Any other priority value 
    should be rejected with status code 422.
    """
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        priority=valid_complaint_priorities
    )
    def test_valid_complaint_priorities_succeed(
        self, db_session, sample_user, priority
    ):
        """Test that all valid complaint priorities are accepted."""
        complaint = Complaint(
            title="Test complaint",
            description="Test description",
            category="technical",
            priority=priority,
            submitter_id=sample_user.id,
        )
        db_session.add(complaint)
        db_session.commit()
        
        # Verify priority was set correctly
        assert complaint.priority == priority
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        priority=invalid_complaint_priorities
    )
    def test_invalid_complaint_priorities_fail(
        self, db_session, sample_user, priority
    ):
        """Test that invalid complaint priorities are rejected."""
        complaint = Complaint(
            title="Test complaint",
            description="Test description",
            category="technical",
            priority=priority,
            submitter_id=sample_user.id,
        )
        db_session.add(complaint)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()


class TestActivityEventTypes:
    """
    **Property 45: Activity Feed Event Types**
    **Validates: Requirement 17.1**
    
    For any activity feed request, all returned events should have type 
    in the set {note_upload, user_registration, high_rating}.
    """
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        activity_type=valid_activity_types
    )
    def test_valid_activity_types_succeed(
        self, db_session, sample_user, activity_type
    ):
        """Test that all valid activity types are accepted."""
        activity = Activity(
            type=activity_type,
            user_id=sample_user.id,
            entity_id=uuid.uuid4(),
            metadata_={"test": "data"},
        )
        db_session.add(activity)
        db_session.commit()
        
        # Verify activity was created successfully
        assert activity.id is not None
        assert activity.type == activity_type
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        activity_type=invalid_activity_types
    )
    def test_invalid_activity_types_fail(
        self, db_session, sample_user, activity_type
    ):
        """Test that invalid activity types are rejected."""
        activity = Activity(
            type=activity_type,
            user_id=sample_user.id,
        )
        db_session.add(activity)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()


class TestForeignKeyCascadeBehavior:
    """
    **Property 57: Foreign Key Cascade Behavior**
    **Validates: Requirement 23.4**
    
    For any database record with foreign key relationships, deleting the 
    parent record should cascade to child records according to the defined 
    ON DELETE behavior (CASCADE for most relationships).
    """
    
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        num_complaints=st.integers(min_value=1, max_value=10)
    )
    def test_complaint_cascade_on_user_deletion(
        self, db_session, num_complaints
    ):
        """
        Test that complaints are deleted when the submitter is deleted.
        
        Property: For any number of complaints by a user, deleting the user
        should cascade delete all their complaints.
        """
        # Create fresh user per Hypothesis example to avoid stale references
        user = User(
            firebase_uid=f"casc_user_{uuid.uuid4().hex[:8]}",
            email=f"casc_{uuid.uuid4().hex[:8]}@test.com",
            name="Cascade User",
        )
        db_session.add(user)
        db_session.commit()

        # Create multiple complaints
        complaint_ids = []
        for i in range(num_complaints):
            complaint = Complaint(
                title=f"Complaint {i}",
                description=f"Description {i}",
                category="technical",
                submitter_id=user.id,
            )
            db_session.add(complaint)
            db_session.flush()
            complaint_ids.append(complaint.id)
        
        db_session.commit()
        
        # Verify complaints exist
        assert db_session.query(Complaint).filter(
            Complaint.submitter_id == user.id
        ).count() == num_complaints
        
        # Delete user
        db_session.delete(user)
        db_session.commit()
        
        # Verify all complaints were cascade deleted
        for complaint_id in complaint_ids:
            assert db_session.query(Complaint).filter_by(id=complaint_id).first() is None
    
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        num_responses=st.integers(min_value=1, max_value=10)
    )
    def test_complaint_response_cascade_on_complaint_deletion(
        self, db_session, sample_user, sample_admin, num_responses
    ):
        """
        Test that complaint responses are deleted when the complaint is deleted.
        
        Property: For any number of responses to a complaint, deleting the 
        complaint should cascade delete all its responses.
        """
        # Create complaint
        complaint = Complaint(
            title="Test complaint",
            description="Test description",
            category="technical",
            submitter_id=sample_user.id,
        )
        db_session.add(complaint)
        db_session.commit()
        
        # Create multiple responses
        response_ids = []
        for i in range(num_responses):
            response = ComplaintResponse(
                complaint_id=complaint.id,
                admin_id=sample_admin.id,
                text=f"Response {i}",
            )
            db_session.add(response)
            db_session.flush()
            response_ids.append(response.id)
        
        db_session.commit()
        
        # Verify responses exist
        assert db_session.query(ComplaintResponse).filter(
            ComplaintResponse.complaint_id == complaint.id
        ).count() == num_responses
        
        # Delete complaint
        db_session.delete(complaint)
        db_session.commit()
        
        # Verify all responses were cascade deleted
        for response_id in response_ids:
            assert db_session.query(ComplaintResponse).filter_by(
                id=response_id
            ).first() is None
    
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        num_activities=st.integers(min_value=1, max_value=10)
    )
    def test_activity_cascade_on_user_deletion(
        self, db_session, num_activities
    ):
        """
        Test that activities are deleted when the related user is deleted.
        
        Property: For any number of activities by a user, deleting the user
        should cascade delete all their activities.
        """
        # Create fresh user per Hypothesis example to avoid stale references
        user = User(
            firebase_uid=f"act_casc_{uuid.uuid4().hex[:8]}",
            email=f"act_{uuid.uuid4().hex[:8]}@test.com",
            name="Activity Cascade User",
        )
        db_session.add(user)
        db_session.commit()

        # Create multiple activities
        activity_ids = []
        for i in range(num_activities):
            activity = Activity(
                type="note_upload",
                user_id=user.id,
                entity_id=uuid.uuid4(),
                metadata_={"index": i},
            )
            db_session.add(activity)
            db_session.flush()
            activity_ids.append(activity.id)
        
        db_session.commit()
        
        # Verify activities exist
        assert db_session.query(Activity).filter(
            Activity.user_id == user.id
        ).count() == num_activities
        
        # Delete user
        db_session.delete(user)
        db_session.commit()
        
        # Verify all activities were cascade deleted
        for activity_id in activity_ids:
            assert db_session.query(Activity).filter_by(id=activity_id).first() is None


class TestComplaintResponseCascade:
    """
    Additional cascade tests for complaint responses.
    
    **Validates: Requirement 23.4**
    """
    
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        num_responses=st.integers(min_value=1, max_value=10)
    )
    def test_complaint_response_cascade_on_admin_deletion(
        self, db_session, sample_user, num_responses
    ):
        """
        Test that complaint responses are deleted when the admin is deleted.
        
        Property: For any number of responses by an admin, deleting the admin
        should cascade delete all their responses.
        """
        # Create fresh admin per Hypothesis example to avoid stale references
        admin = User(
            firebase_uid=f"resp_admin_{uuid.uuid4().hex[:8]}",
            email=f"resp_admin_{uuid.uuid4().hex[:8]}@test.com",
            name="Resp Admin",
            role="admin",
        )
        db_session.add(admin)
        db_session.commit()

        # Create complaint
        complaint = Complaint(
            title="Test complaint",
            description="Test description",
            category="technical",
            submitter_id=sample_user.id,
        )
        db_session.add(complaint)
        db_session.commit()
        
        # Create multiple responses
        response_ids = []
        for i in range(num_responses):
            response = ComplaintResponse(
                complaint_id=complaint.id,
                admin_id=admin.id,
                text=f"Response {i}",
            )
            db_session.add(response)
            db_session.flush()
            response_ids.append(response.id)
        
        db_session.commit()
        
        # Verify responses exist
        assert db_session.query(ComplaintResponse).filter(
            ComplaintResponse.admin_id == admin.id
        ).count() == num_responses
        
        # Delete admin
        db_session.delete(admin)
        db_session.commit()
        
        # Verify all responses were cascade deleted
        for response_id in response_ids:
            assert db_session.query(ComplaintResponse).filter_by(
                id=response_id
            ).first() is None
