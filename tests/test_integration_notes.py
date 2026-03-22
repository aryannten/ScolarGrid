"""
Integration tests for notes workflow (Task 29.2)

Tests note listing, detail, download, rating, and admin moderation
through the TestClient with DB override.
"""

import pytest
from uuid import uuid4


# ─── Notes: list approved notes ───────────────────────────────────────────────

def test_list_notes_returns_approved_only(client, approved_note, pending_note):
    response = client.get("/api/v1/notes")
    assert response.status_code == 200
    data = response.json()
    ids = [n["id"] for n in data["items"]]
    assert str(approved_note.id) in ids
    assert str(pending_note.id) not in ids


# ─── Notes: search by keyword ─────────────────────────────────────────────────

def test_search_notes_by_keyword(client, approved_note):
    response = client.get("/api/v1/notes?keyword=Calculus")
    assert response.status_code == 200
    data = response.json()
    assert any("Calculus" in n["title"] for n in data["items"])


# ─── Notes: get specific note ─────────────────────────────────────────────────

def test_get_note_detail(client, approved_note):
    response = client.get(f"/api/v1/notes/{approved_note.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(approved_note.id)
    assert data["title"] == approved_note.title


# ─── Notes: get non-existent note returns 404 ────────────────────────────────

def test_get_nonexistent_note_returns_404(client):
    response = client.get(f"/api/v1/notes/{uuid4()}")
    assert response.status_code == 404


# ─── Notes: download records are tracked ─────────────────────────────────────

def test_download_note_returns_url(client, approved_note, db_session, student_user):
    prev_count = approved_note.download_count
    response = client.post(f"/api/v1/notes/{approved_note.id}/download")
    assert response.status_code == 200
    data = response.json()
    assert "download_url" in data
    db_session.refresh(approved_note)
    assert approved_note.download_count == prev_count + 1


# ─── Notes: download pending note returns 403 ────────────────────────────────

def test_download_pending_note_returns_403(client, pending_note):
    response = client.post(f"/api/v1/notes/{pending_note.id}/download")
    assert response.status_code == 403


# ─── Notes: rating stores correctly ──────────────────────────────────────────

def test_rate_note(client, approved_note):
    response = client.post(f"/api/v1/notes/{approved_note.id}/rate", json={"rating": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5


# ─── Notes: invalid rating rejected ──────────────────────────────────────────

def test_invalid_rating_rejected(client, approved_note):
    response = client.post(f"/api/v1/notes/{approved_note.id}/rate", json={"rating": 6})
    assert response.status_code == 422


# ─── Admin: approve note changes status ──────────────────────────────────────

def test_admin_can_approve_pending_note(admin_client, pending_note, db_session):
    response = admin_client.put(f"/api/v1/notes/{pending_note.id}/approve")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


# ─── Admin: reject note with reason ──────────────────────────────────────────

def test_admin_can_reject_note_with_reason(admin_client, pending_note, db_session):
    # Reset to pending first
    pending_note.status = "pending"
    db_session.commit()
    response = admin_client.put(
        f"/api/v1/notes/{pending_note.id}/reject",
        json={"reason": "Poor quality content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["rejection_reason"] == "Poor quality content"


# ─── Admin: pending notes list ────────────────────────────────────────────────

def test_admin_can_list_pending_notes(admin_client, pending_note, db_session):
    pending_note.status = "pending"
    db_session.commit()
    response = admin_client.get("/api/v1/admin/notes/pending")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


# ─── Leaderboard: returns rankings ───────────────────────────────────────────

def test_leaderboard_returns_students(client, student_user):
    response = client.get("/api/v1/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert "rankings" in data
    assert "total" in data
