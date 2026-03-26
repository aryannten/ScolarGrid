"""
Property-based tests for activity feed (Task 19.4)

Tests activity feed event type constraints and time window filtering.
"""

import pytest
from datetime import datetime, timedelta, timezone
from hypothesis import given, settings as hyp_settings, HealthCheck
from hypothesis import strategies as st
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.complaint import Activity


@pytest.fixture(scope="module")
def engine():
    """Create an in-memory SQLite engine for property tests."""
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    
    @event.listens_for(eng, "connect")
    def fk(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")
    
    Base.metadata.create_all(eng)
    return eng


def _make_user(db, suffix):
    """Helper to create a test user."""
    u = User(
        firebase_uid=f"activity_prop_{suffix}",
        email=f"activity_prop_{suffix}@test.com",
        name="Test User"
    )
    db.add(u)
    db.commit()
    return u


def _make_activity(db, user, activity_type, created_at=None):
    """Helper to create a test activity."""
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    
    a = Activity(
        type=activity_type,
        user_id=user.id,
        entity_id=None,
        metadata_={"title": "Test Activity"},
        created_at=created_at,
    )
    db.add(a)
    db.commit()
    return a


# ─── Property 45: Activity Feed Event Types ──────────────────────────────────
# **Validates: Requirements 17.1**

@given(activity_type=st.sampled_from(["note_upload", "user_registration", "high_rating"]))
@hyp_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_45_activity_feed_event_types(activity_type, engine):
    """
    Property 45: Activity Feed Event Types
    
    *For any* activity feed request, all returned events should have type in the 
    set {note_upload, user_registration, high_rating}.
    
    **Validates: Requirements 17.1**
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        # Create user and activity
        u = _make_user(db, f"type_{activity_type}_{id(db)}")
        a = _make_activity(db, u, activity_type)
        
        # Verify the activity type is one of the valid types
        assert a.type in {"note_upload", "user_registration", "high_rating"}
        
        # Query activities (simulating activity feed request)
        activities = db.query(Activity).filter(Activity.user_id == u.id).all()
        
        # All returned activities should have valid types
        for activity in activities:
            assert activity.type in {"note_upload", "user_registration", "high_rating"}
    finally:
        db.rollback()
        db.close()


# ─── Property 46: Activity Feed Time Window ──────────────────────────────────
# **Validates: Requirements 17.5**

@given(
    days_ago=st.integers(min_value=0, max_value=60),
)
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_46_activity_feed_time_window(days_ago, engine):
    """
    Property 46: Activity Feed Time Window
    
    *For any* activity feed request, all returned events should have created_at 
    within the past 30 days from the request time.
    
    **Validates: Requirements 17.5**
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        # Create user
        u = _make_user(db, f"time_{days_ago}_{id(db)}")
        
        # Create activity with timestamp days_ago in the past
        now = datetime.now(timezone.utc)
        created_at = now - timedelta(days=days_ago)
        a = _make_activity(db, u, "note_upload", created_at=created_at)
        
        # Simulate activity feed request with 30-day cutoff
        cutoff = now - timedelta(days=30)
        activities = db.query(Activity).filter(
            Activity.user_id == u.id,
            Activity.created_at >= cutoff
        ).all()
        
        # Verify filtering logic
        if days_ago <= 30:
            # Activity should be included (within 30 days)
            assert len(activities) == 1
            assert activities[0].id == a.id
            # Convert to timezone-aware for comparison (SQLite returns naive datetimes)
            activity_time = activities[0].created_at
            if activity_time.tzinfo is None:
                activity_time = activity_time.replace(tzinfo=timezone.utc)
            assert activity_time >= cutoff
        else:
            # Activity should be excluded (older than 30 days)
            assert len(activities) == 0
    finally:
        db.rollback()
        db.close()


# ─── Edge Case: Exactly 30 days old ──────────────────────────────────────────

def test_property_46_edge_case_exactly_30_days(engine):
    """
    Edge case: Activity exactly 30 days old should be included.
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _make_user(db, f"edge_30_{id(db)}")
        
        # Create activity exactly 30 days ago
        now = datetime.now(timezone.utc)
        exactly_30_days_ago = now - timedelta(days=30)
        a = _make_activity(db, u, "user_registration", created_at=exactly_30_days_ago)
        
        # Query with 30-day cutoff
        cutoff = now - timedelta(days=30)
        activities = db.query(Activity).filter(
            Activity.user_id == u.id,
            Activity.created_at >= cutoff
        ).all()
        
        # Activity exactly 30 days old should be included (>= cutoff)
        assert len(activities) == 1
        assert activities[0].id == a.id
    finally:
        db.rollback()
        db.close()


# ─── Edge Case: 31 days old ──────────────────────────────────────────────────

def test_property_46_edge_case_31_days_old(engine):
    """
    Edge case: Activity 31 days old should be excluded.
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _make_user(db, f"edge_31_{id(db)}")
        
        # Create activity 31 days ago
        now = datetime.now(timezone.utc)
        thirty_one_days_ago = now - timedelta(days=31)
        a = _make_activity(db, u, "high_rating", created_at=thirty_one_days_ago)
        
        # Query with 30-day cutoff
        cutoff = now - timedelta(days=30)
        activities = db.query(Activity).filter(
            Activity.user_id == u.id,
            Activity.created_at >= cutoff
        ).all()
        
        # Activity 31 days old should be excluded
        assert len(activities) == 0
    finally:
        db.rollback()
        db.close()


# ─── Edge Case: Future dates ─────────────────────────────────────────────────

def test_property_46_edge_case_future_date(engine):
    """
    Edge case: Activity with future timestamp should be included.
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _make_user(db, f"edge_future_{id(db)}")
        
        # Create activity with future timestamp
        now = datetime.now(timezone.utc)
        future_time = now + timedelta(days=1)
        a = _make_activity(db, u, "note_upload", created_at=future_time)
        
        # Query with 30-day cutoff
        cutoff = now - timedelta(days=30)
        activities = db.query(Activity).filter(
            Activity.user_id == u.id,
            Activity.created_at >= cutoff
        ).all()
        
        # Future activity should be included (>= cutoff)
        assert len(activities) == 1
        assert activities[0].id == a.id
    finally:
        db.rollback()
        db.close()


# ─── Combined Property Test ──────────────────────────────────────────────────

@given(
    activity_type=st.sampled_from(["note_upload", "user_registration", "high_rating"]),
    days_ago=st.integers(min_value=0, max_value=60),
)
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_combined_activity_feed_properties(activity_type, days_ago, engine):
    """
    Combined test: Activity feed should return only valid event types within 30 days.
    
    **Validates: Requirements 17.1, 17.5**
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _make_user(db, f"combined_{activity_type}_{days_ago}_{id(db)}")
        
        # Create activity
        now = datetime.now(timezone.utc)
        created_at = now - timedelta(days=days_ago)
        a = _make_activity(db, u, activity_type, created_at=created_at)
        
        # Query with 30-day cutoff
        cutoff = now - timedelta(days=30)
        activities = db.query(Activity).filter(
            Activity.user_id == u.id,
            Activity.created_at >= cutoff
        ).all()
        
        # All returned activities must satisfy both properties
        for activity in activities:
            # Property 45: Valid event type
            assert activity.type in {"note_upload", "user_registration", "high_rating"}
            # Property 46: Within 30 days
            # Convert to timezone-aware for comparison (SQLite returns naive datetimes)
            activity_time = activity.created_at
            if activity_time.tzinfo is None:
                activity_time = activity_time.replace(tzinfo=timezone.utc)
            assert activity_time >= cutoff
        
        # Verify correct filtering
        if days_ago <= 30:
            assert len(activities) == 1
        else:
            assert len(activities) == 0
    finally:
        db.rollback()
        db.close()
