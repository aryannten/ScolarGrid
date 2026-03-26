"""
Integration and unit tests for rating-based scoring.
"""

from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.orm import sessionmaker

from app.schemas.schemas import (
    LeaderboardEntry,
    LeaderboardResponse,
    NoteRatingBreakdown,
    ScoreDetailsResponse,
    UserProfileResponse,
)
from app.services.scoring_service import batch_recalculate_scores, recalculate_on_note_status_change, update_user_score_and_tier
from scripts.recalculate_scores import recalculate_all_user_scores


def test_rating_creation_triggers_score_recalculation(client, approved_note, db_session, student_user):
    response = client.post(f"/api/v1/notes/{approved_note.id}/rate", json={"rating": 5})
    assert response.status_code == 200

    db_session.refresh(student_user)
    db_session.refresh(approved_note)
    assert approved_note.average_rating == Decimal("5.00")
    assert student_user.average_rating == Decimal("5.00")
    assert student_user.score == Decimal("5.00")


def test_note_approval_triggers_score_recalculation(admin_client, pending_note, db_session, student_user):
    pending_note.average_rating = Decimal("4.00")
    pending_note.rating_count = 1
    db_session.commit()

    response = admin_client.put(f"/api/v1/notes/{pending_note.id}/approve")
    assert response.status_code == 200

    db_session.refresh(student_user)
    assert student_user.average_rating == Decimal("4.00")
    assert student_user.score == Decimal("4.00")


def test_note_rejection_triggers_score_recalculation(admin_client, approved_note, db_session, student_user):
    approved_note.average_rating = Decimal("4.50")
    approved_note.rating_count = 3
    db_session.commit()
    recalculate_on_note_status_change(student_user.id, db_session)

    response = admin_client.put(
        f"/api/v1/notes/{approved_note.id}/reject",
        json={"reason": "No longer approved"},
    )
    assert response.status_code == 200

    db_session.refresh(student_user)
    assert student_user.average_rating == Decimal("0.00")
    assert student_user.score == Decimal("0.00")


def test_note_deletion_triggers_score_recalculation(admin_client, approved_note, db_session, student_user):
    approved_note.average_rating = Decimal("3.25")
    approved_note.rating_count = 2
    db_session.commit()
    recalculate_on_note_status_change(student_user.id, db_session)

    with patch("app.services.cloudinary_storage.delete_file_from_storage", new_callable=AsyncMock):
        response = admin_client.delete(f"/api/v1/notes/{approved_note.id}")

    assert response.status_code == 204
    db_session.refresh(student_user)
    assert student_user.average_rating == Decimal("0.00")
    assert student_user.score == Decimal("0.00")


def test_profile_and_leaderboard_include_score_breakdown(client, approved_note, db_session, student_user):
    approved_note.average_rating = Decimal("4.25")
    approved_note.rating_count = 2
    db_session.commit()
    recalculate_on_note_status_change(student_user.id, db_session)

    profile = client.get("/api/v1/auth/me")
    leaderboard = client.get("/api/v1/leaderboard")

    assert profile.status_code == 200
    assert leaderboard.status_code == 200
    assert "average_rating" in profile.json()
    assert "score" in profile.json()
    assert "average_rating" in leaderboard.json()["rankings"][0]


def test_score_details_endpoint_returns_breakdown(admin_client, approved_note, db_session, student_user):
    approved_note.average_rating = Decimal("4.25")
    approved_note.rating_count = 2
    db_session.commit()
    recalculate_on_note_status_change(student_user.id, db_session)

    response = admin_client.get(f"/api/v1/admin/users/{student_user.id}/score-details")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(student_user.id)
    assert data["average_rating"] == 4.25
    assert data["approved_notes_with_ratings_count"] == 1
    assert data["note_ratings"][0]["average_rating"] == 4.25


def test_score_details_endpoint_requires_admin(client, student_user):
    response = client.get(f"/api/v1/admin/users/{student_user.id}/score-details")
    assert response.status_code == 403


def test_score_details_endpoint_handles_missing_user(admin_client):
    response = admin_client.get(f"/api/v1/admin/users/{uuid4()}/score-details")
    assert response.status_code == 404


def test_schema_serialization_for_score_breakdown():
    user = UserProfileResponse(
        id=uuid4(),
        email="student@test.com",
        name="Student",
        role="student",
        status="active",
        score=Decimal("12.34"),
        average_rating=Decimal("4.25"),
        tier="bronze",
        uploads_count=5,
        downloads_count=3,
        created_at="2026-03-26T00:00:00Z",
    )
    leaderboard = LeaderboardResponse(
        rankings=[
            LeaderboardEntry(
                rank=1,
                user_id=uuid4(),
                name="Student",
                avatar_url=None,
                score=Decimal("12.34"),
                average_rating=Decimal("4.25"),
                tier="bronze",
                uploads_count=5,
                downloads_count=3,
            )
        ],
        total=1,
        page=1,
        page_size=50,
    )
    details = ScoreDetailsResponse(
        user_id=uuid4(),
        name="Student",
        uploads_count=5,
        downloads_count=3,
        average_rating=Decimal("4.25"),
        approved_notes_with_ratings_count=1,
        note_ratings=[
            NoteRatingBreakdown(
                note_id=uuid4(),
                title="Rated Note",
                average_rating=Decimal("4.25"),
                rating_count=2,
            )
        ],
        score=Decimal("12.34"),
        tier="bronze",
    )

    assert user.model_dump(mode="json")["score"] == 12.34
    assert leaderboard.model_dump(mode="json")["rankings"][0]["average_rating"] == 4.25
    assert details.model_dump(mode="json")["note_ratings"][0]["average_rating"] == 4.25


def test_score_update_invalidates_cache_keys(db_session, student_user):
    student_user.uploads_count = 1000

    with patch("app.services.redis_service.invalidate_pattern") as mock_invalidate:
        with patch("app.services.redis_service.delete_cache") as mock_delete:
            update_user_score_and_tier(student_user, db_session, commit=False)

    mock_invalidate.assert_any_call("leaderboard:*")
    mock_delete.assert_called_with(f"user:profile:{student_user.id}")
    mock_invalidate.assert_any_call("leaderboard:tier:bronze:*")
    mock_invalidate.assert_any_call("leaderboard:tier:silver:*")


def test_cache_invalidation_failures_do_not_block_score_updates(db_session, student_user):
    student_user.uploads_count = 10

    with patch("app.services.redis_service.invalidate_pattern", side_effect=RuntimeError("redis down")):
        with patch("app.services.redis_service.delete_cache", side_effect=RuntimeError("redis down")):
            update_user_score_and_tier(student_user, db_session, commit=False)

    assert student_user.score == Decimal("10.00")
    assert student_user.tier == "bronze"


def test_batch_recalculate_scores_preserves_counts_and_initializes_average_rating(db_session, student_user):
    student_user.uploads_count = 7
    student_user.downloads_count = 9
    student_user.average_rating = Decimal("5.00")
    student_user.score = Decimal("21.00")
    db_session.commit()

    updated = batch_recalculate_scores(db_session, [student_user.id])
    db_session.refresh(student_user)

    assert updated == 1
    assert student_user.uploads_count == 7
    assert student_user.downloads_count == 9
    assert student_user.average_rating == Decimal("0.00")
    assert student_user.score == Decimal("16.00")


def test_recalculate_script_handles_users_with_no_notes(test_engine):
    from app.models.user import User

    SessionLocal = sessionmaker(bind=test_engine)
    setup_session = SessionLocal()
    try:
        student_user = User(
            firebase_uid=f"script_user_{uuid4().hex}",
            email=f"script_user_{uuid4().hex[:8]}@test.com",
            name="Script User",
            role="student",
            uploads_count=4,
            downloads_count=6,
        )
        setup_session.add(student_user)
        setup_session.commit()
        user_id = student_user.id
    finally:
        setup_session.close()

    with patch("scripts.recalculate_scores.SessionLocal", SessionLocal):
        updated = recalculate_all_user_scores(batch_size=50)

    fresh_session = SessionLocal()
    try:
        refreshed_user = fresh_session.get(User, user_id)
        assert updated >= 1
        assert refreshed_user.average_rating == Decimal("0.00")
        assert refreshed_user.score == Decimal("10.00")
    finally:
        fresh_session.close()
