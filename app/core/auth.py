"""
Authentication dependencies for ScholarGrid Backend API

Provides Firebase token verification and user context injection for FastAPI routes.
Handles user creation/update on first login, and enforces suspended user blocking.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Verify Firebase ID token and return the authenticated user.

    Creates a new user record if this is the first login, or retrieves
    the existing user otherwise. Blocks suspended accounts.

    Args:
        credentials: Bearer token from Authorization header
        db: Database session

    Returns:
        User: The authenticated user ORM object

    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        HTTPException 401: If user account is suspended
    """
    token = credentials.credentials

    try:
        from app.services.firebase_service import verify_firebase_token
        decoded_token = await verify_firebase_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    firebase_uid = decoded_token.get("uid")
    email = decoded_token.get("email", "")

    # Look up existing user by firebase_uid
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()

    if user is None:
        # Auto-create user record on first authenticated request
        name = decoded_token.get("name") or email.split("@")[0]
        avatar_url = decoded_token.get("picture")
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            name=name,
            avatar_url=avatar_url,
            role="student",
            status="active",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update email/name if changed in Firebase
        updated = False
        if email and user.email != email:
            user.email = email
            updated = True
        if updated:
            db.commit()
            db.refresh(user)

    # Block suspended users
    if user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your account has been suspended. Please contact support.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_student(current_user: User = Depends(get_current_user)) -> User:
    """
    Require the current user to have student or admin role.

    Returns:
        User: The currently authenticated user

    Raises:
        HTTPException 403: If user role is not student or admin
    """
    if current_user.role not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student or admin access required.",
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require the current user to have admin role.

    Returns:
        User: The currently authenticated admin user

    Raises:
        HTTPException 403: If user role is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user
