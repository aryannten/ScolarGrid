"""
Authentication and user profile routes for ScholarGrid Backend API

Handles user registration, profile retrieval, and profile updates.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.schemas import UserRegisterRequest, UserUpdateRequest, UserProfileResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Cache TTL for user profiles (15 minutes)
PROFILE_CACHE_TTL = 900


# ─── TEST ENDPOINT (NO FIREBASE REQUIRED) ────────────────────────────────────
@router.post(
    "/test-register",
    response_model=UserResponse,
    status_code=201,
    openapi_extra={"security": []},
)
async def test_register(
    email: str,
    name: str,
    db: Session = Depends(get_db),
):
    """
    TEST ONLY: Create a user without Firebase authentication.
    This bypasses Firebase and creates a user directly in the database.
    """
    import uuid
    
    # Check if user exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return existing
    
    # Create test user
    user = User(
        firebase_uid=f"test-{uuid.uuid4()}",
        email=email,
        name=name,
        role="student",
        status="active",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


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


@router.get("/me", response_model=UserProfileResponse)
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

    result = UserProfileResponse.model_validate(current_user)
    try:
        from app.services.redis_service import set_cache
        set_cache(cache_key, result.model_dump(mode="json"), ttl=PROFILE_CACHE_TTL)
    except Exception:
        pass
    return result


@router.put(
    "/me",
    response_model=UserProfileResponse,
    openapi_extra={
        "requestBody": {
            "required": False,
            "content": {
                "application/json": {"schema": UserUpdateRequest.model_json_schema()},
                "application/x-www-form-urlencoded": {
                    "schema": UserUpdateRequest.model_json_schema()
                },
                "multipart/form-data": {"schema": UserUpdateRequest.model_json_schema()},
            },
        }
    },
)
async def update_me(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the authenticated user's profile (name, about, avatar_url)."""
    body = None
    content_type = request.headers.get("content-type", "")

    try:
        if "application/json" in content_type:
            payload = await request.json()
            body = UserUpdateRequest.model_validate(payload)
        elif (
            "application/x-www-form-urlencoded" in content_type
            or "multipart/form-data" in content_type
        ):
            form = await request.form()
            body = UserUpdateRequest.model_validate(dict(form))
        else:
            payload = await request.body()
            if payload:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Unsupported content type for profile update.",
                )
            body = UserUpdateRequest()
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc

    if body.name is not None:
        current_user.name = body.name
    if body.about is not None:
        current_user.about = body.about
    if body.avatar_url is not None:
        current_user.avatar_url = body.avatar_url

    db.commit()
    db.refresh(current_user)

    try:
        from app.services.redis_service import invalidate_pattern
        invalidate_pattern(f"user:profile:{current_user.id}")
    except Exception:
        pass

    return current_user
