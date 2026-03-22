"""
Activity feed routes for ScholarGrid Backend API
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.complaint import Activity
from app.schemas.schemas import ActivityResponse, ActivityListResponse

router = APIRouter(prefix="/activity", tags=["Activity Feed"])


@router.get("", response_model=ActivityListResponse)
def get_activity_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recent platform activity from the past 30 days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    query = db.query(Activity).filter(Activity.created_at >= cutoff).order_by(Activity.created_at.desc())
    total = query.count()
    activities = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for act in activities:
        actor = db.query(User).filter(User.id == act.user_id).first()
        items.append(ActivityResponse(
            id=act.id,
            type=act.type,
            user_id=act.user_id,
            user_name=actor.name if actor else None,
            entity_id=act.entity_id,
            entity_title=act.metadata_.get("title") if act.metadata_ else None,
            metadata=act.metadata_,
            created_at=act.created_at,
        ))

    return ActivityListResponse(
        activities=items, total=total, page=page, page_size=page_size,
    )
