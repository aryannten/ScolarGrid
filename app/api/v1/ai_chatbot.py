"""
AI Chatbot routes for ScholarGrid Backend API

Endpoints for chat interaction (non-streaming and streaming), conversation
management, and usage statistics.
"""

import math
from datetime import datetime, date, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.ai_chatbot import AIConversation, AIMessage, AIUsageTracking
from app.schemas.schemas import (
    AIChatRequest, AIChatResponse,
    AIConversationSummary, AIConversationDetail, AIMessageItem,
    AIConversationListResponse, AIUsageResponse,
)

router = APIRouter(prefix="/ai", tags=["AI Chatbot"])

DAILY_MSG_LIMIT = 50


def _get_or_create_usage(user_id: UUID, db: Session) -> AIUsageTracking:
    """Get or create today's usage tracking record."""
    today = date.today()
    tracking = db.query(AIUsageTracking).filter(
        AIUsageTracking.user_id == user_id,
        AIUsageTracking.date == today,
    ).first()
    if not tracking:
        tracking = AIUsageTracking(user_id=user_id, date=today, message_count=0)
        db.add(tracking)
        db.commit()
        db.refresh(tracking)
    return tracking


def _remaining_msgs(tracking: AIUsageTracking) -> int:
    return max(0, DAILY_MSG_LIMIT - tracking.message_count)


def _next_midnight_utc() -> datetime:
    now = datetime.now(timezone.utc)
    return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


# ─── Chat Endpoints ────────────────────────────────────────────────────────────

@router.post("/chat", response_model=AIChatResponse)
async def chat(
    body: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message to the AI chatbot and receive a response."""
    tracking = _get_or_create_usage(current_user.id, db)
    if tracking.message_count >= DAILY_MSG_LIMIT:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "daily_limit_exceeded",
                "message": f"Daily limit of {DAILY_MSG_LIMIT} messages reached.",
                "reset_at": _next_midnight_utc().isoformat(),
            },
        )

    # Get or create conversation
    if body.conversation_id:
        conversation = db.query(AIConversation).filter(
            AIConversation.id == body.conversation_id,
            AIConversation.user_id == current_user.id,
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found.")
    else:
        title = body.message[:100] if len(body.message) <= 100 else body.message[:97] + "..."
        conversation = AIConversation(user_id=current_user.id, title=title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Load conversation history
    history_msgs = db.query(AIMessage).filter(
        AIMessage.conversation_id == conversation.id
    ).order_by(AIMessage.created_at.asc()).all()

    from app.services.gemini_service import build_conversation_history, send_message as gemini_send
    history = build_conversation_history(history_msgs)

    # Send to Gemini
    try:
        ai_response = await gemini_send(body.message, history)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AI service temporarily unavailable: {str(e)}")

    # Persist messages
    user_msg = AIMessage(conversation_id=conversation.id, role="user", content=body.message)
    ai_msg = AIMessage(conversation_id=conversation.id, role="assistant", content=ai_response)
    db.add_all([user_msg, ai_msg])

    conversation.message_count += 2
    conversation.updated_at = datetime.now(timezone.utc)
    tracking.message_count += 1
    tracking.updated_at = datetime.now(timezone.utc)

    db.commit()

    return AIChatResponse(
        conversation_id=conversation.id,
        message=body.message,
        response=ai_response,
        timestamp=datetime.now(timezone.utc),
        remaining_messages=_remaining_msgs(tracking),
    )


@router.post("/chat/stream")
async def chat_stream(
    body: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stream AI chatbot response via Server-Sent Events."""
    tracking = _get_or_create_usage(current_user.id, db)
    if tracking.message_count >= DAILY_MSG_LIMIT:
        raise HTTPException(status_code=429, detail="Daily AI message limit reached.")

    if body.conversation_id:
        conversation = db.query(AIConversation).filter(
            AIConversation.id == body.conversation_id,
            AIConversation.user_id == current_user.id,
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found.")
    else:
        title = body.message[:100]
        conversation = AIConversation(user_id=current_user.id, title=title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    history_msgs = db.query(AIMessage).filter(
        AIMessage.conversation_id == conversation.id
    ).order_by(AIMessage.created_at.asc()).all()

    from app.services.gemini_service import build_conversation_history, send_message_stream
    history = build_conversation_history(history_msgs)

    full_response = []

    async def generate():
        import json
        yield f"data: {json.dumps({'type': 'start', 'conversation_id': str(conversation.id)})}\n\n"
        try:
            async for chunk in send_message_stream(body.message, history):
                full_response.append(chunk)
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            return

        # Persist after streaming
        complete = "".join(full_response)
        user_msg = AIMessage(conversation_id=conversation.id, role="user", content=body.message)
        ai_msg = AIMessage(conversation_id=conversation.id, role="assistant", content=complete)
        db.add_all([user_msg, ai_msg])
        conversation.message_count += 2
        tracking.message_count += 1
        db.commit()

        yield f"data: {json.dumps({'type': 'end', 'remaining_messages': _remaining_msgs(tracking)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ─── Conversation Management ───────────────────────────────────────────────────

@router.get("/conversations", response_model=AIConversationListResponse)
def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's AI chatbot conversations."""
    query = db.query(AIConversation).filter(
        AIConversation.user_id == current_user.id
    ).order_by(AIConversation.updated_at.desc())
    total = query.count()
    conversations = query.offset((page - 1) * page_size).limit(page_size).all()
    return AIConversationListResponse(
        conversations=conversations, total=total, page=page, page_size=page_size,
    )


@router.get("/conversations/{conversation_id}", response_model=AIConversationDetail)
def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a full conversation with all messages."""
    conv = db.query(AIConversation).filter(
        AIConversation.id == conversation_id,
        AIConversation.user_id == current_user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    messages = db.query(AIMessage).filter(
        AIMessage.conversation_id == conversation_id
    ).order_by(AIMessage.created_at.asc()).all()

    return AIConversationDetail(
        id=conv.id, user_id=conv.user_id, title=conv.title,
        created_at=conv.created_at, updated_at=conv.updated_at,
        messages=[AIMessageItem.model_validate(m) for m in messages],
    )


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a conversation and all its messages."""
    conv = db.query(AIConversation).filter(
        AIConversation.id == conversation_id,
        AIConversation.user_id == current_user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    db.delete(conv)
    db.commit()


# ─── Usage ────────────────────────────────────────────────────────────────────

@router.get("/usage", response_model=AIUsageResponse)
def get_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get today's AI chatbot usage statistics."""
    tracking = _get_or_create_usage(current_user.id, db)
    total_convs = db.query(AIConversation).filter(
        AIConversation.user_id == current_user.id
    ).count()
    total_msgs = db.query(AIMessage).join(AIConversation).filter(
        AIConversation.user_id == current_user.id
    ).count()

    return AIUsageResponse(
        daily_limit=DAILY_MSG_LIMIT,
        messages_today=tracking.message_count,
        remaining_today=_remaining_msgs(tracking),
        total_conversations=total_convs,
        total_messages=total_msgs,
        reset_at=_next_midnight_utc(),
    )
