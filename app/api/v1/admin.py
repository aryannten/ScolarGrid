"""
Admin routes for ScholarGrid Backend API

Analytics dashboard, user management, and pending notes review.
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.core.database import get_db
from app.core.auth import require_admin
from app.models.user import User
from app.models.note import Note
from app.models.download import Download
from app.models.chat import ChatGroup
from app.models.complaint import Complaint
from app.schemas.schemas import (
    UserResponse, PaginatedUsers, NoteResponse, NoteListResponse,
    AnalyticsResponse, AnalyticsTotals, MonthlyCount, SubjectCount, ComplaintStats,
    ScoreDetailsResponse, NoteRatingBreakdown,
)

router = APIRouter(prefix="/admin", tags=["Admin"])

ANALYTICS_TTL = 600  # 10 minutes


def _year_month_expression(db: Session, column):
    if db.bind is not None and db.bind.dialect.name == "sqlite":
        return func.strftime("%Y-%m", column)
    return func.to_char(column, "YYYY-MM")


# ─── Analytics ────────────────────────────────────────────────────────────────

@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Platform analytics dashboard (admin only). Cached for 10 minutes."""
    cache_key = "analytics:dashboard"
    try:
        from app.services.redis_service import get_cache, set_cache
        cached = get_cache(cache_key)
        if cached:
            return cached
    except Exception:
        pass

    totals = AnalyticsTotals(
        users=db.query(User).count(),
        students=db.query(User).filter(User.role == "student").count(),
        admins=db.query(User).filter(User.role == "admin").count(),
        notes=db.query(Note).count(),
        approved_notes=db.query(Note).filter(Note.status == "approved").count(),
        pending_notes=db.query(Note).filter(Note.status == "pending").count(),
        total_downloads=db.query(func.sum(Note.download_count)).scalar() or 0,
        chat_groups=db.query(ChatGroup).count(),
        complaints=db.query(Complaint).count(),
    )

    # Monthly uploads (last 12 months)
    monthly_uploads = []
    monthly_regs = []
    note_year_month = _year_month_expression(db, Note.upload_date)
    user_year_month = _year_month_expression(db, User.created_at)
    for i in range(11, -1, -1):
        dt = datetime.now(timezone.utc) - timedelta(days=30 * i)
        label = dt.strftime("%Y-%m")
        uploads = db.query(Note).filter(
            note_year_month == label
        ).count()
        regs = db.query(User).filter(
            user_year_month == label
        ).count()
        monthly_uploads.append(MonthlyCount(month=label, count=uploads))
        monthly_regs.append(MonthlyCount(month=label, count=regs))

    # Top 10 subjects
    subject_rows = (
        db.query(Note.subject, func.count(Note.id).label("cnt"))
        .filter(Note.status == "approved")
        .group_by(Note.subject)
        .order_by(func.count(Note.id).desc())
        .limit(10)
        .all()
    )
    top_subjects = [SubjectCount(subject=r.subject, count=r.cnt) for r in subject_rows]

    # Complaint stats
    def _complaint_count(s):
        return db.query(Complaint).filter(Complaint.status == s).count()

    complaint_stats = ComplaintStats(
        open=_complaint_count("open"),
        in_progress=_complaint_count("in_progress"),
        resolved=_complaint_count("resolved"),
        closed=_complaint_count("closed"),
    )

    result = AnalyticsResponse(
        totals=totals,
        trends={
            "monthly_uploads": [m.model_dump() for m in monthly_uploads],
            "monthly_registrations": [m.model_dump() for m in monthly_regs],
        },
        top_subjects=top_subjects,
        complaint_stats=complaint_stats,
    )

    try:
        from app.services.redis_service import set_cache
        set_cache(cache_key, result.model_dump(mode="json"), ttl=ANALYTICS_TTL)
    except Exception:
        pass

    return result


# ─── User Management ─────────────────────────────────────────────────────────

@router.get("/users", response_model=PaginatedUsers)
def list_users(
    role: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all users with filtering (admin only)."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if tier:
        query = query.filter(User.tier == tier)
    if search:
        q = f"%{search}%"
        query = query.filter(User.name.ilike(q) | User.email.ilike(q))

    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedUsers(items=users, total=total, page=page, page_size=page_size)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get full user details (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.get("/users/{user_id}/score-details", response_model=ScoreDetailsResponse)
def get_user_score_details(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Return a detailed score breakdown for a student."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    rated_notes = (
        db.query(Note)
        .filter(
            Note.uploader_id == user_id,
            Note.status == "approved",
            Note.average_rating.isnot(None),
        )
        .order_by(Note.upload_date.desc())
        .all()
    )

    return ScoreDetailsResponse(
        user_id=user.id,
        name=user.name,
        uploads_count=user.uploads_count,
        downloads_count=user.downloads_count,
        average_rating=user.average_rating,
        approved_notes_with_ratings_count=len(rated_notes),
        note_ratings=[
            NoteRatingBreakdown(
                note_id=note.id,
                title=note.title,
                average_rating=note.average_rating,
                rating_count=note.rating_count,
            )
            for note in rated_notes
        ],
        score=user.score,
        tier=user.tier,
    )


@router.put("/users/{user_id}/suspend", response_model=UserResponse)
def suspend_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Suspend a user account (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.status = "suspended"
    db.commit()
    db.refresh(user)
    try:
        from app.services.redis_service import invalidate_pattern
        invalidate_pattern(f"user:profile:{user_id}")
    except Exception:
        pass
    return user


@router.put("/users/{user_id}/unsuspend", response_model=UserResponse)
def unsuspend_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Unsuspend a user account (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.status = "active"
    db.commit()
    db.refresh(user)
    try:
        from app.services.redis_service import invalidate_pattern
        invalidate_pattern(f"user:profile:{user_id}")
    except Exception:
        pass
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a user and anonymize their content (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)
    db.commit()
    try:
        from app.services.redis_service import invalidate_pattern
        invalidate_pattern(f"user:profile:{user_id}")
        invalidate_pattern("leaderboard:*")
        invalidate_pattern("analytics:*")
    except Exception:
        pass


# ─── Pending Notes ────────────────────────────────────────────────────────────

@router.get("/notes/pending", response_model=NoteListResponse)
def list_pending_notes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all notes awaiting approval (admin only)."""
    query = db.query(Note).filter(Note.status == "pending").order_by(Note.upload_date.desc())
    total = query.count()
    notes = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for note in notes:
        uploader = db.query(User).filter(User.id == note.uploader_id).first()
        from app.api.v1.notes import _note_with_uploader
        items.append(_note_with_uploader(note, uploader))

    return NoteListResponse(
        items=items, total=total, page=page, page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )
