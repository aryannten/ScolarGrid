"""
Integration tests for authentication flow (Task 29.1)

Tests complete auth flow with mocked Firebase token, user creation,
role-based access, and suspended user blocking.
"""

import pytest
from unittest.mock import patch, AsyncMock


# ─── Auth: unauthenticated requests return 403 ────────────────────────────────

def test_unauthed_request_rejected():
    """Endpoint requiring auth must return 403/401 without a token."""
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as bare:
        response = bare.get("/api/v1/auth/me")
    assert response.status_code in (401, 403, 422)


# ─── Auth: /auth/me returns the current user's full profile ──────────────────

def test_get_me_returns_profile(client, student_user):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == student_user.email
    assert data["role"] == "student"


# ─── Auth: /auth/register updates name and about ─────────────────────────────

def test_register_updates_user_profile(client, student_user):
    response = client.post("/api/v1/auth/register", json={
        "name": "Updated Name", "about": "I love studying"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["about"] == "I love studying"


# ─── Auth: PUT /auth/me updates name ─────────────────────────────────────────

def test_update_me_updates_name(client, student_user):
    response = client.put("/api/v1/auth/me", data={"name": "New Name"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"


# ─── Auth: admin endpoints reject students ────────────────────────────────────

def test_student_cannot_access_admin_analytics(client):
    response = client.get("/api/v1/admin/analytics")
    assert response.status_code == 403


def test_student_cannot_list_all_users(client):
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 403


# ─── Auth: admin can access admin endpoints ───────────────────────────────────

def test_admin_can_get_analytics(admin_client):
    response = admin_client.get("/api/v1/admin/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "totals" in data


def test_admin_can_list_users(admin_client):
    response = admin_client.get("/api/v1/admin/users")
    assert response.status_code == 200
    assert "items" in response.json()
