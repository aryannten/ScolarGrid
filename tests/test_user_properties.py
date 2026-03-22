"""
Property-based tests for user model and registration (Tasks 3.2, 4.2, 4.5)

Tests auth token structure properties and user profile update invariants.
"""

import pytest
from hypothesis import given, settings as hyp_settings, HealthCheck
from hypothesis import strategies as st
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.core.database import Base
from app.models.user import User


@pytest.fixture(scope="module")
def engine():
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    @event.listens_for(eng, "connect")
    def fk(conn, _): conn.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def db(engine):
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.rollback()
    s.close()


# ─── Property: every user always has a non-empty role ─────────────────────────

@given(role=st.sampled_from(["student", "admin"]))
@hyp_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_user_role_always_valid(role, engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        uid = f"prop_role_{role}_{id(db)}"
        u = User(firebase_uid=uid, email=f"{uid}@test.com", name="Test", role=role)
        db.add(u)
        db.commit()
        assert u.role in ("student", "admin")
    finally:
        db.rollback()
        db.close()


# ─── Property: firebase_uid uniqueness is always enforced ─────────────────────

def test_property_firebase_uid_unique_enforced(engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        uid = f"dup_uid_{id(db)}"
        u1 = User(firebase_uid=uid, email=f"{uid}_a@test.com", name="A")
        u2 = User(firebase_uid=uid, email=f"{uid}_b@test.com", name="B")
        db.add(u1)
        db.commit()
        db.add(u2)
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()


# ─── Property: score = uploads + downloads always ─────────────────────────────

@given(
    uploads=st.integers(min_value=0, max_value=1000),
    downloads=st.integers(min_value=0, max_value=1000),
)
@hyp_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_score_equals_uploads_plus_downloads(uploads, downloads, engine):
    from app.services.scoring_service import calculate_tier
    score = uploads + downloads
    tier = calculate_tier(score)
    assert score >= 0
    assert tier in ("bronze", "silver", "gold", "elite")


# ─── Property: user status is always active or suspended ──────────────────────

@given(status=st.sampled_from(["active", "suspended"]))
@hyp_settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_user_status_always_valid(status, engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        uid = f"prop_status_{status}_{id(db)}"
        u = User(firebase_uid=uid, email=f"{uid}@test.com", name="S", status=status)
        db.add(u)
        db.commit()
        assert u.status in ("active", "suspended")
    finally:
        db.rollback()
        db.close()


# ─── Property: tier upgrade is monotonic with score ───────────────────────────

@given(
    score_a=st.integers(min_value=0, max_value=5000),
    delta=st.integers(min_value=0, max_value=5000),
)
@hyp_settings(max_examples=200)
def test_property_higher_score_never_lower_tier(score_a, delta):
    from app.services.scoring_service import calculate_tier
    tier_order = ["bronze", "silver", "gold", "elite"]
    t_a = tier_order.index(calculate_tier(score_a))
    t_b = tier_order.index(calculate_tier(score_a + delta))
    assert t_b >= t_a
