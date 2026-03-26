"""
Unit tests for Chat models

Tests the ChatGroup, ChatMembership, and Message SQLAlchemy models
including field validation, constraints, defaults, and database operations.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.core.database import Base
from app.models import User, ChatGroup, ChatMembership, Message


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
def sample_chat_group(db_session, sample_user):
    """Create a sample chat group for testing"""
    group = ChatGroup(
        name="Test Group",
        description="Test Description",
        join_code="ABC12345",
        creator_id=sample_user.id
    )
    db_session.add(group)
    db_session.commit()
    return group


# ChatGroup Tests

def test_chat_group_creation_with_required_fields(db_session, sample_user):
    """Test creating a chat group with required fields"""
    group = ChatGroup(
        name="Study Group",
        join_code="XYZ98765",
        creator_id=sample_user.id
    )
    db_session.add(group)
    db_session.commit()
    
    assert group.id is not None
    assert group.name == "Study Group"
    assert group.join_code == "XYZ98765"
    assert group.creator_id == sample_user.id
    assert group.member_count == 1  # Default value
    assert group.description is None
    assert group.last_message is None
    assert group.last_message_at is None
    assert group.created_at is not None
    assert group.updated_at is not None


def test_chat_group_creation_with_all_fields(db_session, sample_user):
    """Test creating a chat group with all fields"""
    group = ChatGroup(
        name="Advanced Study Group",
        description="For advanced students",
        join_code="ADV12345",
        creator_id=sample_user.id,
        member_count=5,
        last_message="Hello everyone!",
        last_message_at=datetime.utcnow()
    )
    db_session.add(group)
    db_session.commit()
    
    assert group.description == "For advanced students"
    assert group.member_count == 5
    assert group.last_message == "Hello everyone!"
    assert group.last_message_at is not None


def test_chat_group_unique_join_code(db_session, sample_user):
    """Test that join_code must be unique"""
    group1 = ChatGroup(
        name="Group 1",
        join_code="UNIQUE01",
        creator_id=sample_user.id
    )
    db_session.add(group1)
    db_session.commit()
    
    group2 = ChatGroup(
        name="Group 2",
        join_code="UNIQUE01",  # Duplicate join_code
        creator_id=sample_user.id
    )
    db_session.add(group2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_chat_group_cascade_delete_on_creator_deletion(db_session, sample_user):
    """Test that chat groups are deleted when creator is deleted"""
    group = ChatGroup(
        name="Test Group",
        join_code="TEST1234",
        creator_id=sample_user.id
    )
    db_session.add(group)
    db_session.commit()
    
    group_id = group.id
    
    # Delete the creator
    db_session.delete(sample_user)
    db_session.commit()
    
    # Group should be deleted
    found_group = db_session.query(ChatGroup).filter_by(id=group_id).first()
    assert found_group is None


def test_chat_group_query_by_join_code(db_session, sample_user):
    """Test querying chat group by join_code"""
    group = ChatGroup(
        name="Query Test Group",
        join_code="QUERY123",
        creator_id=sample_user.id
    )
    db_session.add(group)
    db_session.commit()
    
    found_group = db_session.query(ChatGroup).filter_by(join_code="QUERY123").first()
    assert found_group is not None
    assert found_group.name == "Query Test Group"


def test_chat_group_repr(db_session, sample_user):
    """Test the string representation of ChatGroup"""
    group = ChatGroup(
        name="Repr Test Group",
        join_code="REPR1234",
        creator_id=sample_user.id,
        member_count=10
    )
    db_session.add(group)
    db_session.commit()
    
    repr_str = repr(group)
    assert "ChatGroup" in repr_str
    assert "Repr Test Group" in repr_str
    assert "REPR1234" in repr_str
    assert "10" in repr_str


# ChatMembership Tests

def test_chat_membership_creation(db_session, sample_user, sample_chat_group):
    """Test creating a chat membership"""
    membership = ChatMembership(
        group_id=sample_chat_group.id,
        user_id=sample_user.id
    )
    db_session.add(membership)
    db_session.commit()
    
    assert membership.id is not None
    assert membership.group_id == sample_chat_group.id
    assert membership.user_id == sample_user.id
    assert membership.joined_at is not None
    assert isinstance(membership.joined_at, datetime)


def test_chat_membership_unique_constraint(db_session, sample_user, sample_chat_group):
    """Test that a user can only join a group once"""
    membership1 = ChatMembership(
        group_id=sample_chat_group.id,
        user_id=sample_user.id
    )
    db_session.add(membership1)
    db_session.commit()
    
    # Try to create another membership for the same group and user
    membership2 = ChatMembership(
        group_id=sample_chat_group.id,
        user_id=sample_user.id
    )
    db_session.add(membership2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_chat_membership_cascade_delete_on_group_deletion(db_session, sample_user, sample_chat_group):
    """Test that memberships are deleted when group is deleted"""
    membership = ChatMembership(
        group_id=sample_chat_group.id,
        user_id=sample_user.id
    )
    db_session.add(membership)
    db_session.commit()
    
    membership_id = membership.id
    
    # Delete the group
    db_session.delete(sample_chat_group)
    db_session.commit()
    
    # Membership should be deleted
    found_membership = db_session.query(ChatMembership).filter_by(id=membership_id).first()
    assert found_membership is None


def test_chat_membership_cascade_delete_on_user_deletion(db_session, sample_user, sample_chat_group):
    """Test that memberships are deleted when user is deleted"""
    membership = ChatMembership(
        group_id=sample_chat_group.id,
        user_id=sample_user.id
    )
    db_session.add(membership)
    db_session.commit()
    
    membership_id = membership.id
    
    # Delete the user
    db_session.delete(sample_user)
    db_session.commit()
    
    # Membership should be deleted
    found_membership = db_session.query(ChatMembership).filter_by(id=membership_id).first()
    assert found_membership is None


def test_chat_membership_query_by_group(db_session, sample_chat_group):
    """Test querying memberships by group_id"""
    # Create multiple users and memberships
    for i in range(3):
        user = User(
            firebase_uid=f"user_{i}",
            email=f"user{i}@example.com",
            name=f"User {i}"
        )
        db_session.add(user)
        db_session.commit()
        
        membership = ChatMembership(
            group_id=sample_chat_group.id,
            user_id=user.id
        )
        db_session.add(membership)
    
    db_session.commit()
    
    memberships = db_session.query(ChatMembership).filter_by(group_id=sample_chat_group.id).all()
    assert len(memberships) == 3


def test_chat_membership_repr(db_session, sample_user, sample_chat_group):
    """Test the string representation of ChatMembership"""
    membership = ChatMembership(
        group_id=sample_chat_group.id,
        user_id=sample_user.id
    )
    db_session.add(membership)
    db_session.commit()
    
    repr_str = repr(membership)
    assert "ChatMembership" in repr_str
    assert str(sample_chat_group.id) in repr_str
    assert str(sample_user.id) in repr_str


# Message Tests

def test_message_creation_text_type(db_session, sample_user, sample_chat_group):
    """Test creating a text message"""
    message = Message(
        group_id=sample_chat_group.id,
        sender_id=sample_user.id,
        content="Hello, world!",
        type="text"
    )
    db_session.add(message)
    db_session.commit()
    
    assert message.id is not None
    assert message.group_id == sample_chat_group.id
    assert message.sender_id == sample_user.id
    assert message.content == "Hello, world!"
    assert message.type == "text"
    assert message.file_url is None
    assert message.created_at is not None


def test_message_creation_file_type(db_session, sample_user, sample_chat_group):
    """Test creating a file message"""
    message = Message(
        group_id=sample_chat_group.id,
        sender_id=sample_user.id,
        content="Check out this file",
        type="file",
        file_url="https://example.com/file.pdf"
    )
    db_session.add(message)
    db_session.commit()
    
    assert message.type == "file"
    assert message.file_url == "https://example.com/file.pdf"


def test_message_default_type(db_session, sample_user, sample_chat_group):
    """Test that message type defaults to 'text'"""
    message = Message(
        group_id=sample_chat_group.id,
        sender_id=sample_user.id,
        content="Default type message"
    )
    db_session.add(message)
    db_session.commit()
    
    assert message.type == "text"


def test_message_cascade_delete_on_group_deletion(db_session, sample_user, sample_chat_group):
    """Test that messages are deleted when group is deleted"""
    message = Message(
        group_id=sample_chat_group.id,
        sender_id=sample_user.id,
        content="Test message"
    )
    db_session.add(message)
    db_session.commit()
    
    message_id = message.id
    
    # Delete the group
    db_session.delete(sample_chat_group)
    db_session.commit()
    
    # Message should be deleted
    found_message = db_session.query(Message).filter_by(id=message_id).first()
    assert found_message is None


def test_message_cascade_delete_on_sender_deletion(db_session, sample_user, sample_chat_group):
    """Test that messages are deleted when sender is deleted"""
    message = Message(
        group_id=sample_chat_group.id,
        sender_id=sample_user.id,
        content="Test message"
    )
    db_session.add(message)
    db_session.commit()
    
    message_id = message.id
    
    # Delete the sender
    db_session.delete(sample_user)
    db_session.commit()
    
    # Message should be deleted
    found_message = db_session.query(Message).filter_by(id=message_id).first()
    assert found_message is None


def test_message_query_by_group(db_session, sample_user, sample_chat_group):
    """Test querying messages by group_id"""
    # Create multiple messages
    for i in range(3):
        message = Message(
            group_id=sample_chat_group.id,
            sender_id=sample_user.id,
            content=f"Message {i}"
        )
        db_session.add(message)
    
    db_session.commit()
    
    messages = db_session.query(Message).filter_by(group_id=sample_chat_group.id).all()
    assert len(messages) == 3


def test_message_query_by_sender(db_session, sample_user, sample_chat_group):
    """Test querying messages by sender_id"""
    message = Message(
        group_id=sample_chat_group.id,
        sender_id=sample_user.id,
        content="Sender test message"
    )
    db_session.add(message)
    db_session.commit()
    
    messages = db_session.query(Message).filter_by(sender_id=sample_user.id).all()
    assert len(messages) == 1
    assert messages[0].content == "Sender test message"


def test_message_repr(db_session, sample_user, sample_chat_group):
    """Test the string representation of Message"""
    message = Message(
        group_id=sample_chat_group.id,
        sender_id=sample_user.id,
        content="Repr test message",
        type="text"
    )
    db_session.add(message)
    db_session.commit()
    
    repr_str = repr(message)
    assert "Message" in repr_str
    assert str(sample_chat_group.id) in repr_str
    assert str(sample_user.id) in repr_str
    assert "text" in repr_str
