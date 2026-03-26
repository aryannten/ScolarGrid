"""Backfill cached average_rating and decimal score values for existing users."""

from __future__ import annotations

import logging

from app.core.database import SessionLocal
from app.models.user import User
from app.services.scoring_service import batch_recalculate_scores


logger = logging.getLogger("scholargrid.scripts.recalculate_scores")


def recalculate_all_user_scores(batch_size: int = 100) -> int:
    """Recalculate scores for all student users and log progress."""
    db = SessionLocal()
    try:
        total_students = db.query(User).filter(User.role == "student").count()
        processed = 0

        student_ids = [
            row[0]
            for row in db.query(User.id)
            .filter(User.role == "student")
            .order_by(User.created_at.asc())
            .all()
        ]

        for start in range(0, len(student_ids), batch_size):
            current_ids = student_ids[start:start + batch_size]
            updated = batch_recalculate_scores(db, current_ids, batch_size=batch_size)
            processed += updated

            if processed % 100 == 0 or processed == total_students:
                logger.info("Recalculated scores for %s/%s students", processed, total_students)

        return processed
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    total = recalculate_all_user_scores()
    logger.info("Completed score recalculation for %s students", total)
