"""
Integration tests for chat system (Task 29.3)

Tests chat group creation, join, listing, deletion cascade,
and message history retrieval.
"""

import pytest
from uuid import uuid4


# ─── Chat: create group ───────────────────────────────────────────────────────

def test_create_chat_group(client):
    response = client.post("/api/v1/chat/groups", json={
        "name": "Physics Study Group",
        "description": "For physics students"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Physics Study Group"
    assert len(data["join_code"]) == 8
    assert data["member_count"] == 1


# ─── Chat: join group with valid code ────────────────────────────────────────

def test_join_group_with_valid_code(client, chat_group, second_student, db_session):
    # Switch client to second_student
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.database import get_db
    from app.core.auth import get_current_user

    def override_db():
        yield db_session

    async def override_user():
        return second_student

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user

    with TestClient(app) as c:
        response = c.post("/api/v1/chat/groups/join", json={"join_code": chat_group.join_code})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(chat_group.id)


# ─── Chat: join with invalid code returns 404 ────────────────────────────────

def test_join_group_invalid_code_returns_404(client):
    response = client.post("/api/v1/chat/groups/join", json={"join_code": "XXXXXXXX"})
    assert response.status_code == 404


# ─── Chat: list user's groups ─────────────────────────────────────────────────

def test_list_chat_groups(client, chat_group):
    response = client.get("/api/v1/chat/groups")
    assert response.status_code == 200
    data = response.json()
    assert "groups" in data
    ids = [g["id"] for g in data["groups"]]
    assert str(chat_group.id) in ids


# ─── Chat: get message history ────────────────────────────────────────────────

def test_get_message_history(client, chat_group):
    response = client.get(f"/api/v1/chat/groups/{chat_group.id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert "total" in data


# ─── Chat: non-member cannot get message history ─────────────────────────────

def test_non_member_cannot_view_messages(client, db_session, admin_user):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.database import get_db
    from app.core.auth import get_current_user
    from app.models.chat import ChatGroup

    new_group = ChatGroup(
        name="Private Group", join_code="PRIV1234", creator_id=admin_user.id, member_count=1
    )
    db_session.add(new_group)
    db_session.commit()

    # client is student who is NOT a member of new_group
    response = client.get(f"/api/v1/chat/groups/{new_group.id}/messages")
    assert response.status_code == 403


# ─── Chat: delete own group ───────────────────────────────────────────────────

def test_creator_can_delete_group(client, db_session, student_user):
    from app.models.chat import ChatGroup, ChatMembership
    g = ChatGroup(name="Del Group", join_code="DEL12345", creator_id=student_user.id, member_count=1)
    db_session.add(g)
    db_session.flush()
    db_session.add(ChatMembership(group_id=g.id, user_id=student_user.id))
    db_session.commit()

    response = client.delete(f"/api/v1/chat/groups/{g.id}")
    assert response.status_code == 204
