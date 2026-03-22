"""
Security and error handling tests (Tasks 23.2–23.4, 24.2–24.3, 32.5)

Tests input validation, SQL injection prevention, error response formats,
security headers, and CORS behavior.
"""

import pytest


# ─── Error format: validation errors return standard structure ────────────────

def test_validation_error_returns_standard_format(client, approved_note):
    response = client.post(f"/api/v1/notes/{approved_note.id}/rate", json={"rating": 99})
    assert response.status_code == 422
    data = response.json()
    # Should have our custom error format OR FastAPI's default
    assert "detail" in data or "error" in data


# ─── Error format: 404 returns JSON not HTML ─────────────────────────────────

def test_404_returns_json(client):
    from uuid import uuid4
    response = client.get(f"/api/v1/notes/{uuid4()}")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")


# ─── Security: security headers are present ──────────────────────────────────

def test_security_headers_present(client):
    response = client.get("/health")
    assert "x-content-type-options" in response.headers
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "x-frame-options" in response.headers
    assert "x-xss-protection" in response.headers


# ─── Security: SQL injection attempt is safely rejected ──────────────────────

def test_sql_injection_in_search_is_safe(client):
    # SQLAlchemy parameterized queries prevent injection; just check no 500
    response = client.get("/api/v1/notes?keyword='; DROP TABLE notes;--")
    assert response.status_code == 200
    # Must return a valid notes list, not crash
    assert "items" in response.json()


# ─── Security: oversized string is rejected by Pydantic ─────────────────────

def test_oversized_name_in_register_rejected(client):
    oversized = "A" * 101  # limit is 100
    response = client.post("/api/v1/auth/register", json={"name": oversized})
    assert response.status_code == 422


# ─── Security: empty content rejected ────────────────────────────────────────

def test_empty_message_in_ai_chat_rejected(client):
    response = client.post("/api/v1/ai/chat", json={"message": ""})
    assert response.status_code == 422


# ─── Security: invalid category in complaint rejected ────────────────────────

def test_invalid_complaint_category_rejected(client):
    response = client.post(
        "/api/v1/complaints",
        data={"title": "T", "description": "D", "category": "illegal_category"}
    )
    assert response.status_code in (422, 400)


# ─── Security: endpoints documented in OpenAPI ───────────────────────────────

def test_openapi_schema_accessible(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/auth/me" in schema["paths"]
    assert "/api/v1/notes" in schema["paths"]
    assert "/api/v1/leaderboard" in schema["paths"]
    assert "/api/v1/ai/chat" in schema["paths"]
