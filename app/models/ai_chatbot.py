"""
SQLAlchemy ORM models for AI Chatbot entities

This module defines the AIConversation, AIMessage, and AIUsageTracking models
for the Google Gemini-powered AI chatbot feature.
"""

from sqlalchemy import String, Integer, Text, TIMESTAMP, Date, CheckConstraint, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date
from typing import Optional
import uuid

from app.core.database import Base


class AIConversation(Base):
    """
    AIConversation model representing a chat session between a user and the AI chatbot.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to users table (CASCADE delete)
        title: Conversation title (first message preview, max 200 chars)
        message_count: Total number of messages in the conversation
        created_at: Conversation creation timestamp
        updated_at: Last update timestamp (updated on each new message)
    """

    __tablename__ = "ai_conversations"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Foreign key to user
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Conversation metadata
    title: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        default=None
    )

    message_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
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
        return f"<AIConversation(id={self.id}, user_id={self.user_id}, message_count={self.message_count})>"


class AIMessage(Base):
    """
    AIMessage model representing a single message in an AI chatbot conversation.

    Attributes:
        id: Unique identifier (UUID)
        conversation_id: Foreign key to ai_conversations table (CASCADE delete)
        role: Message role — 'user' or 'assistant'
        content: Message content text
        created_at: Message creation timestamp
    """

    __tablename__ = "ai_messages"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Foreign key to conversation
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Message content
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
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
            "role IN ('user', 'assistant')",
            name="check_ai_message_role"
        ),
    )

    def __repr__(self) -> str:
        return f"<AIMessage(id={self.id}, conversation_id={self.conversation_id}, role={self.role})>"


class AIUsageTracking(Base):
    """
    AIUsageTracking model for tracking daily AI chatbot usage per user.

    Enforces the 50 messages/day limit with a unique constraint on (user_id, date).

    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to users table (CASCADE delete)
        date: The calendar date being tracked
        message_count: Number of messages sent on this date
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "ai_usage_tracking"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Foreign key to user
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Usage tracking fields
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    message_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
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

    # Table constraints — unique per user per day
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_ai_usage_user_date"),
        Index("idx_ai_usage_user_date", "user_id", "date"),
    )

    def __repr__(self) -> str:
        return f"<AIUsageTracking(id={self.id}, user_id={self.user_id}, date={self.date}, message_count={self.message_count})>"
