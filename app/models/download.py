"""
SQLAlchemy ORM model for Download entity

This module defines the Download model representing note download tracking.
"""

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class Download(Base):
    """
    Download model representing note download tracking.
    
    Attributes:
        id: Unique identifier (UUID)
        note_id: Foreign key to notes table
        user_id: Foreign key to users table
        downloaded_at: Download timestamp
    """
    
    __tablename__ = "downloads"
    
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
    
    # Timestamp
    downloaded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    
    def __repr__(self) -> str:
        return f"<Download(id={self.id}, note_id={self.note_id}, user_id={self.user_id}, downloaded_at={self.downloaded_at})>"
