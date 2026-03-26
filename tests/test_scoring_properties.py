"""
Property-based and edge-case tests for rating-based scoring.

These tests cover the seven spec properties plus the critical edge cases
called out in the scoring tasks.
"""

from decimal import Decimal, ROUND_HALF_UP
import uuid
from unittest.mock import patch

import pytest
from hypothesis import given, settings as hyp_settings, HealthCheck
from hypothesis import strategies as st
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.note import Note
from app.models.user import User
from app.services.scoring_service import (
    calculate_average_rating_of_student_notes,
    calculate_tier,
    quantize_decimal,
    recalculate_on_note_status_change,
    recalculate_on_rating_change,
    update_user_score_and_tier,
)


TWOPLACES = Decimal("0.01")


def _mean(values: list[Decimal]) -> Decimal:
    return (sum(values) / Decimal(len(values))).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


@pytest.fixture(scope="module")
def engine():
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    @event.listens_for(eng, "connect")
    def enable_fk(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def db(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(autouse=True)
def disable_cache_invalidation(monkeypatch):
    monkeypatch.setattr("app.services.scoring_service._invalidate_score_caches", lambda *args, **kwargs: None)


def _make_user(db, *, uploads_count: int = 0, downloads_count: int = 0, average_rating: Decimal = Decimal("0.00")) -> User:
    user = User(
        firebase_uid=f"score_prop_{uuid.uuid4().hex}",
        email=f"score_prop_{uuid.uuid4().hex[:8]}@test.com",
        name="Scoring Test User",
        role="student",
        uploads_count=uploads_count,
        downloads_count=downloads_count,
        average_rating=average_rating,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_note(
    db,
    user: User,
    *,
    status: str = "approved",
    average_rating: Decimal | None = None,
    suffix: str | None = None,
) -> Note:
    label = suffix or uuid.uuid4().hex[:8]
    note = Note(
        title=f"Note {label}",
        description="Scoring test note",
        subject="Mathematics",
        tags=["scores"],
        file_url=f"https://storage.example.com/{label}.pdf",
        file_name=f"{label}.pdf",
        file_size=1024,
        file_type="pdf",
        uploader_id=user.id,
        status=status,
        average_rating=average_rating,
        rating_count=1 if average_rating is not None else 0,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


rating_values = st.lists(
    st.decimals(min_value=Decimal("1.00"), max_value=Decimal("5.00"), places=2),
    min_size=1,
    max_size=20,
)


# Property 1: Average Rating Calculation Correctness
@given(ratings=rating_values)
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_average_rating_calculation_correctness(ratings, db):
    user = _make_user(db)
    for idx, rating in enumerate(ratings):
        _make_note(db, user, average_rating=rating, suffix=f"approved_{idx}")

    _make_note(db, user, status="pending", average_rating=Decimal("5.00"), suffix="pending")
    _make_note(db, user, status="approved", average_rating=None, suffix="unrated")

    assert calculate_average_rating_of_student_notes(user.id, db) == _mean(list(ratings))


# Property 2: Score Formula Correctness
@given(
    uploads=st.integers(min_value=0, max_value=5000),
    downloads=st.integers(min_value=0, max_value=5000),
    average_rating=st.decimals(min_value=Decimal("0.00"), max_value=Decimal("5.00"), places=2),
)
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_score_formula_correctness(uploads, downloads, average_rating, db):
    user = _make_user(db, uploads_count=uploads, downloads_count=downloads, average_rating=average_rating)
    update_user_score_and_tier(user, db, commit=False)

    expected = quantize_decimal(Decimal(uploads) + Decimal(downloads) + average_rating)
    assert user.score == expected


# Property 3: Score Precision
@given(
    uploads=st.integers(min_value=0, max_value=5000),
    downloads=st.integers(min_value=0, max_value=5000),
    average_rating=st.decimals(min_value=Decimal("0.00"), max_value=Decimal("5.00"), places=2),
)
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_score_precision(uploads, downloads, average_rating, db):
    user = _make_user(db, uploads_count=uploads, downloads_count=downloads, average_rating=average_rating)
    update_user_score_and_tier(user, db, commit=False)
    assert user.score.as_tuple().exponent >= -2


# Property 4: Debouncing Behavior
@given(call_count=st.integers(min_value=1, max_value=20))
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_debouncing_behavior(call_count, db):
    user = _make_user(db)
    _make_note(db, user, average_rating=Decimal("4.00"))

    debounce_values = [True] + [False] * max(call_count - 1, 0)
    with patch("app.services.scoring_service._mark_debounce", side_effect=debounce_values):
        with patch(
            "app.services.scoring_service.calculate_average_rating_of_student_notes",
            return_value=Decimal("4.00"),
        ) as mock_calc:
            for _ in range(call_count):
                recalculate_on_rating_change(user.id, db)

    assert mock_calc.call_count <= 1


# Property 5: Tier Assignment Correctness
@given(score=st.decimals(min_value=Decimal("0.00"), max_value=Decimal("5000.00"), places=2))
@hyp_settings(max_examples=100)
def test_property_tier_assignment_correctness(score):
    if score < Decimal("1000.00"):
        assert calculate_tier(score) == "bronze"
    elif score < Decimal("2000.00"):
        assert calculate_tier(score) == "silver"
    elif score < Decimal("3000.00"):
        assert calculate_tier(score) == "gold"
    else:
        assert calculate_tier(score) == "elite"


# Property 6: Average Rating Precision
@given(value=st.decimals(min_value=Decimal("0.00"), max_value=Decimal("5.00"), places=2))
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_average_rating_precision(value, db):
    user = _make_user(db, average_rating=value)
    assert Decimal("0.00") <= user.average_rating <= Decimal("5.00")
    assert user.average_rating.as_tuple().exponent >= -2


# Property 7: Status Changes Affect Average Rating
@given(
    approved_rating=st.decimals(min_value=Decimal("1.00"), max_value=Decimal("5.00"), places=2),
    second_rating=st.decimals(min_value=Decimal("1.00"), max_value=Decimal("5.00"), places=2),
)
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_status_changes_affect_average_rating(approved_rating, second_rating, db):
    user = _make_user(db)
    first_note = _make_note(db, user, status="approved", average_rating=approved_rating, suffix="first")
    second_note = _make_note(db, user, status="rejected", average_rating=second_rating, suffix="second")

    recalculate_on_note_status_change(user.id, db)
    db.refresh(user)
    assert user.average_rating == quantize_decimal(approved_rating)

    second_note.status = "approved"
    db.commit()
    recalculate_on_note_status_change(user.id, db)
    db.refresh(user)
    assert user.average_rating == _mean([approved_rating, second_rating])

    first_note.status = "rejected"
    db.commit()
    recalculate_on_note_status_change(user.id, db)
    db.refresh(user)
    assert user.average_rating == quantize_decimal(second_rating)


def test_student_with_no_approved_notes_gets_zero_average_rating(db):
    user = _make_user(db)
    _make_note(db, user, status="pending", average_rating=Decimal("5.00"))

    assert calculate_average_rating_of_student_notes(user.id, db) == Decimal("0.00")


def test_student_with_approved_notes_but_no_ratings_gets_zero_average_rating(db):
    user = _make_user(db)
    _make_note(db, user, status="approved", average_rating=None)

    assert calculate_average_rating_of_student_notes(user.id, db) == Decimal("0.00")


def test_single_one_star_note_is_counted(db):
    user = _make_user(db)
    _make_note(db, user, status="approved", average_rating=Decimal("1.00"))

    recalculate_on_note_status_change(user.id, db)
    db.refresh(user)
    assert user.average_rating == Decimal("1.00")
    assert user.score == Decimal("1.00")


@pytest.mark.parametrize(
    ("score", "tier"),
    [
        (Decimal("999.99"), "bronze"),
        (Decimal("1000.00"), "silver"),
        (Decimal("1999.99"), "silver"),
        (Decimal("2000.00"), "gold"),
        (Decimal("2999.99"), "gold"),
        (Decimal("3000.00"), "elite"),
    ],
)
def test_exact_tier_boundaries(score, tier):
    assert calculate_tier(score) == tier
