"""
SQLAlchemy ORM model for Note entity

This module defines the Note model representing uploaded educational materials.
"""

from sqlalchemy import String, Integer, Text, TIMESTAMP, CheckConstraint, Index, DECIMAL, BigInteger, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
import uuid

from app.core.database import Base


class Note(Base):
    """
    Note model representing uploaded educational documents.
    
    Attributes:
        id: Unique identifier (UUID)
        title: Note title
        description: Detailed description of the note content
        subject: Academic subject category
        tags: JSON array of tags for categorization
        file_url: Firebase Storage URL for the uploaded file
        file_name: Original filename
        file_size: File size in bytes
        file_type: MIME type or file extension
        uploader_id: Foreign key to users table
        status: Approval status (pending, approved, rejected)
        rejection_reason: Admin's reason for rejection (if rejected)
        download_count: Number of times the note has been downloaded
        average_rating: Average rating from 1-5 stars
        rating_count: Total number of ratings received
        upload_date: Timestamp when note was uploaded
        status_updated_at: Timestamp when status was last changed
        updated_at: Last modification timestamp
    """
    
    __tablename__ = "notes"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Note metadata
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    subject: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    
    # Tags are stored as a JSON array for flexible querying and transport.
    tags: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=True,
        default=None
    )
    
    # File information
    file_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )
    
    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    # Foreign key to users
    uploader_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Moderation fields
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True
    )
    
    rejection_reason: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        default=None
    )
    
    # Statistics
    download_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    
    average_rating: Mapped[Decimal] = mapped_column(
        DECIMAL(3, 2),
        nullable=True,
        default=None
    )
    
    rating_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    
    # Timestamps
    upload_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    
    status_updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Table constraints and indexes
    # Note: Additional indexes (average_rating, upload_date, tags GIN, full-text search)
    # will be created via Alembic migrations for PostgreSQL production database
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="check_note_status"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Note(id={self.id}, title={self.title}, status={self.status}, uploader_id={self.uploader_id})>"
