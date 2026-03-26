"""
Unit tests for AI Chatbot models

Tests AIConversation, AIMessage, and AIUsageTracking SQLAlchemy models
including field validation, constraints, defaults, and cascade deletes.
"""

import pytest
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.core.database import Base
from app.models import User, AIConversation, AIMessage, AIUsageTracking


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")

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
        firebase_uid="ai_test_user_uid",
        email="ai_user@example.com",
        name="AI Test User"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_conversation(db_session, sample_user):
    """Create a sample AI conversation for testing"""
    conversation = AIConversation(
        user_id=sample_user.id,
        title="What is machine learning?"
    )
    db_session.add(conversation)
    db_session.commit()
    return conversation


# ─── AIConversation Tests ──────────────────────────────────────────────────────

def test_ai_conversation_creation_with_required_fields(db_session, sample_user):
    """Test creating an AIConversation with required fields"""
    conversation = AIConversation(user_id=sample_user.id)
    db_session.add(conversation)
    db_session.commit()

    assert conversation.id is not None
    assert conversation.user_id == sample_user.id
    assert conversation.title is None
    assert conversation.message_count == 0
    assert conversation.created_at is not None
    assert conversation.updated_at is not None
    assert isinstance(conversation.created_at, datetime)


def test_ai_conversation_creation_with_all_fields(db_session, sample_user):
    """Test creating an AIConversation with all fields"""
    conversation = AIConversation(
        user_id=sample_user.id,
        title="Tell me about neural networks",
        message_count=5
    )
    db_session.add(conversation)
    db_session.commit()

    assert conversation.title == "Tell me about neural networks"
    assert conversation.message_count == 5


def test_ai_conversation_default_message_count(db_session, sample_user):
    """Test that message_count defaults to 0"""
    conversation = AIConversation(user_id=sample_user.id)
    db_session.add(conversation)
    db_session.commit()

    assert conversation.message_count == 0


def test_ai_conversation_cascade_delete_on_user_deletion(db_session, sample_user, sample_conversation):
    """Test that conversations are deleted when user is deleted"""
    conversation_id = sample_conversation.id

    db_session.delete(sample_user)
    db_session.commit()

    found = db_session.query(AIConversation).filter_by(id=conversation_id).first()
    assert found is None


def test_ai_conversation_query_by_user(db_session, sample_user):
    """Test querying conversations by user_id"""
    for i in range(3):
        conv = AIConversation(user_id=sample_user.id, title=f"Conversation {i}")
        db_session.add(conv)
    db_session.commit()

    conversations = db_session.query(AIConversation).filter_by(user_id=sample_user.id).all()
    assert len(conversations) == 3


def test_ai_conversation_repr(db_session, sample_user):
    """Test the string representation of AIConversation"""
    conversation = AIConversation(user_id=sample_user.id, message_count=3)
    db_session.add(conversation)
    db_session.commit()

    repr_str = repr(conversation)
    assert "AIConversation" in repr_str
    assert str(sample_user.id) in repr_str
    assert "3" in repr_str


# ─── AIMessage Tests ───────────────────────────────────────────────────────────

def test_ai_message_creation_user_role(db_session, sample_conversation):
    """Test creating a user message"""
    message = AIMessage(
        conversation_id=sample_conversation.id,
        role="user",
        content="What is gradient descent?"
    )
    db_session.add(message)
    db_session.commit()

    assert message.id is not None
    assert message.conversation_id == sample_conversation.id
    assert message.role == "user"
    assert message.content == "What is gradient descent?"
    assert message.created_at is not None


def test_ai_message_creation_assistant_role(db_session, sample_conversation):
    """Test creating an assistant message"""
    message = AIMessage(
        conversation_id=sample_conversation.id,
        role="assistant",
        content="Gradient descent is an optimization algorithm..."
    )
    db_session.add(message)
    db_session.commit()

    assert message.role == "assistant"
    assert "optimization" in message.content


def test_ai_message_invalid_role_rejected(db_session, sample_conversation):
    """Test that invalid roles are rejected by DB constraint"""
    message = AIMessage(
        conversation_id=sample_conversation.id,
        role="system",  # Not allowed — only 'user'/'assistant'
        content="This should fail"
    )
    db_session.add(message)

    with pytest.raises(Exception):  # IntegrityError or similar
        db_session.commit()


def test_ai_message_cascade_delete_on_conversation(db_session, sample_user, sample_conversation):
    """Test that messages are deleted when conversation is deleted"""
    message = AIMessage(
        conversation_id=sample_conversation.id,
        role="user",
        content="Test message"
    )
    db_session.add(message)
    db_session.commit()
    message_id = message.id

    db_session.delete(sample_conversation)
    db_session.commit()

    found = db_session.query(AIMessage).filter_by(id=message_id).first()
    assert found is None


def test_ai_message_query_by_conversation(db_session, sample_conversation):
    """Test querying messages by conversation_id"""
    roles = ["user", "assistant", "user"]
    for i, role in enumerate(roles):
        msg = AIMessage(
            conversation_id=sample_conversation.id,
            role=role,
            content=f"Message {i}"
        )
        db_session.add(msg)
    db_session.commit()

    messages = db_session.query(AIMessage).filter_by(conversation_id=sample_conversation.id).all()
    assert len(messages) == 3


def test_ai_message_repr(db_session, sample_conversation):
    """Test the string representation of AIMessage"""
    message = AIMessage(
        conversation_id=sample_conversation.id,
        role="user",
        content="Hello AI"
    )
    db_session.add(message)
    db_session.commit()

    repr_str = repr(message)
    assert "AIMessage" in repr_str
    assert str(sample_conversation.id) in repr_str
    assert "user" in repr_str


# ─── AIUsageTracking Tests ─────────────────────────────────────────────────────

def test_ai_usage_tracking_creation(db_session, sample_user):
    """Test creating an AIUsageTracking record"""
    today = date.today()
    tracking = AIUsageTracking(
        user_id=sample_user.id,
        date=today,
        message_count=5
    )
    db_session.add(tracking)
    db_session.commit()

    assert tracking.id is not None
    assert tracking.user_id == sample_user.id
    assert tracking.date == today
    assert tracking.message_count == 5
    assert tracking.created_at is not None
    assert tracking.updated_at is not None


def test_ai_usage_tracking_default_message_count(db_session, sample_user):
    """Test that message_count defaults to 0"""
    tracking = AIUsageTracking(user_id=sample_user.id, date=date.today())
    db_session.add(tracking)
    db_session.commit()

    assert tracking.message_count == 0


def test_ai_usage_tracking_unique_constraint(db_session, sample_user):
    """Test that duplicate (user_id, date) raises IntegrityError"""
    today = date.today()
    tracking1 = AIUsageTracking(user_id=sample_user.id, date=today, message_count=10)
    db_session.add(tracking1)
    db_session.commit()

    tracking2 = AIUsageTracking(user_id=sample_user.id, date=today, message_count=5)
    db_session.add(tracking2)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_ai_usage_tracking_different_dates_allowed(db_session, sample_user):
    """Test that same user can have tracking for different dates"""
    from datetime import timedelta
    today = date.today()
    yesterday = today - timedelta(days=1)

    tracking1 = AIUsageTracking(user_id=sample_user.id, date=today, message_count=10)
    tracking2 = AIUsageTracking(user_id=sample_user.id, date=yesterday, message_count=20)
    db_session.add_all([tracking1, tracking2])
    db_session.commit()

    records = db_session.query(AIUsageTracking).filter_by(user_id=sample_user.id).all()
    assert len(records) == 2


def test_ai_usage_tracking_cascade_delete_on_user(db_session, sample_user):
    """Test that tracking records are deleted when user is deleted"""
    tracking = AIUsageTracking(user_id=sample_user.id, date=date.today(), message_count=3)
    db_session.add(tracking)
    db_session.commit()
    tracking_id = tracking.id

    db_session.delete(sample_user)
    db_session.commit()

    found = db_session.query(AIUsageTracking).filter_by(id=tracking_id).first()
    assert found is None


def test_ai_usage_tracking_repr(db_session, sample_user):
    """Test the string representation of AIUsageTracking"""
    today = date.today()
    tracking = AIUsageTracking(user_id=sample_user.id, date=today, message_count=42)
    db_session.add(tracking)
    db_session.commit()

    repr_str = repr(tracking)
    assert "AIUsageTracking" in repr_str
    assert str(sample_user.id) in repr_str
    assert "42" in repr_str
