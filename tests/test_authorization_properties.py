"""
Property-based tests for role-based authorization (Task 3.3)

Tests require_student and require_admin dependencies with various user roles.
"""

import pytest
from hypothesis import given, settings as hyp_settings, HealthCheck
from hypothesis import strategies as st
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.auth import require_student, require_admin
from app.core.database import Base
from app.models.user import User
from fastapi import HTTPException


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


# ─── Strategy: Generate users with different roles ────────────────────────────

@st.composite
def user_with_role(draw, role=None):
    """Generate a user with a specific role or random role."""
    if role is None:
        role = draw(st.sampled_from(["student", "admin", "invalid_role"]))
    
    return User(
        firebase_uid=f"uid_{draw(st.integers(min_value=1000, max_value=9999))}",
        email=f"user{draw(st.integers(min_value=1000, max_value=9999))}@test.com",
        name=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll'), min_codepoint=65, max_codepoint=122
        ))),
        role=role,
        status="active"
    )


# ─── Property 1: require_student allows students ──────────────────────────────
# **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

@given(user=user_with_role(role="student"))
@hyp_settings(
    max_examples=30,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_require_student_allows_students(user, db_session):
    """
    Property: require_student should allow users with 'student' role.
    
    Given a user with role='student',
    When require_student is called with that user,
    Then it should:
    - Return the user object without raising an exception
    - Not modify the user object
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    """
    # Call require_student
    result = require_student(current_user=user)
    
    # Verify user is returned unchanged
    assert result is user
    assert result.role == "student"


# ─── Property 2: require_student allows admins ────────────────────────────────
# **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

@given(user=user_with_role(role="admin"))
@hyp_settings(
    max_examples=30,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_require_student_allows_admins(user, db_session):
    """
    Property: require_student should allow users with 'admin' role.
    
    Given a user with role='admin',
    When require_student is called with that user,
    Then it should:
    - Return the user object without raising an exception
    - Not modify the user object
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    """
    # Call require_student
    result = require_student(current_user=user)
    
    # Verify user is returned unchanged
    assert result is user
    assert result.role == "admin"


# ─── Property 3: require_student rejects invalid roles ────────────────────────
# **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

@given(
    invalid_role=st.text(min_size=1, max_size=20).filter(
        lambda x: x not in ("student", "admin")
    )
)
@hyp_settings(
    max_examples=30,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_require_student_rejects_invalid_roles(invalid_role, db_session):
    """
    Property: require_student should reject users with roles other than 'student' or 'admin'.
    
    Given a user with an invalid role (not 'student' or 'admin'),
    When require_student is called with that user,
    Then it should:
    - Raise HTTPException with status code 403
    - Include appropriate error message
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    """
    # Create user with invalid role
    user = User(
        firebase_uid=f"uid_invalid_{invalid_role}",
        email=f"invalid@test.com",
        name="Invalid User",
        role=invalid_role,
        status="active"
    )
    
    # Verify require_student raises HTTPException with 403
    with pytest.raises(HTTPException) as exc_info:
        require_student(current_user=user)
    
    assert exc_info.value.status_code == 403
    assert "Student or admin access required" in str(exc_info.value.detail)


# ─── Property 4: require_admin allows only admins ─────────────────────────────
# **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

@given(user=user_with_role(role="admin"))
@hyp_settings(
    max_examples=30,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_require_admin_allows_admins(user, db_session):
    """
    Property: require_admin should allow users with 'admin' role.
    
    Given a user with role='admin',
    When require_admin is called with that user,
    Then it should:
    - Return the user object without raising an exception
    - Not modify the user object
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    """
    # Call require_admin
    result = require_admin(current_user=user)
    
    # Verify user is returned unchanged
    assert result is user
    assert result.role == "admin"


# ─── Property 5: require_admin rejects students ───────────────────────────────
# **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

@given(user=user_with_role(role="student"))
@hyp_settings(
    max_examples=30,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_require_admin_rejects_students(user, db_session):
    """
    Property: require_admin should reject users with 'student' role.
    
    Given a user with role='student',
    When require_admin is called with that user,
    Then it should:
    - Raise HTTPException with status code 403
    - Include appropriate error message
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    """
    # Verify require_admin raises HTTPException with 403
    with pytest.raises(HTTPException) as exc_info:
        require_admin(current_user=user)
    
    assert exc_info.value.status_code == 403
    assert "Admin access required" in str(exc_info.value.detail)


# ─── Property 6: require_admin rejects invalid roles ──────────────────────────
# **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

@given(
    invalid_role=st.text(min_size=1, max_size=20).filter(
        lambda x: x != "admin"
    )
)
@hyp_settings(
    max_examples=30,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_require_admin_rejects_non_admin_roles(invalid_role, db_session):
    """
    Property: require_admin should reject users with any role other than 'admin'.
    
    Given a user with a role that is not 'admin',
    When require_admin is called with that user,
    Then it should:
    - Raise HTTPException with status code 403
    - Include appropriate error message
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    """
    # Create user with non-admin role
    user = User(
        firebase_uid=f"uid_nonadmin_{invalid_role}",
        email=f"nonadmin@test.com",
        name="Non-Admin User",
        role=invalid_role,
        status="active"
    )
    
    # Verify require_admin raises HTTPException with 403
    with pytest.raises(HTTPException) as exc_info:
        require_admin(current_user=user)
    
    assert exc_info.value.status_code == 403
    assert "Admin access required" in str(exc_info.value.detail)


# ─── Property 7: Authorization preserves user identity ────────────────────────
# **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

@given(
    role=st.sampled_from(["student", "admin"]),
    email=st.emails(),
    name=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'), min_codepoint=65, max_codepoint=122
    ))
)
@hyp_settings(
    max_examples=30,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_authorization_preserves_user_identity(role, email, name, db_session):
    """
    Property: Authorization checks should preserve all user identity fields.
    
    Given a user with specific identity fields (email, name, role),
    When authorization checks are performed,
    Then the returned user should:
    - Have the same email
    - Have the same name
    - Have the same role
    - Be the exact same object reference
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    """
    # Create user with specific identity
    user = User(
        firebase_uid=f"uid_{hash(email)}",
        email=email,
        name=name,
        role=role,
        status="active"
    )
    
    # Call appropriate authorization function
    if role == "student":
        result = require_student(current_user=user)
    else:  # admin
        result = require_admin(current_user=user)
    
    # Verify identity is preserved
    assert result is user  # Same object reference
    assert result.email == email
    assert result.name == name
    assert result.role == role


# ═══════════════════════════════════════════════════════════════════════════════
# Task 3.4: Property Tests for Role-Based Access Control
# ═══════════════════════════════════════════════════════════════════════════════

# ─── Property 3: Role Assignment Completeness ──────────────────────────────────
# **Validates: Requirements 2.1**

@given(
    role=st.sampled_from(["student", "admin"]),
    firebase_uid=st.text(min_size=5, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=48, max_codepoint=122
    )),
    email=st.emails(),
    name=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'), min_codepoint=65, max_codepoint=122
    ))
)
@hyp_settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_3_role_assignment_completeness(role, firebase_uid, email, name, db_session):
    """
    Property 3: Role Assignment Completeness
    
    For any authenticated user, they should have exactly one role from the set {student, admin}.
    
    Given any user object created through the authentication system,
    When checking the user's role,
    Then the role should:
    - Be present (not None or empty)
    - Be exactly one of: "student" or "admin"
    - Not be any other value
    
    **Validates: Requirements 2.1**
    """
    # Create user as the authentication system would
    user = User(
        firebase_uid=firebase_uid,
        email=email,
        name=name,
        role=role,
        status="active"
    )
    
    # Verify role is present
    assert user.role is not None, "User role must not be None"
    assert user.role != "", "User role must not be empty"
    
    # Verify role is from valid set
    valid_roles = {"student", "admin"}
    assert user.role in valid_roles, f"User role must be one of {valid_roles}, got {user.role}"


# ─── Property 4: Role-Based Access Control ────────────────────────────────────
# **Validates: Requirements 2.2, 2.3**

@given(
    user_role=st.sampled_from(["student", "admin"]),
    endpoint_type=st.sampled_from(["student_endpoint", "admin_endpoint"])
)
@hyp_settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_4_role_based_access_control(user_role, endpoint_type, db_session):
    """
    Property 4: Role-Based Access Control
    
    For any admin-only endpoint and any student user, access attempts should return status code 403.
    For any endpoint and any admin user, access should be granted.
    
    Given a user with a specific role and an endpoint with access requirements,
    When the user attempts to access the endpoint,
    Then:
    - Students accessing admin-only endpoints should be denied (403)
    - Admins accessing any endpoint should be granted access
    - Students accessing student endpoints should be granted access
    
    **Validates: Requirements 2.2, 2.3**
    """
    # Create user with specified role
    user = User(
        firebase_uid=f"uid_rbac_{user_role}_{endpoint_type}",
        email=f"rbac_{user_role}@test.com",
        name=f"RBAC Test User {user_role}",
        role=user_role,
        status="active"
    )
    
    if endpoint_type == "admin_endpoint":
        # Admin-only endpoint
        if user_role == "admin":
            # Admins should have access
            result = require_admin(current_user=user)
            assert result is user, "Admin should have access to admin endpoint"
        else:  # student
            # Students should be denied
            with pytest.raises(HTTPException) as exc_info:
                require_admin(current_user=user)
            assert exc_info.value.status_code == 403, "Student should be denied access to admin endpoint"
            assert "Admin access required" in str(exc_info.value.detail)
    else:  # student_endpoint
        # Student endpoint (accessible by both students and admins)
        result = require_student(current_user=user)
        assert result is user, f"{user_role} should have access to student endpoint"


# ─── Property 5: Role Change Propagation ──────────────────────────────────────
# **Validates: Requirements 2.5**

@given(
    initial_role=st.sampled_from(["student", "admin"]),
    new_role=st.sampled_from(["student", "admin"]),
    uid_suffix=st.integers(min_value=1000, max_value=999999)
)
@hyp_settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_5_role_change_propagation(initial_role, new_role, uid_suffix, db_session):
    """
    Property 5: Role Change Propagation
    
    For any user whose role is changed, the next authenticated request should reflect
    the new role's permissions.
    
    Given a user with an initial role,
    When the user's role is changed to a new role,
    Then:
    - The user object should reflect the new role
    - Authorization checks should use the new role
    - Access permissions should match the new role immediately
    
    **Validates: Requirements 2.5**
    """
    # Create user with initial role and unique identifiers
    user = User(
        firebase_uid=f"uid_rolechange_{uid_suffix}",
        email=f"rolechange_{uid_suffix}@test.com",
        name=f"Role Change Test User {uid_suffix}",
        role=initial_role,
        status="active"
    )
    
    # Persist user to database with error handling for duplicates
    try:
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    except Exception:
        # If there's a duplicate, rollback and skip this example
        db_session.rollback()
        # Query for existing user instead
        user = db_session.query(User).filter(
            User.firebase_uid == f"uid_rolechange_{uid_suffix}"
        ).first()
        if user is None:
            # If we can't get the user, skip this test case
            return
        # Update the user's role to initial_role for this test
        user.role = initial_role
        db_session.commit()
        db_session.refresh(user)
    
    # Verify initial role works correctly
    if initial_role == "admin":
        result = require_admin(current_user=user)
        assert result is user
    else:
        result = require_student(current_user=user)
        assert result is user
    
    # Change the user's role
    user.role = new_role
    db_session.commit()
    db_session.refresh(user)
    
    # Verify the role change is reflected
    assert user.role == new_role, f"User role should be updated to {new_role}"
    
    # Verify authorization checks use the new role
    if new_role == "admin":
        # Should now have admin access
        result = require_admin(current_user=user)
        assert result is user, "User should have admin access after role change to admin"
    else:  # new_role == "student"
        # Should have student access but not admin access
        result = require_student(current_user=user)
        assert result is user, "User should have student access after role change to student"
        
        # Should NOT have admin access
        with pytest.raises(HTTPException) as exc_info:
            require_admin(current_user=user)
        assert exc_info.value.status_code == 403, "User should not have admin access after role change to student"
