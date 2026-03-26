"""
SQLAlchemy ORM model for Rating entity

This module defines the Rating model representing user ratings of notes.
"""

from sqlalchemy import Integer, TIMESTAMP, CheckConstraint, Index, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class Rating(Base):
    """
    Rating model representing user ratings of notes.
    
    Attributes:
        id: Unique identifier (UUID)
        note_id: Foreign key to notes table
        user_id: Foreign key to users table
        rating: Rating value (1-5 stars)
        created_at: Rating creation timestamp
        updated_at: Last rating update timestamp
    """
    
    __tablename__ = "ratings"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign keys
    note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Rating value
    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False
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
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="check_rating_value"
        ),
        UniqueConstraint("note_id", "user_id", name="uq_rating_note_user"),
    )
    
    def __repr__(self) -> str:
        return f"<Rating(id={self.id}, note_id={self.note_id}, user_id={self.user_id}, rating={self.rating})>"
