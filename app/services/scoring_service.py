"""
Scoring service for ScholarGrid Backend API

Calculates user score (uploads + downloads) and assigns tier levels.
"""

from sqlalchemy.orm import Session
from app.models.user import User


TIER_THRESHOLDS = {
    "elite": 3000,
    "gold": 2000,
    "silver": 1000,
    "bronze": 0,
}


def calculate_tier(score: int) -> str:
    """Return tier string for a given score."""
    if score >= 3000:
        return "elite"
    elif score >= 2000:
        return "gold"
    elif score >= 1000:
        return "silver"
    return "bronze"


def update_user_score_and_tier(user: User, db: Session) -> User:
    """
    Recalculate and persist score and tier for a user.

    Score = uploads_count + downloads_count
    Tier is then set based on the score thresholds.

    Args:
        user: User ORM object (already reflects updated counts)
        db: Active database session

    Returns:
        User: Updated user object
    """
    new_score = user.uploads_count + user.downloads_count
    new_tier = calculate_tier(new_score)

    user.score = new_score
    user.tier = new_tier
    db.commit()
    db.refresh(user)

    # Invalidate leaderboard and user profile caches
    try:
        from app.services.redis_service import invalidate_pattern
        invalidate_pattern("leaderboard:*")
        invalidate_pattern(f"user:profile:{user.id}")
    except Exception:
        pass

    return user
