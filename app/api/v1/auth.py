"""
Authentication and user profile routes for ScholarGrid Backend API

Handles user registration, profile retrieval, and profile updates.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.schemas import UserRegisterRequest, UserUpdateRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Cache TTL for user profiles (15 minutes)
PROFILE_CACHE_TTL = 900


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    body: UserRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Register or update a user profile from a Firebase token.

    Creates a new user record if not already present, or updates name/avatar
    for existing users. Student statistics are initialized to zero on first registration.
    """
    current_user.name = body.name
    if body.avatar_url is not None:
        current_user.avatar_url = body.avatar_url
    if body.about is not None:
        current_user.about = body.about

    db.commit()
    db.refresh(current_user)

    # Invalidate cache after update
    try:
        from app.services.redis_service import invalidate_pattern
        invalidate_pattern(f"user:profile:{current_user.id}")
    except Exception:
        pass

    # Track registration activity
    try:
        from app.services.activity_service import create_activity
        create_activity(
            db=db,
            activity_type="user_registration",
            user_id=current_user.id,
            entity_id=current_user.id,
        )
    except Exception:
        pass

    return current_user


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the authenticated user's full profile including statistics.

    Response is cached in Redis for 15 minutes.
    """
    cache_key = f"user:profile:{current_user.id}"
    try:
        from app.services.redis_service import get_cache, set_cache
        cached = get_cache(cache_key)
        if cached:
            return cached
    except Exception:
        pass

    result = UserResponse.model_validate(current_user)
    try:
        from app.services.redis_service import set_cache
        set_cache(cache_key, result.model_dump(mode="json"), ttl=PROFILE_CACHE_TTL)
    except Exception:
        pass
    return result


@router.put("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdateRequest,
    avatar: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the authenticated user's profile (name, about, avatar)."""
    if body.name is not None:
        current_user.name = body.name
    if body.about is not None:
        current_user.about = body.about

    if avatar is not None:
        try:
            from app.services.firebase_service import upload_file_to_storage, ALLOWED_EXTENSIONS
            url, _, _ = await upload_file_to_storage(avatar, "avatars/", ALLOWED_EXTENSIONS["avatars"])
            current_user.avatar_url = url
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Avatar upload failed: {str(e)}")

    db.commit()
    db.refresh(current_user)

    try:
        from app.services.redis_service import invalidate_pattern
        invalidate_pattern(f"user:profile:{current_user.id}")
    except Exception:
        pass

    return current_user
