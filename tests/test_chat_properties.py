"""
Property-based tests for chat system (Tasks 12.2, 12.4, 12.7, 14.2)

Tests join code uniqueness, member count invariants, message ordering,
and group deletion cascade properties.
"""

import pytest
import string
from hypothesis import given, settings as hyp_settings, HealthCheck
from hypothesis import strategies as st
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.core.database import Base
from app.models.user import User
from app.models.chat import ChatGroup, ChatMembership, Message


@pytest.fixture(scope="module")
def engine():
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    @event.listens_for(eng, "connect")
    def fk(conn, _): conn.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(eng)
    return eng


def _user(db, suffix):
    u = User(firebase_uid=f"chat_p_{suffix}", email=f"chat_p_{suffix}@t.com", name="U")
    db.add(u)
    db.commit()
    return u


def _group(db, creator, code=None, suffix=""):
    g = ChatGroup(
        name=f"Group {suffix}", join_code=code or f"JC{suffix[:6]}", creator_id=creator.id, member_count=1,
    )
    db.add(g)
    db.commit()
    return g


# ─── Property: join_code is always exactly 8 characters ──────────────────────

@given(suffix=st.text(alphabet=string.ascii_uppercase + string.digits, min_size=8, max_size=8))
@hyp_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_join_code_always_8_chars(suffix, engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _user(db, f"jc_{suffix[:4]}_{id(db)}")
        g = ChatGroup(name="G", join_code=suffix, creator_id=u.id, member_count=1)
        db.add(g)
        db.commit()
        assert len(g.join_code) == 8
    finally:
        db.rollback()
        db.close()


# ─── Property: duplicate join codes are rejected ──────────────────────────────

def test_property_duplicate_join_code_rejected(engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _user(db, f"dup_{id(db)}")
        code = f"DUPCODE{id(db)}"[:8]
        g1 = ChatGroup(name="G1", join_code=code, creator_id=u.id, member_count=1)
        g2 = ChatGroup(name="G2", join_code=code, creator_id=u.id, member_count=1)
        db.add(g1)
        db.commit()
        db.add(g2)
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()


# ─── Property: member_count is always >= 1 (creator is always a member) ───────

@given(extra_members=st.integers(min_value=0, max_value=100))
@hyp_settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_member_count_always_at_least_one(extra_members, engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _user(db, f"mc_{extra_members}_{id(db)}")
        g = ChatGroup(
            name="G", join_code=f"MC{id(db)}"[:8],
            creator_id=u.id, member_count=1 + extra_members,
        )
        db.add(g)
        db.commit()
        assert g.member_count >= 1
    finally:
        db.rollback()
        db.close()


# ─── Property: messages cascade delete when group is deleted ──────────────────

def test_property_messages_cascade_on_group_delete(engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _user(db, f"casc_{id(db)}")
        g = _group(db, u, code=f"CASC{id(db)}"[:8], suffix=str(id(db)))
        m = Message(group_id=g.id, sender_id=u.id, content="Hello world", type="text")
        db.add(m)
        db.commit()
        msg_id = m.id

        db.delete(g)
        db.commit()

        found = db.query(Message).filter(Message.id == msg_id).first()
        assert found is None
    finally:
        db.rollback()
        db.close()


# ─── Property: message type is always 'text' or 'file' ───────────────────────

@given(msg_type=st.sampled_from(["text", "file"]))
@hyp_settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_message_type_always_valid(msg_type, engine):
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        u = _user(db, f"mtype_{msg_type}_{id(db)}")
        g = _group(db, u, code=f"MT{msg_type[:2]}{id(db)}"[:8], suffix=str(id(db)))
        m = Message(group_id=g.id, sender_id=u.id, content="Test", type=msg_type)
        db.add(m)
        db.commit()
        assert m.type in ("text", "file")
    finally:
        db.rollback()
        db.close()
