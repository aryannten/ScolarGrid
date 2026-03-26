"""
Scoring service for ScholarGrid Backend API.

Calculates cached user average ratings, total score, and tier assignments.
"""

from __future__ import annotations

import logging
import time
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.user import User


logger = logging.getLogger("scholargrid.scoring")

RATING_QUANTIZER = Decimal("0.01")
SCORE_QUANTIZER = Decimal("0.01")
ZERO_DECIMAL = Decimal("0.00")
DEBOUNCE_TTL_SECONDS = 60
PERFORMANCE_WARNING_MS = 200
TIER_CACHE_PREFIX = "leaderboard:tier"

TIER_THRESHOLDS = {
    "elite": Decimal("3000.00"),
    "gold": Decimal("2000.00"),
    "silver": Decimal("1000.00"),
    "bronze": Decimal("0.00"),
}


def quantize_decimal(value: Decimal | int | float | None) -> Decimal:
    """Normalize any score-related numeric value to two decimal places."""
    if value is None:
        return ZERO_DECIMAL
    if isinstance(value, Decimal):
        raw = value
    else:
        raw = Decimal(str(value))
    return raw.quantize(SCORE_QUANTIZER, rounding=ROUND_HALF_UP)


def calculate_tier(score: Decimal | int | float) -> str:
    """Return tier string for a given score."""
    normalized_score = quantize_decimal(score)
    if normalized_score >= TIER_THRESHOLDS["elite"]:
        return "elite"
    if normalized_score >= TIER_THRESHOLDS["gold"]:
        return "gold"
    if normalized_score >= TIER_THRESHOLDS["silver"]:
        return "silver"
    return "bronze"


def _log_slow_query(operation: str, user_id: UUID, started_at: float) -> None:
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    if duration_ms > PERFORMANCE_WARNING_MS:
        logger.warning(
            "Slow scoring query",
            extra={
                "operation": operation,
                "user_id": str(user_id),
                "duration_ms": duration_ms,
            },
        )


def _invalidate_score_caches(user_id: UUID, old_tier: str | None, new_tier: str | None) -> None:
    try:
        from app.services.redis_service import delete_cache, invalidate_pattern

        invalidate_pattern("leaderboard:*")
        delete_cache(f"user:profile:{user_id}")

        if old_tier and new_tier and old_tier != new_tier:
            invalidate_pattern(f"{TIER_CACHE_PREFIX}:{old_tier}:*")
            invalidate_pattern(f"{TIER_CACHE_PREFIX}:{new_tier}:*")
    except Exception:
        logger.debug("Cache invalidation skipped for user %s", user_id, exc_info=True)


def calculate_average_rating_of_student_notes(user_id: UUID, db: Session) -> Decimal:
    """
    Calculate the mean note average rating across approved notes for a student.

    Only approved notes with a non-null `average_rating` are included.
    Returns 0.00 when the user has no eligible notes.
    """
    started_at = time.perf_counter()
    try:
        user_exists = db.query(User.id).filter(User.id == user_id).first()
        if user_exists is None:
            raise ValueError(f"User {user_id} does not exist.")

        rating_totals = (
            db.query(
                func.coalesce(func.sum(Note.average_rating), 0),
                func.count(Note.id),
            )
            .filter(
                Note.uploader_id == user_id,
                Note.status == "approved",
                Note.average_rating.isnot(None),
            )
            .one()
        )

        rating_sum, rating_count = rating_totals
        if not rating_count:
            result = ZERO_DECIMAL
        else:
            result = quantize_decimal(Decimal(str(rating_sum)) / Decimal(rating_count))
        _log_slow_query("calculate_average_rating_of_student_notes", user_id, started_at)
        return result
    except SQLAlchemyError:
        logger.exception("Database failure while calculating average rating for user %s", user_id)
        raise


def update_user_score_and_tier(user: User, db: Session, *, commit: bool = True) -> User:
    """
    Recalculate and persist score and tier for a user.

    Score = uploads_count + downloads_count + average_rating
    """
    previous_tier = user.tier

    uploads = Decimal(user.uploads_count)
    downloads = Decimal(user.downloads_count)
    average_rating = quantize_decimal(user.average_rating)
    new_score = quantize_decimal(uploads + downloads + average_rating)
    new_tier = calculate_tier(new_score)

    user.average_rating = average_rating
    user.score = new_score
    user.tier = new_tier

    if commit:
        db.commit()
        db.refresh(user)

    _invalidate_score_caches(user.id, previous_tier, new_tier)
    return user


def _mark_debounce(user_id: UUID, ttl_seconds: int = DEBOUNCE_TTL_SECONDS) -> bool:
    """
    Mark a score recalculation debounce window.

    Returns True when recalculation should proceed. Returns False when a valid
    debounce marker already exists. Fails open if Redis is unavailable.
    """
    try:
        from app.services.redis_service import redis_client

        result = redis_client.client.set(
            f"score_recalc_debounce:{user_id}",
            "1",
            ex=ttl_seconds,
            nx=True,
        )
        return bool(result)
    except Exception:
        logger.debug("Redis debounce unavailable; recalculation will proceed", exc_info=True)
        return True


def recalculate_on_rating_change(user_id: UUID, db: Session) -> User | None:
    """Recalculate a student's cached average rating and score after rating changes."""
    if not _mark_debounce(user_id):
        return None

    started_at = time.perf_counter()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    user.average_rating = calculate_average_rating_of_student_notes(user_id, db)
    updated_user = update_user_score_and_tier(user, db)
    _log_slow_query("recalculate_on_rating_change", user_id, started_at)
    return updated_user


def recalculate_on_note_status_change(user_id: UUID, db: Session) -> User | None:
    """Recalculate a student's cached average rating and score after note status changes."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return None

        user.average_rating = calculate_average_rating_of_student_notes(user_id, db)
        return update_user_score_and_tier(user, db)
    except Exception:
        db.rollback()
        logger.exception("Failed to recalculate score after note status change for user %s", user_id)
        raise


def batch_recalculate_scores(
    db: Session,
    user_ids: Iterable[UUID] | None = None,
    *,
    batch_size: int = 100,
) -> int:
    """
    Recalculate scores for multiple students using batch updates.

    Returns the number of users updated.
    """
    user_query = db.query(User).filter(User.role == "student")
    if user_ids is not None:
        user_query = user_query.filter(User.id.in_(list(user_ids)))

    users = user_query.order_by(User.created_at.asc()).all()
    if not users:
        return 0

    user_id_list = [user.id for user in users]
    average_rows = (
        db.query(Note.uploader_id, func.avg(Note.average_rating))
        .filter(
            Note.uploader_id.in_(user_id_list),
            Note.status == "approved",
            Note.average_rating.isnot(None),
        )
        .group_by(Note.uploader_id)
        .all()
    )
    average_map = {row[0]: quantize_decimal(row[1]) for row in average_rows}

    total_updated = 0
    for start in range(0, len(users), batch_size):
        batch = users[start:start + batch_size]
        mappings = []
        for user in batch:
            average_rating = average_map.get(user.id, ZERO_DECIMAL)
            score = quantize_decimal(
                Decimal(user.uploads_count) + Decimal(user.downloads_count) + average_rating
            )
            tier = calculate_tier(score)

            mappings.append(
                {
                    "id": user.id,
                    "average_rating": average_rating,
                    "score": score,
                    "tier": tier,
                }
            )
            total_updated += 1

        db.bulk_update_mappings(User, mappings)
        db.commit()

        for user in batch:
            old_tier = user.tier
            new_tier = next(mapping["tier"] for mapping in mappings if mapping["id"] == user.id)
            _invalidate_score_caches(user.id, old_tier, new_tier)

    return total_updated
