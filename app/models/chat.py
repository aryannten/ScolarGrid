"""
SQLAlchemy ORM models for Chat entities

This module defines the ChatGroup, ChatMembership, and Message models
representing the real-time chat system.
"""

from sqlalchemy import String, Integer, Text, TIMESTAMP, CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import Optional
import uuid

from app.core.database import Base


class ChatGroup(Base):
    """
    ChatGroup model representing a chat group.
    
    Attributes:
        id: Unique identifier (UUID)
        name: Group name
        description: Group description
        join_code: Unique 8-character alphanumeric code for joining
        creator_id: Foreign key to users table (group creator)
        member_count: Number of members in the group
        last_message: Content of the last message sent
        last_message_at: Timestamp of the last message
        created_at: Group creation timestamp
        updated_at: Last group update timestamp
    """
    
    __tablename__ = "chat_groups"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Group information
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        default=None
    )
    
    join_code: Mapped[str] = mapped_column(
        String(8),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Foreign key to creator
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Group statistics
    member_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )
    
    # Last message tracking
    last_message: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        default=None
    )
    
    last_message_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        return f"<ChatGroup(id={self.id}, name={self.name}, join_code={self.join_code}, member_count={self.member_count})>"


class ChatMembership(Base):
    """
    ChatMembership model representing user membership in chat groups.
    
    Attributes:
        id: Unique identifier (UUID)
        group_id: Foreign key to chat_groups table
        user_id: Foreign key to users table
        joined_at: Membership creation timestamp
    """
    
    __tablename__ = "chat_memberships"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign keys
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Timestamp
    joined_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
    
    # Table constraints
    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_membership_group_user"),
    )
    
    def __repr__(self) -> str:
        return f"<ChatMembership(id={self.id}, group_id={self.group_id}, user_id={self.user_id})>"


class Message(Base):
    """
    Message model representing messages in chat groups.
    
    Attributes:
        id: Unique identifier (UUID)
        group_id: Foreign key to chat_groups table
        sender_id: Foreign key to users table
        content: Message content text
        type: Message type (text or file)
        file_url: URL to file in Firebase Storage (for file messages)
        created_at: Message creation timestamp
    """
    
    __tablename__ = "messages"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign keys
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Message content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="text"
    )
    
    file_url: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        default=None
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('text', 'file')",
            name="check_message_type"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, group_id={self.group_id}, sender_id={self.sender_id}, type={self.type})>"
