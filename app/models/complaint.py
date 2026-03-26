"""
SQLAlchemy ORM models for complaint and activity entities.

This module defines the Complaint, ComplaintResponse, and Activity models
used for issue tracking and the public activity feed.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, TIMESTAMP, JSON, desc
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Complaint(Base):
    """
    Complaint model representing a user-submitted issue or feature request.

    Attributes:
        id: Unique identifier (UUID)
        title: Complaint title
        description: Detailed complaint description
        category: Complaint category
        status: Complaint lifecycle status
        priority: Complaint severity priority
        screenshot_url: Optional Firebase Storage URL for an attached screenshot
        resolution_note: Optional note explaining how the complaint was resolved
        submitter_id: Foreign key to the user who submitted the complaint
        created_at: Complaint creation timestamp
        updated_at: Last complaint update timestamp
    """

    __tablename__ = "complaints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
        index=True,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
        index=True,
    )

    screenshot_url: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        default=None,
    )

    resolution_note: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )

    submitter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        CheckConstraint(
            "category IN ('technical', 'content', 'account', 'feature_request', 'other')",
            name="check_complaint_category",
        ),
        CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved', 'closed')",
            name="check_complaint_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'critical')",
            name="check_complaint_priority",
        ),
        Index("idx_complaints_created_at", desc("created_at")),
    )

    def __repr__(self) -> str:
        return (
            f"<Complaint(id={self.id}, title={self.title}, status={self.status}, "
            f"priority={self.priority}, submitter_id={self.submitter_id})>"
        )


class ComplaintResponse(Base):
    """
    ComplaintResponse model representing an admin reply on a complaint.

    Attributes:
        id: Unique identifier (UUID)
        complaint_id: Foreign key to the related complaint
        admin_id: Foreign key to the admin user posting the response
        text: Response body text
        created_at: Response creation timestamp
    """

    __tablename__ = "complaint_responses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    admin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return (
            f"<ComplaintResponse(id={self.id}, complaint_id={self.complaint_id}, "
            f"admin_id={self.admin_id})>"
        )


class Activity(Base):
    """
    Activity model representing a recent platform event.

    Notes:
        The database column is named ``metadata`` to match the specification.
        The Python attribute is ``metadata_`` because ``metadata`` is reserved
        by SQLAlchemy's declarative base.

    Attributes:
        id: Unique identifier (UUID)
        type: Activity event type
        user_id: Foreign key to the related user
        entity_id: Optional UUID for the related resource
        metadata_: Event metadata payload stored as JSON
        created_at: Activity creation timestamp
    """

    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        default=None,
    )

    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
        default=None,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    __table_args__ = (
        CheckConstraint(
            "type IN ('note_upload', 'user_registration', 'high_rating')",
            name="check_activity_type",
        ),
        Index("idx_activities_created_at", desc("created_at")),
    )

    def __repr__(self) -> str:
        return (
            f"<Activity(id={self.id}, type={self.type}, user_id={self.user_id}, "
            f"entity_id={self.entity_id})>"
        )
