"""
Integration tests for admin features (Task 29.5)

Tests note moderation workflow, user management, analytics calculation,
and complaint management end-to-end.

**Validates: Requirements 8, 15, 16, 18**
"""

import pytest
from uuid import uuid4
from unittest.mock import patch, AsyncMock


# ═══════════════════════════════════════════════════════════════════════════════
# Note Moderation Workflow Tests
# ═══════════════════════════════════════════════════════════════════════════════

def test_admin_can_approve_pending_note(admin_client, pending_note, db_session):
    """Admin approves a pending note, making it visible to all users."""
    response = admin_client.put(f"/api/v1/notes/{pending_note.id}/approve")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["id"] == str(pending_note.id)
    
    # Verify in database
    db_session.refresh(pending_note)
    assert pending_note.status == "approved"


def test_admin_can_reject_note_with_reason(admin_client, pending_note, db_session):
    """Admin rejects a note with a rejection reason."""
    response = admin_client.put(
        f"/api/v1/notes/{pending_note.id}/reject",
        json={"reason": "Content does not meet quality standards"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["rejection_reason"] == "Content does not meet quality standards"
    
    # Verify in database
    db_session.refresh(pending_note)
    assert pending_note.status == "rejected"
    assert pending_note.rejection_reason == "Content does not meet quality standards"


def test_admin_can_delete_note(admin_client, approved_note, db_session):
    """Admin deletes a note and its file from storage."""
    note_id = approved_note.id
    
    # Mock the storage deletion
    with patch("app.services.cloudinary_storage.delete_file_from_storage", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = None
        response = admin_client.delete(f"/api/v1/notes/{note_id}")
    
    assert response.status_code == 204
    
    # Verify note is deleted from database
    from app.models.note import Note
    deleted_note = db_session.query(Note).filter(Note.id == note_id).first()
    assert deleted_note is None


def test_admin_can_list_pending_notes(admin_client, pending_note, db_session):
    """Admin retrieves list of all pending notes for review."""
    response = admin_client.get("/api/v1/admin/notes/pending")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # Verify pending note is in the list
    note_ids = [item["id"] for item in data["items"]]
    assert str(pending_note.id) in note_ids


def test_student_cannot_approve_note(client, pending_note):
    """Students cannot approve notes (authorization check)."""
    response = client.put(f"/api/v1/notes/{pending_note.id}/approve")
    assert response.status_code == 403


def test_student_cannot_reject_note(client, pending_note):
    """Students cannot reject notes (authorization check)."""
    response = client.put(
        f"/api/v1/notes/{pending_note.id}/reject",
        json={"reason": "Test"}
    )
    assert response.status_code == 403


def test_student_cannot_delete_note(client, approved_note):
    """Students cannot delete notes (authorization check)."""
    response = client.delete(f"/api/v1/notes/{approved_note.id}")
    assert response.status_code == 403


def test_approve_nonexistent_note_returns_404(admin_client):
    """Approving a non-existent note returns 404."""
    response = admin_client.put(f"/api/v1/notes/{uuid4()}/approve")
    assert response.status_code == 404


def test_reject_nonexistent_note_returns_404(admin_client):
    """Rejecting a non-existent note returns 404."""
    response = admin_client.put(
        f"/api/v1/notes/{uuid4()}/reject",
        json={"reason": "Test"}
    )
    assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# User Management Tests
# ═══════════════════════════════════════════════════════════════════════════════

def test_admin_can_suspend_user(admin_client, student_user, db_session):
    """Admin suspends a user account, preventing authentication."""
    response = admin_client.put(f"/api/v1/admin/users/{student_user.id}/suspend")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "suspended"
    assert data["id"] == str(student_user.id)
    
    # Verify in database
    db_session.refresh(student_user)
    assert student_user.status == "suspended"


def test_admin_can_unsuspend_user(admin_client, student_user, db_session):
    """Admin unsuspends a previously suspended user."""
    # First suspend
    student_user.status = "suspended"
    db_session.commit()
    
    # Then unsuspend
    response = admin_client.put(f"/api/v1/admin/users/{student_user.id}/unsuspend")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    
    # Verify in database
    db_session.refresh(student_user)
    assert student_user.status == "active"


def test_admin_can_delete_user(admin_client, second_student, db_session):
    """Admin deletes a user account and anonymizes their content."""
    user_id = second_student.id
    
    response = admin_client.delete(f"/api/v1/admin/users/{user_id}")
    assert response.status_code == 204
    
    # Verify user is deleted from database
    from app.models.user import User
    deleted_user = db_session.query(User).filter(User.id == user_id).first()
    assert deleted_user is None


def test_admin_can_list_all_users(admin_client, student_user, admin_user):
    """Admin retrieves paginated list of all users."""
    response = admin_client.get("/api/v1/admin/users")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 2  # At least student and admin


def test_admin_can_filter_users_by_role(admin_client, student_user, admin_user):
    """Admin filters users by role."""
    response = admin_client.get("/api/v1/admin/users?role=student")
    assert response.status_code == 200
    data = response.json()
    assert all(user["role"] == "student" for user in data["items"])


def test_admin_can_filter_users_by_tier(admin_client, student_user, db_session):
    """Admin filters users by tier."""
    # Set student to gold tier
    student_user.tier = "gold"
    student_user.score = 2500
    db_session.commit()
    
    response = admin_client.get("/api/v1/admin/users?tier=gold")
    assert response.status_code == 200
    data = response.json()
    assert any(user["id"] == str(student_user.id) for user in data["items"])


def test_admin_can_search_users_by_name(admin_client, student_user):
    """Admin searches users by name."""
    response = admin_client.get(f"/api/v1/admin/users?search={student_user.name}")
    assert response.status_code == 200
    data = response.json()
    assert any(user["id"] == str(student_user.id) for user in data["items"])


def test_admin_can_get_user_details(admin_client, student_user):
    """Admin retrieves detailed user information."""
    response = admin_client.get(f"/api/v1/admin/users/{student_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(student_user.id)
    assert data["email"] == student_user.email
    assert "score" in data
    assert "tier" in data


def test_student_cannot_access_user_management(client, student_user):
    """Students cannot access user management endpoints."""
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 403


def test_suspend_nonexistent_user_returns_404(admin_client):
    """Suspending a non-existent user returns 404."""
    response = admin_client.put(f"/api/v1/admin/users/{uuid4()}/suspend")
    assert response.status_code == 404


def test_get_nonexistent_user_returns_404(admin_client):
    """Getting a non-existent user returns 404."""
    response = admin_client.get(f"/api/v1/admin/users/{uuid4()}")
    assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# Analytics Calculation Tests
# ═══════════════════════════════════════════════════════════════════════════════

def test_admin_can_get_analytics_dashboard(admin_client, student_user, approved_note):
    """Admin retrieves comprehensive analytics dashboard."""
    response = admin_client.get("/api/v1/admin/analytics")
    assert response.status_code == 200
    data = response.json()
    
    # Verify totals structure
    assert "totals" in data
    totals = data["totals"]
    assert "users" in totals
    assert "students" in totals
    assert "admins" in totals
    assert "notes" in totals
    assert "approved_notes" in totals
    assert "pending_notes" in totals
    assert "total_downloads" in totals
    assert "chat_groups" in totals
    assert "complaints" in totals
    
    # Verify counts are non-negative
    assert totals["users"] >= 0
    assert totals["students"] >= 0
    assert totals["admins"] >= 0
    assert totals["notes"] >= 0


def test_analytics_includes_monthly_trends(admin_client):
    """Analytics includes monthly upload and registration trends."""
    response = admin_client.get("/api/v1/admin/analytics")
    assert response.status_code == 200
    data = response.json()
    
    assert "trends" in data
    trends = data["trends"]
    assert "monthly_uploads" in trends
    assert "monthly_registrations" in trends
    
    # Verify 12 months of data
    assert len(trends["monthly_uploads"]) == 12
    assert len(trends["monthly_registrations"]) == 12
    
    # Verify structure of monthly data
    for month_data in trends["monthly_uploads"]:
        assert "month" in month_data
        assert "count" in month_data


def test_analytics_includes_top_subjects(admin_client, approved_note):
    """Analytics includes top 10 subjects by note count."""
    response = admin_client.get("/api/v1/admin/analytics")
    assert response.status_code == 200
    data = response.json()
    
    assert "top_subjects" in data
    top_subjects = data["top_subjects"]
    assert isinstance(top_subjects, list)
    assert len(top_subjects) <= 10
    
    # Verify structure
    for subject in top_subjects:
        assert "subject" in subject
        assert "count" in subject
        assert subject["count"] > 0


def test_analytics_includes_complaint_stats(admin_client, open_complaint):
    """Analytics includes complaint statistics by status."""
    response = admin_client.get("/api/v1/admin/analytics")
    assert response.status_code == 200
    data = response.json()
    
    assert "complaint_stats" in data
    stats = data["complaint_stats"]
    assert "open" in stats
    assert "in_progress" in stats
    assert "resolved" in stats
    assert "closed" in stats
    
    # Verify counts are non-negative
    assert stats["open"] >= 0
    assert stats["in_progress"] >= 0
    assert stats["resolved"] >= 0
    assert stats["closed"] >= 0


def test_student_cannot_access_analytics(client):
    """Students cannot access analytics dashboard."""
    response = client.get("/api/v1/admin/analytics")
    assert response.status_code == 403


def test_analytics_caching_works(admin_client, db_session):
    """Analytics results are cached for performance."""
    # First request - cache miss
    response1 = admin_client.get("/api/v1/admin/analytics")
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Second request - should hit cache
    response2 = admin_client.get("/api/v1/admin/analytics")
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Results should be identical
    assert data1 == data2


# ═══════════════════════════════════════════════════════════════════════════════
# Complaint Management Tests
# ═══════════════════════════════════════════════════════════════════════════════

def test_admin_can_update_complaint_status(admin_client, open_complaint, db_session):
    """Admin updates complaint status to in_progress."""
    response = admin_client.put(
        f"/api/v1/complaints/{open_complaint.id}",
        json={"status": "in_progress"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    
    # Verify in database
    db_session.refresh(open_complaint)
    assert open_complaint.status == "in_progress"


def test_admin_can_update_complaint_priority(admin_client, open_complaint, db_session):
    """Admin updates complaint priority to high."""
    response = admin_client.put(
        f"/api/v1/complaints/{open_complaint.id}",
        json={"priority": "high"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "high"
    
    # Verify in database
    db_session.refresh(open_complaint)
    assert open_complaint.priority == "high"


def test_admin_can_resolve_complaint_with_note(admin_client, open_complaint, db_session):
    """Admin resolves complaint with resolution note."""
    response = admin_client.put(
        f"/api/v1/complaints/{open_complaint.id}",
        json={
            "status": "resolved",
            "resolution_note": "Issue fixed in version 2.0"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "resolved"
    assert data["resolution_note"] == "Issue fixed in version 2.0"
    
    # Verify in database
    db_session.refresh(open_complaint)
    assert open_complaint.status == "resolved"
    assert open_complaint.resolution_note == "Issue fixed in version 2.0"


def test_resolve_complaint_requires_resolution_note(admin_client, open_complaint):
    """Resolving a complaint without resolution note returns 422."""
    response = admin_client.put(
        f"/api/v1/complaints/{open_complaint.id}",
        json={"status": "resolved"}
    )
    assert response.status_code == 422


def test_admin_can_add_response_to_complaint(admin_client, open_complaint, db_session):
    """Admin adds a response to a complaint."""
    response = admin_client.post(
        f"/api/v1/complaints/{open_complaint.id}/responses",
        json={"text": "We are investigating this issue."}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "We are investigating this issue."
    assert "admin_id" in data
    assert "admin_name" in data
    assert "created_at" in data


def test_admin_can_view_complaint_with_responses(admin_client, open_complaint, db_session):
    """Admin views complaint details including all responses."""
    # Add a response first
    admin_client.post(
        f"/api/v1/complaints/{open_complaint.id}/responses",
        json={"text": "Response 1"}
    )
    admin_client.post(
        f"/api/v1/complaints/{open_complaint.id}/responses",
        json={"text": "Response 2"}
    )
    
    # Get complaint details
    response = admin_client.get(f"/api/v1/complaints/{open_complaint.id}")
    assert response.status_code == 200
    data = response.json()
    assert "responses" in data
    assert len(data["responses"]) == 2
    assert data["responses"][0]["text"] == "Response 1"
    assert data["responses"][1]["text"] == "Response 2"


def test_student_cannot_update_complaint_status(client, open_complaint):
    """Students cannot update complaint status."""
    response = client.put(
        f"/api/v1/complaints/{open_complaint.id}",
        json={"status": "resolved", "resolution_note": "Test"}
    )
    assert response.status_code == 403


def test_student_cannot_add_complaint_response(client, open_complaint):
    """Students cannot add responses to complaints."""
    response = client.post(
        f"/api/v1/complaints/{open_complaint.id}/responses",
        json={"text": "Test response"}
    )
    assert response.status_code == 403


def test_update_nonexistent_complaint_returns_404(admin_client):
    """Updating a non-existent complaint returns 404."""
    response = admin_client.put(
        f"/api/v1/complaints/{uuid4()}",
        json={"status": "resolved", "resolution_note": "Test"}
    )
    assert response.status_code == 404


def test_add_response_to_nonexistent_complaint_returns_404(admin_client):
    """Adding response to non-existent complaint returns 404."""
    response = admin_client.post(
        f"/api/v1/complaints/{uuid4()}/responses",
        json={"text": "Test"}
    )
    assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# End-to-End Workflow Tests
# ═══════════════════════════════════════════════════════════════════════════════

def test_complete_note_moderation_workflow(admin_client, pending_note, db_session):
    """Complete workflow: list pending → approve → verify visible."""
    # 1. List pending notes
    response = admin_client.get("/api/v1/admin/notes/pending")
    assert response.status_code == 200
    assert any(item["id"] == str(pending_note.id) for item in response.json()["items"])
    
    # 2. Approve the note
    response = admin_client.put(f"/api/v1/notes/{pending_note.id}/approve")
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    
    # 3. Verify it's no longer in pending list
    response = admin_client.get("/api/v1/admin/notes/pending")
    assert response.status_code == 200
    assert not any(item["id"] == str(pending_note.id) for item in response.json()["items"])


def test_complete_user_management_workflow(admin_client, student_user, db_session):
    """Complete workflow: list users → get details → suspend → unsuspend."""
    # 1. List all users
    response = admin_client.get("/api/v1/admin/users")
    assert response.status_code == 200
    assert any(user["id"] == str(student_user.id) for user in response.json()["items"])
    
    # 2. Get user details
    response = admin_client.get(f"/api/v1/admin/users/{student_user.id}")
    assert response.status_code == 200
    assert response.json()["status"] == "active"
    
    # 3. Suspend user
    response = admin_client.put(f"/api/v1/admin/users/{student_user.id}/suspend")
    assert response.status_code == 200
    assert response.json()["status"] == "suspended"
    
    # 4. Unsuspend user
    response = admin_client.put(f"/api/v1/admin/users/{student_user.id}/unsuspend")
    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_complete_complaint_management_workflow(admin_client, open_complaint, db_session):
    """Complete workflow: view complaint → update priority → add response → resolve."""
    # 1. View complaint
    response = admin_client.get(f"/api/v1/complaints/{open_complaint.id}")
    assert response.status_code == 200
    assert response.json()["status"] == "open"
    
    # 2. Update priority to high
    response = admin_client.put(
        f"/api/v1/complaints/{open_complaint.id}",
        json={"priority": "high"}
    )
    assert response.status_code == 200
    assert response.json()["priority"] == "high"
    
    # 3. Add admin response
    response = admin_client.post(
        f"/api/v1/complaints/{open_complaint.id}/responses",
        json={"text": "We are working on this issue."}
    )
    assert response.status_code == 201
    
    # 4. Resolve with note
    response = admin_client.put(
        f"/api/v1/complaints/{open_complaint.id}",
        json={
            "status": "resolved",
            "resolution_note": "Fixed in latest release"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"
    
    # 5. Verify resolution persisted
    response = admin_client.get(f"/api/v1/complaints/{open_complaint.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "resolved"
    assert data["resolution_note"] == "Fixed in latest release"
    assert len(data["responses"]) == 1
