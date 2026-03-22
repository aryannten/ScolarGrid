"""
Property-based tests for token verification (Task 3.2)

Tests Firebase token verification round trip and invalid token rejection.
"""

import pytest
import uuid
from unittest.mock import patch, AsyncMock
from hypothesis import given, settings as hyp_settings, HealthCheck
from hypothesis import strategies as st
from firebase_admin import auth as firebase_auth
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.auth import get_current_user
from app.core.database import Base
from app.models.user import User
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


# ─── Database Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def test_engine():
    """Create a module-scoped in-memory SQLite engine."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    
    @event.listens_for(engine, "connect")
    def enable_fk(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")
    
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(test_engine):
    """Function-scoped DB session with transaction isolation."""
    from sqlalchemy.orm import Session
    
    connection = test_engine.connect()
    trans = connection.begin()
    
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    session.begin_nested()
    
    yield session
    
    session.close()
    trans.rollback()
    connection.close()


# ─── Strategy: Generate valid Firebase token payloads ─────────────────────────

@st.composite
def valid_token_payload(draw):
    """Generate a valid Firebase token payload structure with unique identifiers."""
    # Use UUID to ensure uniqueness across test runs
    unique_id = uuid.uuid4().hex
    uid = f"uid_{unique_id}"
    email = f"user_{unique_id}@test.com"
    name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), min_codepoint=32, max_codepoint=122
    )))
    
    return {
        "uid": uid,
        "email": email,
        "name": name,
        "email_verified": draw(st.booleans()),
        "picture": draw(st.one_of(st.none(), st.text(min_size=10, max_size=200)))
    }


# ─── Strategy: Generate invalid token scenarios ───────────────────────────────

@st.composite
def invalid_token_scenario(draw):
    """Generate different types of invalid token scenarios."""
    scenario_type = draw(st.sampled_from([
        "empty",
        "malformed",
        "expired",
        "revoked",
        "invalid_signature"
    ]))
    
    if scenario_type == "empty":
        return "", "empty"
    elif scenario_type == "malformed":
        return draw(st.text(min_size=1, max_size=50, alphabet="abc123")), "malformed"
    elif scenario_type == "expired":
        return "expired_token_" + draw(st.text(min_size=10, max_size=20)), "expired"
    elif scenario_type == "revoked":
        return "revoked_token_" + draw(st.text(min_size=10, max_size=20)), "revoked"
    else:  # invalid_signature
        return "invalid_sig_" + draw(st.text(min_size=10, max_size=20)), "invalid"


# ─── Property 1: Token Verification Round Trip ────────────────────────────────
# **Validates: Requirements 1.1, 1.2, 1.3, 1.5**

@given(token_payload=valid_token_payload())
@hyp_settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
async def test_property_valid_token_authenticates_and_returns_user(token_payload, db_session):
    """
    Property: Valid Firebase tokens should successfully authenticate and return user data.
    
    Given a valid Firebase token with user identity (uid, email, name),
    When the token is verified through get_current_user,
    Then the function should:
    - Successfully verify the token
    - Create or retrieve the user record
    - Return a User object with correct identity fields
    - Not raise any exceptions
    
    **Validates: Requirements 1.1, 1.2, 1.3, 1.5**
    """
    # Mock Firebase token verification to return our test payload
    with patch('app.services.firebase_service.verify_firebase_token', new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = token_payload
        
        # Create mock credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=f"valid_token_{uuid.uuid4().hex}"
        )
        
        # Call get_current_user
        user = await get_current_user(credentials=credentials, db=db_session)
        
        # Verify token was checked
        assert mock_verify.called
        
        # Verify user was created/retrieved
        assert user is not None
        assert isinstance(user, User)
        
        # Verify user identity matches token payload
        assert user.firebase_uid == token_payload["uid"]
        assert user.email == token_payload["email"]
        
        # Verify user has valid role and status
        assert user.role in ("student", "admin")
        assert user.status in ("active", "suspended")
        
        # Verify user was persisted to database
        db_user = db_session.query(User).filter(
            User.firebase_uid == token_payload["uid"]
        ).first()
        assert db_user is not None
        assert db_user.id == user.id


# ─── Property 2: Invalid Token Rejection ──────────────────────────────────────
# **Validates: Requirements 1.1, 1.2, 1.3, 1.5**

@given(invalid_scenario=invalid_token_scenario())
@hyp_settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
async def test_property_invalid_tokens_rejected_with_401(invalid_scenario, db_session):
    """
    Property: Invalid, expired, or malformed tokens should be rejected with 401.
    
    Given an invalid Firebase token (empty, malformed, expired, revoked, or invalid signature),
    When the token is verified through get_current_user,
    Then the function should:
    - Raise HTTPException with status code 401
    - Include appropriate error details
    - Not create any user records
    - Not allow authentication to proceed
    
    **Validates: Requirements 1.1, 1.2, 1.3, 1.5**
    """
    token, scenario_type = invalid_scenario
    
    # Count users before the test
    initial_user_count = db_session.query(User).count()
    
    # Mock Firebase token verification to raise appropriate exception
    with patch('app.services.firebase_service.verify_firebase_token', new_callable=AsyncMock) as mock_verify:
        # Configure mock to raise appropriate Firebase exception
        if scenario_type == "empty":
            mock_verify.side_effect = ValueError("Token cannot be empty")
        elif scenario_type == "expired":
            mock_verify.side_effect = firebase_auth.ExpiredIdTokenError(
                "Token has expired",
                cause=Exception("expired")
            )
        elif scenario_type == "revoked":
            mock_verify.side_effect = firebase_auth.RevokedIdTokenError(
                "Token has been revoked"
            )
        elif scenario_type in ("malformed", "invalid"):
            mock_verify.side_effect = firebase_auth.InvalidIdTokenError(
                "Invalid token"
            )
        
        # Create mock credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        # Verify that get_current_user raises HTTPException with 401
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=db_session)
        
        # Verify exception details
        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in str(exc_info.value.detail)
        
        # Verify no new user was created
        final_user_count = db_session.query(User).count()
        assert final_user_count == initial_user_count


# ─── Property: Suspended users are blocked ────────────────────────────────────
# **Validates: Requirements 1.5, 18.2**

@given(token_payload=valid_token_payload())
@hyp_settings(
    max_examples=30,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
async def test_property_suspended_users_blocked(token_payload, db_session):
    """
    Property: Suspended user accounts should be blocked from authentication.
    
    Given a valid Firebase token for a suspended user,
    When the token is verified through get_current_user,
    Then the function should:
    - Successfully verify the token
    - Retrieve the suspended user record
    - Raise HTTPException with status code 401
    - Include suspension message in error details
    
    **Validates: Requirements 1.5, 18.2**
    """
    # Create a suspended user with unique identifiers
    suspended_user = User(
        firebase_uid=token_payload["uid"],
        email=token_payload["email"],
        name=token_payload.get("name", "Test User"),
        role="student",
        status="suspended"
    )
    db_session.add(suspended_user)
    db_session.flush()  # Use flush instead of commit to stay in transaction
    
    # Mock Firebase token verification to return our test payload
    with patch('app.services.firebase_service.verify_firebase_token', new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = token_payload
        
        # Create mock credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=f"valid_token_{uuid.uuid4().hex}"
        )
        
        # Verify that get_current_user raises HTTPException with 401
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=db_session)
        
        # Verify exception details
        assert exc_info.value.status_code == 401
        assert "suspended" in str(exc_info.value.detail).lower()


# ─── Property: User auto-creation on first login ──────────────────────────────
# **Validates: Requirements 1.3**

@given(token_payload=valid_token_payload())
@hyp_settings(
    max_examples=30,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
async def test_property_user_auto_created_on_first_login(token_payload, db_session):
    """
    Property: New users should be auto-created on first authenticated request.
    
    Given a valid Firebase token for a user that doesn't exist in the database,
    When the token is verified through get_current_user,
    Then the function should:
    - Successfully verify the token
    - Create a new user record with default values
    - Set role to 'student'
    - Set status to 'active'
    - Initialize score to 0, tier to 'bronze', counts to 0
    - Return the newly created user
    
    **Validates: Requirements 1.3**
    """
    # Ensure user doesn't exist
    existing_user = db_session.query(User).filter(
        User.firebase_uid == token_payload["uid"]
    ).first()
    if existing_user:
        db_session.delete(existing_user)
        db_session.commit()
    
    # Mock Firebase token verification to return our test payload
    with patch('app.services.firebase_service.verify_firebase_token', new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = token_payload
        
        # Create mock credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=f"valid_token_{uuid.uuid4().hex}"
        )
        
        # Call get_current_user
        user = await get_current_user(credentials=credentials, db=db_session)
        
        # Verify user was created with correct defaults
        assert user is not None
        assert user.firebase_uid == token_payload["uid"]
        assert user.email == token_payload["email"]
        assert user.role == "student"
        assert user.status == "active"
        assert user.score == 0
        assert user.tier == "bronze"
        assert user.uploads_count == 0
        assert user.downloads_count == 0
        
        # Verify user was persisted
        db_user = db_session.query(User).filter(
            User.firebase_uid == token_payload["uid"]
        ).first()
        assert db_user is not None
        assert db_user.id == user.id
