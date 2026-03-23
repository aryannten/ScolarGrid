"""
Complaints routes for ScholarGrid Backend API
"""

import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user, require_admin
from app.models.user import User
from app.models.complaint import Complaint, ComplaintResponse as ComplaintResponseModel
from app.schemas.schemas import (
    ComplaintResponse, ComplaintDetailResponse, ComplaintListResponse,
    ComplaintUpdateRequest, ComplaintResponseCreate, ComplaintResponseItem,
    VALID_CATEGORIES,
)

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("", response_model=ComplaintResponse, status_code=201)
async def submit_complaint(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    screenshot: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a complaint with optional screenshot attachment."""
    if category.lower() not in VALID_CATEGORIES:
        raise HTTPException(status_code=422, detail=f"category must be one of {VALID_CATEGORIES}")

    screenshot_url = None
    if screenshot:
        try:
            from app.services.cloudinary_storage import upload_file_to_storage, STORAGE_FOLDERS, ALLOWED_EXTENSIONS
            url, _, _ = await upload_file_to_storage(
                screenshot, STORAGE_FOLDERS['complaint_attachments'], ALLOWED_EXTENSIONS["complaint_attachments"]
            )
            screenshot_url = url
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Screenshot upload failed: {str(e)}")

    complaint = Complaint(
        title=title,
        description=description,
        category=category.lower(),
        status="open",
        priority="medium",
        screenshot_url=screenshot_url,
        submitter_id=current_user.id,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return _complaint_response(complaint, current_user)


@router.get("", response_model=ComplaintListResponse)
def list_complaints(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List complaints. Students see only own; admins see all."""
    query = db.query(Complaint)
    if current_user.role != "admin":
        query = query.filter(Complaint.submitter_id == current_user.id)
    if status:
        query = query.filter(Complaint.status == status)
    if priority:
        query = query.filter(Complaint.priority == priority)
    if category:
        query = query.filter(Complaint.category == category)

    total = query.count()
    complaints = query.order_by(Complaint.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    submitter_map = {}
    for c in complaints:
        if c.submitter_id and c.submitter_id not in submitter_map:
            submitter_map[c.submitter_id] = db.query(User).filter(User.id == c.submitter_id).first()

    items = [_complaint_response(c, submitter_map.get(c.submitter_id)) for c in complaints]

    return ComplaintListResponse(
        items=items, total=total, page=page, page_size=page_size,
    )


@router.get("/{complaint_id}", response_model=ComplaintDetailResponse)
def get_complaint(
    complaint_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single complaint with all responses. Users can only access their own."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")
    if current_user.role != "admin" and complaint.submitter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    submitter = db.query(User).filter(User.id == complaint.submitter_id).first()
    responses_db = db.query(ComplaintResponseModel).filter(
        ComplaintResponseModel.complaint_id == complaint_id
    ).order_by(ComplaintResponseModel.created_at.asc()).all()

    responses = []
    for r in responses_db:
        admin = db.query(User).filter(User.id == r.admin_id).first()
        responses.append(ComplaintResponseItem(
            id=r.id, text=r.text,
            admin_id=r.admin_id, admin_name=admin.name if admin else None,
            created_at=r.created_at,
        ))

    return ComplaintDetailResponse(
        id=complaint.id, title=complaint.title, description=complaint.description,
        category=complaint.category, status=complaint.status, priority=complaint.priority,
        screenshot_url=complaint.screenshot_url, submitter_id=complaint.submitter_id,
        submitter_name=submitter.name if submitter else None,
        resolution_note=complaint.resolution_note,
        created_at=complaint.created_at, responses=responses,
    )


@router.put("/{complaint_id}", response_model=ComplaintDetailResponse)
def update_complaint(
    complaint_id: UUID,
    body: ComplaintUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update complaint status/priority (admin only). resolution_note required when resolving."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    if body.status == "resolved" and not body.resolution_note:
        raise HTTPException(status_code=422, detail="resolution_note is required when resolving a complaint.")

    if body.status:
        complaint.status = body.status
    if body.priority:
        complaint.priority = body.priority
    if body.resolution_note:
        complaint.resolution_note = body.resolution_note

    db.commit()
    db.refresh(complaint)

    # Return detail response
    from fastapi import Request
    return get_complaint(complaint_id, current_user, db)


@router.post("/{complaint_id}/responses", response_model=ComplaintResponseItem, status_code=201)
def add_response(
    complaint_id: UUID,
    body: ComplaintResponseCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Add an admin response to a complaint."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    response = ComplaintResponseModel(
        complaint_id=complaint_id,
        admin_id=current_user.id,
        text=body.text,
    )
    db.add(response)
    db.commit()
    db.refresh(response)

    return ComplaintResponseItem(
        id=response.id, text=response.text,
        admin_id=response.admin_id, admin_name=current_user.name,
        created_at=response.created_at,
    )


def _complaint_response(complaint: Complaint, submitter: Optional[User]) -> ComplaintResponse:
    return ComplaintResponse(
        id=complaint.id, title=complaint.title, description=complaint.description,
        category=complaint.category, status=complaint.status, priority=complaint.priority,
        screenshot_url=complaint.screenshot_url, submitter_id=complaint.submitter_id,
        submitter_name=submitter.name if submitter else None,
        resolution_note=complaint.resolution_note,
        created_at=complaint.created_at,
    )
