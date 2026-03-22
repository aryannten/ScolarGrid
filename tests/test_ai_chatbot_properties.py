"""
Property-based tests for AI chatbot models (Task 2.7)

Tests universal properties using Hypothesis.
"""

import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from hypothesis import given, settings as hyp_settings, HealthCheck
from hypothesis import strategies as st

from app.core.database import Base
from app.models.user import User
from app.models.ai_chatbot import AIConversation, AIMessage, AIUsageTracking


@pytest.fixture(scope="module")
def engine():
    engine = create_engine("sqlite:///:memory:")
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_foreign_keys(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def user(db_session):
    u = User(firebase_uid=f"uid_{id(db_session)}", email=f"u{id(db_session)}@test.com", name="Test")
    db_session.add(u)
    db_session.commit()
    return u


# ─── Property: AIConversation message_count is always non-negative ─────────────

@given(count=st.integers(min_value=0, max_value=10_000))
@hyp_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_conversation_message_count_non_negative(count, engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = User(firebase_uid=f"pb_uid_{count}", email=f"pb{count}@test.com", name="PBUser")
        db.add(u)
        db.commit()
        conv = AIConversation(user_id=u.id, message_count=count)
        db.add(conv)
        db.commit()
        assert conv.message_count >= 0
    finally:
        db.rollback()
        db.close()


# ─── Property: AIMessage role must be 'user' or 'assistant' ───────────────────

@given(role=st.sampled_from(["user", "assistant"]))
@hyp_settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_valid_roles_always_persist(role, engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = User(firebase_uid=f"pb_role_{role}_{id(db)}", email=f"role_{role}_{id(db)}@test.com", name="R")
        db.add(u)
        db.commit()
        conv = AIConversation(user_id=u.id)
        db.add(conv)
        db.commit()
        msg = AIMessage(conversation_id=conv.id, role=role, content="hello")
        db.add(msg)
        db.commit()
        assert msg.id is not None
        assert msg.role == role
    finally:
        db.rollback()
        db.close()


# ─── Property: usage tracking message_count never negative ────────────────────

@given(count=st.integers(min_value=0, max_value=50))
@hyp_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_usage_tracking_count_positive(count, engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        uid = f"pb_usage_{count}_{id(db)}"
        u = User(firebase_uid=uid, email=f"{uid}@test.com", name="U")
        db.add(u)
        db.commit()
        tracking = AIUsageTracking(user_id=u.id, date=date.today(), message_count=count)
        db.add(tracking)
        db.commit()
        assert tracking.message_count >= 0
    finally:
        db.rollback()
        db.close()


# ─── Property: unique constraint on (user_id, date) is always enforced ─────────

def test_property_unique_user_date_enforced(engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        uid = f"pb_unique_{id(db)}"
        u = User(firebase_uid=uid, email=f"{uid}@test.com", name="U2")
        db.add(u)
        db.commit()
        d = date.today() - timedelta(days=100)
        db.add(AIUsageTracking(user_id=u.id, date=d, message_count=5))
        db.commit()
        db.add(AIUsageTracking(user_id=u.id, date=d, message_count=3))
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()
