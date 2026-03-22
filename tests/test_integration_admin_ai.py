"""
Integration tests for AI chatbot (Task 29.4) and admin features (Task 29.5)

Tests AI conversation management, daily rate limiting,
admin user management, complaint workflow, and activity feed.
"""

import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4


# ─── AI: usage stats always return valid structure ────────────────────────────

def test_ai_usage_returns_valid_structure(client):
    response = client.get("/api/v1/ai/usage")
    assert response.status_code == 200
    data = response.json()
    assert "daily_limit" in data
    assert "messages_today" in data
    assert "remaining_today" in data
    assert data["daily_limit"] == 50
    assert data["remaining_today"] >= 0


# ─── AI: list conversations (initially empty) ─────────────────────────────────

def test_ai_conversations_list_initially_empty(client):
    response = client.get("/api/v1/ai/conversations")
    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert isinstance(data["conversations"], list)


# ─── AI: chat creates conversation (mocked Gemini) ────────────────────────────

def test_ai_chat_creates_conversation(client):
    with patch("app.services.gemini_service.send_message", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = "Here is my answer about machine learning!"
        response = client.post("/api/v1/ai/chat", json={
            "message": "What is machine learning?"
        })
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
    assert data["response"] == "Here is my answer about machine learning!"


# ─── AI: delete conversation ──────────────────────────────────────────────────

def test_ai_delete_nonexistent_conversation_returns_404(client):
    response = client.delete(f"/api/v1/ai/conversations/{uuid4()}")
    assert response.status_code == 404


# ─── Admin: suspend and unsuspend user ───────────────────────────────────────

def test_admin_can_suspend_user(admin_client, student_user, db_session):
    response = admin_client.put(f"/api/v1/admin/users/{student_user.id}/suspend")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "suspended"

    # Unsuspend
    response = admin_client.put(f"/api/v1/admin/users/{student_user.id}/unsuspend")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"


# ─── Admin: get user by ID ────────────────────────────────────────────────────

def test_admin_can_get_user_by_id(admin_client, student_user):
    response = admin_client.get(f"/api/v1/admin/users/{student_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(student_user.id)


# ─── Admin: user not found returns 404 ───────────────────────────────────────

def test_admin_get_nonexistent_user_returns_404(admin_client):
    response = admin_client.get(f"/api/v1/admin/users/{uuid4()}")
    assert response.status_code == 404


# ─── Complaints: list own complaints ─────────────────────────────────────────

def test_student_can_list_own_complaints(client, open_complaint):
    response = client.get("/api/v1/complaints")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


# ─── Complaints: get detail ───────────────────────────────────────────────────

def test_student_can_get_own_complaint_detail(client, open_complaint):
    response = client.get(f"/api/v1/complaints/{open_complaint.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(open_complaint.id)
    assert "responses" in data


# ─── Complaints: admin can update status ─────────────────────────────────────

def test_admin_can_resolve_complaint(admin_client, open_complaint):
    response = admin_client.put(
        f"/api/v1/complaints/{open_complaint.id}",
        json={"status": "resolved", "resolution_note": "Fixed in v2.0"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "resolved"


# ─── Activity feed: returns list ─────────────────────────────────────────────

def test_activity_feed_returns_list(client):
    response = client.get("/api/v1/activity")
    assert response.status_code == 200
    data = response.json()
    assert "activities" in data
    assert "total" in data


# ─── Health: health endpoint returns structured response ─────────────────────

def test_health_endpoint_returns_structured_response(client):
    response = client.get("/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data
    assert "timestamp" in data
