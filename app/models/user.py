"""
SQLAlchemy ORM model for User entity

This module defines the User model representing both students and admins.
"""

from sqlalchemy import String, Integer, Text, TIMESTAMP, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class User(Base):
    """
    User model representing both students and admins in the system.
    
    Attributes:
        id: Unique identifier (UUID)
        firebase_uid: Firebase authentication UID (unique)
        email: User email address (unique)
        name: User display name
        role: User role (student or admin)
        avatar_url: URL to user's avatar image in Firebase Storage
        about: User bio/description text
        status: Account status (active or suspended)
        score: Student activity score (uploads_count + downloads_count)
        tier: Student tier level (bronze, silver, gold, elite)
        uploads_count: Number of notes uploaded by student
        downloads_count: Number of notes downloaded by student
        created_at: Account creation timestamp
        updated_at: Last profile update timestamp
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Authentication fields
    firebase_uid: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Profile fields
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="student"
    )
    
    avatar_url: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        default=None
    )
    
    about: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        default=None
    )
    
    # Status field
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active"
    )
    
    # Student statistics
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        index=True
    )
    
    tier: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="bronze",
        index=True
    )
    
    uploads_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    
    downloads_count: Mapped[int] = mapped_column(
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
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "role IN ('student', 'admin')",
            name="check_user_role"
        ),
        CheckConstraint(
            "status IN ('active', 'suspended')",
            name="check_user_status"
        ),
        CheckConstraint(
            "tier IN ('bronze', 'silver', 'gold', 'elite')",
            name="check_user_tier"
        ),
        # Additional indexes for score (descending) and role
        Index("idx_users_score", "score", postgresql_ops={"score": "DESC"}),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role}, tier={self.tier})>"
