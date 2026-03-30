"""
Session management for ScholarGrid Backend API

Provides session-based authentication using secure HTTP-only cookies.
"""

from typing import Optional
from fastapi import Request, Response, HTTPException, status
from sqlalchemy.orm import Session
import secrets
import hashlib
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User

# In-memory session store (for development - use Redis in production)
_sessions = {}

SESSION_COOKIE_NAME = "scholargrid_session"
SESSION_EXPIRY_DAYS = 7


def create_session(user_id: str, role: str) -> str:
    """Create a new session and return session ID"""
    session_id = secrets.token_urlsafe(32)
    _sessions[session_id] = {
        "user_id": user_id,
        "role": role,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=SESSION_EXPIRY_DAYS)
    }
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    """Get session data by session ID"""
    session = _sessions.get(session_id)
    if not session:
        return None
    
    # Check if session expired
    if session["expires_at"] < datetime.utcnow():
        del _sessions[session_id]
        return None
    
    return session


def delete_session(session_id: str):
    """Delete a session"""
    if session_id in _sessions:
        del _sessions[session_id]


def set_session_cookie(response: Response, session_id: str):
    """Set session cookie in response"""
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=SESSION_EXPIRY_DAYS * 24 * 60 * 60
    )


def clear_session_cookie(response: Response):
    """Clear session cookie from response"""
    response.delete_cookie(key=SESSION_COOKIE_NAME)


def get_session_user(request: Request, db: Session) -> Optional[User]:
    """Get user from session cookie"""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        return None
    
    session = get_session(session_id)
    if not session:
        return None
    
    user = db.query(User).filter(User.id == session["user_id"]).first()
    return user
