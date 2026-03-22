"""
Chat group routes for ScholarGrid Backend API

Handles chat group creation, joining, listing, deletion, and message history.
"""

import math
import random
import string
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.chat import ChatGroup, ChatMembership, Message
from app.schemas.schemas import (
    ChatGroupCreateRequest, JoinGroupRequest,
    ChatGroupResponse, ChatGroupListResponse,
    MessageResponse, MessageListResponse,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


def _generate_join_code(db: Session) -> str:
    """Generate a unique 8-character alphanumeric join code."""
    chars = string.ascii_uppercase + string.digits
    for _ in range(20):
        code = "".join(random.choices(chars, k=8))
        if not db.query(ChatGroup).filter(ChatGroup.join_code == code).first():
            return code
    raise RuntimeError("Could not generate a unique join code.")


# ─── Groups ────────────────────────────────────────────────────────────────────

@router.post("/groups", response_model=ChatGroupResponse, status_code=201)
def create_group(
    body: ChatGroupCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new chat group with a unique 8-char join code."""
    join_code = _generate_join_code(db)
    group = ChatGroup(
        name=body.name,
        description=body.description,
        join_code=join_code,
        creator_id=current_user.id,
        member_count=1,
    )
    db.add(group)
    db.flush()

    membership = ChatMembership(group_id=group.id, user_id=current_user.id)
    db.add(membership)
    db.commit()
    db.refresh(group)
    return group


@router.post("/groups/join", response_model=ChatGroupResponse)
def join_group(
    body: JoinGroupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Join a chat group using its join code."""
    group = db.query(ChatGroup).filter(ChatGroup.join_code == body.join_code).first()
    if not group:
        raise HTTPException(status_code=404, detail="Invalid join code.")

    existing = db.query(ChatMembership).filter(
        ChatMembership.group_id == group.id,
        ChatMembership.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You are already a member of this group.")

    membership = ChatMembership(group_id=group.id, user_id=current_user.id)
    group.member_count += 1
    db.add(membership)
    db.commit()
    db.refresh(group)
    return group


@router.get("/groups", response_model=ChatGroupListResponse)
def list_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all chat groups the current user is a member of."""
    memberships = db.query(ChatMembership).filter(
        ChatMembership.user_id == current_user.id
    ).all()
    group_ids = [m.group_id for m in memberships]

    groups = db.query(ChatGroup).filter(
        ChatGroup.id.in_(group_ids)
    ).order_by(ChatGroup.last_message_at.desc().nullslast(), ChatGroup.created_at.desc()).all()

    return ChatGroupListResponse(groups=groups)


@router.delete("/groups/{group_id}", status_code=204)
def delete_group(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a chat group (creator only). Cascades to memberships and messages."""
    group = db.query(ChatGroup).filter(ChatGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")
    if group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the group creator can delete this group.")

    db.delete(group)
    db.commit()


# ─── Messages ─────────────────────────────────────────────────────────────────

@router.get("/groups/{group_id}/messages", response_model=MessageListResponse)
def get_messages(
    group_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get paginated message history for a chat group (members only)."""
    group = db.query(ChatGroup).filter(ChatGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")

    membership = db.query(ChatMembership).filter(
        ChatMembership.group_id == group_id,
        ChatMembership.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this group.")

    query = db.query(Message).filter(Message.group_id == group_id).order_by(Message.created_at.asc())
    total = query.count()
    messages_db = query.offset((page - 1) * page_size).limit(page_size).all()

    messages = []
    for msg in messages_db:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        messages.append(MessageResponse(
            id=msg.id,
            sender_id=msg.sender_id,
            sender_name=sender.name if sender else None,
            sender_avatar=sender.avatar_url if sender else None,
            content=msg.content,
            type=msg.type,
            file_url=msg.file_url,
            created_at=msg.created_at,
        ))

    return MessageListResponse(messages=messages, total=total, page=page, page_size=page_size)
