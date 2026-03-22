"""
Leaderboard routes for ScholarGrid Backend API
"""

import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.schemas import LeaderboardResponse, LeaderboardEntry

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

LEADERBOARD_TTL = 300  # 5 minutes


@router.get("", response_model=LeaderboardResponse)
def get_leaderboard(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get ranked students by score (descending). Ties broken by earliest created_at."""
    cache_key = f"leaderboard:page:{page}:size:{page_size}"
    try:
        from app.services.redis_service import get_cache, set_cache
        cached = get_cache(cache_key)
        if cached:
            return cached
    except Exception:
        pass

    query = db.query(User).filter(User.role == "student").order_by(
        User.score.desc(), User.created_at.asc()
    )
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()

    offset = (page - 1) * page_size
    rankings = [
        LeaderboardEntry(
            rank=offset + i + 1,
            user_id=u.id,
            name=u.name,
            avatar_url=u.avatar_url,
            score=u.score,
            tier=u.tier,
            uploads_count=u.uploads_count,
            downloads_count=u.downloads_count,
        )
        for i, u in enumerate(users)
    ]

    result = LeaderboardResponse(rankings=rankings, total=total, page=page, page_size=page_size)

    try:
        from app.services.redis_service import set_cache
        set_cache(cache_key, result.model_dump(mode="json"), ttl=LEADERBOARD_TTL)
    except Exception:
        pass

    return result
