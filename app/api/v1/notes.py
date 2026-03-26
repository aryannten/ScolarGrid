"""
Notes API routes for ScholarGrid Backend API

Handles note upload, listing/search, detail view, download tracking,
rating, and admin moderation (approve, reject, delete).
"""

import math
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.core.database import get_db
from app.core.auth import get_current_user, require_student, require_admin
from app.models.user import User
from app.models.note import Note
from app.models.rating import Rating
from app.models.download import Download
from app.schemas.schemas import (
    NoteResponse, NoteListResponse, NoteRejectRequest,
    NoteDownloadResponse, RatingRequest, RatingResponse,
)
from app.services.scoring_service import (
    quantize_decimal,
    recalculate_on_note_status_change,
    recalculate_on_rating_change,
    update_user_score_and_tier,
)

router = APIRouter(prefix="/notes", tags=["Notes"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
NOTE_ALLOWED_TYPES = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}


# ─── TEST ENDPOINT (NO AUTH REQUIRED) ─────────────────────────────────────────
@router.post("/test-upload", openapi_extra={"security": []})
async def test_upload(file: UploadFile = File(...)):
    """
    TEST ONLY: Upload a file to Cloudinary without authentication.
    This tests the Cloudinary integration without requiring Firebase auth.
    """
    from app.services.cloudinary_storage import upload_file_to_storage, STORAGE_FOLDERS, ALLOWED_EXTENSIONS
    
    try:
        file_url, filename, file_size = await upload_file_to_storage(
            file, STORAGE_FOLDERS['notes'], ALLOWED_EXTENSIONS['notes']
        )
        return {
            "success": True,
            "file_url": file_url,
            "filename": filename,
            "file_size": file_size,
            "message": "Cloudinary upload successful!"
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
NOTE_CACHE_TTL = 600  # 10 minutes


# ─── Upload ────────────────────────────────────────────────────────────────────

@router.post("", response_model=NoteResponse, status_code=201)
async def upload_note(
    title: str = Form(...),
    description: str = Form(...),
    subject: str = Form(...),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    """Upload a new educational note (PDF, PPT, DOC). Sets status to 'pending'."""
    from app.services.cloudinary_storage import upload_file_to_storage, STORAGE_FOLDERS, ALLOWED_EXTENSIONS

    # Validate and upload file
    try:
        file_url, filename, file_size = await upload_file_to_storage(
            file, STORAGE_FOLDERS['notes'], ALLOWED_EXTENSIONS['notes']
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds the 50MB size limit.")

    import pathlib
    file_type = pathlib.Path(filename).suffix.lower().lstrip(".")
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    note = Note(
        title=title,
        description=description,
        subject=subject,
        tags=tag_list,
        file_url=file_url,
        file_name=filename,
        file_size=file_size,
        file_type=file_type,
        uploader_id=current_user.id,
        status="pending",
    )
    db.add(note)

    current_user.uploads_count += 1
    db.commit()
    db.refresh(note)

    # Update score/tier
    update_user_score_and_tier(current_user, db)

    # Activity tracking
    try:
        from app.services.activity_service import create_activity
        create_activity(db, "note_upload", current_user.id, note.id)
    except Exception:
        pass

    return _note_with_uploader(note, current_user)


# ─── Search / List ─────────────────────────────────────────────────────────────

@router.get("", response_model=NoteListResponse)
def list_notes(
    keyword: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=1, le=5),
    sort_by: str = Query("date", pattern="^(date|rating|relevance)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search and filter notes with pagination."""
    query = db.query(Note)

    # Students can only see approved notes
    if current_user.role != "admin":
        query = query.filter(Note.status == "approved")

    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(
            or_(Note.title.ilike(kw), Note.description.ilike(kw))
        )

    if subject:
        query = query.filter(Note.subject.ilike(f"%{subject}%"))

    if min_rating is not None:
        query = query.filter(Note.average_rating >= min_rating)

    # Sorting
    if sort_by == "rating":
        query = query.order_by(Note.average_rating.desc().nullslast())
    else:
        query = query.order_by(Note.upload_date.desc())

    total = query.count()
    notes = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for note in notes:
        uploader = db.query(User).filter(User.id == note.uploader_id).first()
        items.append(_note_with_uploader(note, uploader))

    return NoteListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


# ─── Detail ────────────────────────────────────────────────────────────────────

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed information for a single note."""
    cache_key = f"note:{note_id}"
    try:
        from app.services.redis_service import get_cache, set_cache
        cached = get_cache(cache_key)
        if cached:
            return cached
    except Exception:
        pass

    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    if current_user.role != "admin" and note.status != "approved":
        raise HTTPException(status_code=404, detail="Note not found.")

    uploader = db.query(User).filter(User.id == note.uploader_id).first()
    result = _note_with_uploader(note, uploader)

    try:
        from app.services.redis_service import set_cache
        set_cache(cache_key, result.model_dump(mode="json"), ttl=NOTE_CACHE_TTL)
    except Exception:
        pass

    return result


# ─── Download ─────────────────────────────────────────────────────────────────

@router.post("/{note_id}/download", response_model=NoteDownloadResponse)
def download_note(
    note_id: UUID,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    """Record a download and return the file URL."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    if note.status != "approved":
        raise HTTPException(status_code=403, detail="Note is not approved for download.")

    note.download_count += 1
    current_user.downloads_count += 1

    download = Download(note_id=note.id, user_id=current_user.id)
    db.add(download)
    db.commit()

    update_user_score_and_tier(current_user, db)

    # Invalidate note cache
    try:
        from app.services.redis_service import invalidate_pattern
        invalidate_pattern(f"note:{note_id}")
    except Exception:
        pass

    return NoteDownloadResponse(download_url=note.file_url, note_id=note.id, title=note.title)


# ─── Rating ────────────────────────────────────────────────────────────────────

@router.post("/{note_id}/rate", response_model=RatingResponse)
def rate_note(
    note_id: UUID,
    body: RatingRequest,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    """Rate a note (1–5 stars). Updates existing rating if already rated."""
    note = db.query(Note).filter(Note.id == note_id, Note.status == "approved").first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")

    existing = db.query(Rating).filter(
        Rating.note_id == note_id, Rating.user_id == current_user.id
    ).first()

    if existing:
        existing.rating = body.rating
        db.commit()
        rating_obj = existing
    else:
        rating_obj = Rating(note_id=note_id, user_id=current_user.id, rating=body.rating)
        db.add(rating_obj)
        db.commit()
        db.refresh(rating_obj)

    # Recalculate average
    stats = db.query(
        func.avg(Rating.rating).label("avg"),
        func.count(Rating.id).label("cnt"),
    ).filter(Rating.note_id == note_id).first()

    note.average_rating = quantize_decimal(stats.avg) if stats.avg is not None else None
    note.rating_count = stats.cnt or 0
    db.commit()

    try:
        recalculate_on_rating_change(note.uploader_id, db)
    except Exception:
        pass

    # Invalidate note cache
    try:
        from app.services.redis_service import invalidate_pattern
        invalidate_pattern(f"note:{note_id}")
    except Exception:
        pass

    # Activity for high ratings
    if body.rating >= 4:
        try:
            from app.services.activity_service import create_activity
            create_activity(db, "high_rating", current_user.id, note.id)
        except Exception:
            pass

    return RatingResponse(
        note_id=note_id,
        user_id=current_user.id,
        rating=body.rating,
        created_at=rating_obj.created_at,
    )


# ─── Admin Moderation ─────────────────────────────────────────────────────────

@router.put("/{note_id}/approve", response_model=NoteResponse)
def approve_note(
    note_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Approve a pending note (admin only)."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    previous_status = note.status
    note.status = "approved"
    if previous_status != "approved":
        note.status_updated_at = func.now()
    db.commit()
    db.refresh(note)
    _invalidate_note(note_id)
    recalculate_on_note_status_change(note.uploader_id, db)
    uploader = db.query(User).filter(User.id == note.uploader_id).first()
    return _note_with_uploader(note, uploader)


@router.put("/{note_id}/reject", response_model=NoteResponse)
def reject_note(
    note_id: UUID,
    body: NoteRejectRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Reject a pending note with a reason (admin only)."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    previous_status = note.status
    note.status = "rejected"
    note.rejection_reason = body.reason
    if previous_status != "rejected":
        note.status_updated_at = func.now()
    db.commit()
    db.refresh(note)
    _invalidate_note(note_id)
    recalculate_on_note_status_change(note.uploader_id, db)
    uploader = db.query(User).filter(User.id == note.uploader_id).first()
    return _note_with_uploader(note, uploader)


@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a note and its file from Cloudinary Storage (admin only)."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    uploader_id = note.uploader_id

    # Delete from Cloudinary Storage
    try:
        from app.services.cloudinary_storage import delete_file_from_storage, STORAGE_FOLDERS
        import pathlib
        # Extract public_id from file_name (remove extension)
        public_id = f"{STORAGE_FOLDERS['notes']}/{pathlib.Path(note.file_name).stem}"
        await delete_file_from_storage(public_id)
    except Exception:
        pass

    db.delete(note)
    db.commit()
    _invalidate_note(note_id)
    recalculate_on_note_status_change(uploader_id, db)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _note_with_uploader(note: Note, uploader: Optional[User]) -> NoteResponse:
    return NoteResponse(
        id=note.id,
        title=note.title,
        description=note.description,
        subject=note.subject,
        tags=note.tags,
        file_url=note.file_url,
        file_name=note.file_name,
        file_size=note.file_size,
        file_type=note.file_type,
        uploader_id=note.uploader_id,
        uploader_name=uploader.name if uploader else None,
        status=note.status,
        rejection_reason=note.rejection_reason,
        download_count=note.download_count,
        average_rating=note.average_rating,
        rating_count=note.rating_count,
        upload_date=note.upload_date,
    )


def _invalidate_note(note_id: UUID):
    try:
        from app.services.redis_service import invalidate_pattern
        invalidate_pattern(f"note:{note_id}")
    except Exception:
        pass
