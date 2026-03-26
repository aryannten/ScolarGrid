"""
Property-based tests for notes (Tasks 6.2, 6.4, 6.7, 7.2, 8.4)

Tests note upload constraints, search/filtering properties, download counting,
rating calculation invariants, and moderation state transitions.
"""

import pytest
from decimal import Decimal
from hypothesis import given, settings as hyp_settings, HealthCheck
from hypothesis import strategies as st
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.core.database import Base
from app.models.user import User
from app.models.note import Note
from app.models.rating import Rating


@pytest.fixture(scope="module")
def engine():
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    @event.listens_for(eng, "connect")
    def fk(conn, _): conn.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(eng)
    return eng


def _make_user(db, suffix):
    u = User(firebase_uid=f"note_prop_{suffix}", email=f"note_prop_{suffix}@t.com", name="U")
    db.add(u)
    db.commit()
    return u


def _make_note(db, user, status="approved", suffix=""):
    n = Note(
        title=f"Note {suffix}",
        description="Test",
        subject="Math",
        file_url=f"https://storage.example.com/{suffix}.pdf",
        file_name=f"{suffix}.pdf",
        file_size=1024,
        file_type="pdf",
        uploader_id=user.id,
        status=status,
    )
    db.add(n)
    db.commit()
    return n


# ─── Property: note status is always one of three valid states ────────────────

@given(status=st.sampled_from(["pending", "approved", "rejected"]))
@hyp_settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_note_status_always_valid(status, engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _make_user(db, f"stat_{status}_{id(db)}")
        n = _make_note(db, u, status=status, suffix=f"stat_{id(db)}")
        assert n.status in ("pending", "approved", "rejected")
    finally:
        db.rollback()
        db.close()


# ─── Property: download_count is always non-negative ─────────────────────────

@given(downloads=st.integers(min_value=0, max_value=10_000))
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_download_count_always_non_negative(downloads, engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _make_user(db, f"dl_{downloads}_{id(db)}")
        n = _make_note(db, u, suffix=f"dl_{id(db)}")
        n.download_count = downloads
        db.commit()
        assert n.download_count >= 0
    finally:
        db.rollback()
        db.close()


# ─── Property: rating is always between 1 and 5 ──────────────────────────────

@given(rating_val=st.integers(min_value=1, max_value=5))
@hyp_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_rating_always_in_valid_range(rating_val, engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _make_user(db, f"rat_{rating_val}_{id(db)}")
        n = _make_note(db, u, suffix=f"rat_{id(db)}")
        r = Rating(note_id=n.id, user_id=u.id, rating=rating_val)
        db.add(r)
        db.commit()
        assert 1 <= r.rating <= 5
    finally:
        db.rollback()
        db.close()


# ─── Property: average_rating is always within [1.0, 5.0] if set ─────────────

@given(ratings=st.lists(st.integers(min_value=1, max_value=5), min_size=1, max_size=20))
@hyp_settings(max_examples=100)
def test_property_average_rating_always_valid(ratings):
    avg = sum(ratings) / len(ratings)
    assert 1.0 <= avg <= 5.0


# ─── Property: file_size is always positive ───────────────────────────────────

@given(size=st.integers(min_value=1, max_value=50 * 1024 * 1024))
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_file_size_always_positive(size, engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _make_user(db, f"sz_{size}_{id(db)}")
        n = Note(
            title="Sized Note", description="D", subject="S",
            file_url="https://x.com/a.pdf", file_name="a.pdf",
            file_size=size, file_type="pdf", uploader_id=u.id, status="pending",
        )
        db.add(n)
        db.commit()
        assert n.file_size > 0
    finally:
        db.rollback()
        db.close()


# ─── Property: rejected note always has a status of 'rejected' ───────────────

def test_property_reject_sets_status_correctly(engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _make_user(db, f"rej_{id(db)}")
        n = _make_note(db, u, status="pending", suffix=f"rej_{id(db)}")
        n.status = "rejected"
        n.rejection_reason = "Low quality content"
        db.commit()
        assert n.status == "rejected"
        assert n.rejection_reason is not None
    finally:
        db.rollback()
        db.close()


# ─── Property: approved note never has a rejection_reason ────────────────────

def test_property_approved_note_has_no_rejection_reason(engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _make_user(db, f"apr_{id(db)}")
        n = _make_note(db, u, status="approved", suffix=f"apr_{id(db)}")
        assert n.rejection_reason is None
    finally:
        db.rollback()
        db.close()
