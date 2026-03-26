"""
Activity tracking service for ScholarGrid Backend API
"""

from sqlalchemy.orm import Session
from uuid import UUID
from app.models.complaint import Activity


def create_activity(
    db: Session,
    activity_type: str,
    user_id: UUID,
    entity_id: UUID = None,
    entity_title: str = None,
    metadata: dict = None,
) -> Activity:
    """Create an activity record."""
    activity = Activity(
        type=activity_type,
        user_id=user_id,
        entity_id=entity_id,
        metadata_=metadata or {},
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity
