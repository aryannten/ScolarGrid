# Frontend-Backend Integration Issues

## Critical Issues Found

### 1. **MISSING ADMIN LOGIN ENDPOINT** ❌
**Severity:** CRITICAL

**Frontend Expectation:**
- Frontend calls `POST /api/auth/admin-login` with `{ username, password }`
- Location: `frontend-test/src/context/AuthContext.jsx` line 73

**Backend Reality:**
- No `/api/auth/admin-login` endpoint exists in  `app/api/v1/auth.py`
- Backend only has:
  - `POST /api/v1/auth/test-register` (test only)
  - `POST /api/v1/auth/register` (requires Firebase token)
  - `GET /api/v1/auth/me` (requires Firebase token)
  - `PUT /api/v1/auth/me` (requires Firebase token)

**Impact:**
- Admin login will fail with 404 Not Found
- Admins cannot access the system

**Solution Required:**
Create admin login endpoint that:
- Accepts username/password
- Validates against admin credentials (database or config)
- Returns session cookie or JWT
- Returns admin user data

---

### 2. **MISSING GOOGLE AUTH ENDPOINT** ❌
**Severity:** CRITICAL

**Frontend Expectation:**
- Frontend calls `POST /api/auth/google` with `{ name, email }`
- Location: `frontend-test/src/context/AuthContext.jsx` line 78

**Backend Reality:**
- No `/api/auth/google` endpoint exists
- Backend expects Firebase authentication via Bearer token

**Impact:**
- Student Google login will fail with 404 Not Found
- Students cannot access the system

**Solution Required:**
Create Google auth endpoint that:
- Accepts `{ name, email }` from frontend
- Creates or retrieves user from database
- Returns session cookie
- Returns user data

---

### 3. **MISSING LOGOUT ENDPOINT** ❌
**Severity:** HIGH

**Frontend Expectation:**
- Frontend calls `POST /api/auth/logout`
- Location: `frontend-test/src/context/AuthContext.jsx` line 86

**Backend Reality:**
- No `/api/auth/logout` endpoint exists

**Impact:**
- Logout will fail with 404 Not Found
- Sessions cannot be properly terminated

**Solution Required:**
Create logout endpoint that:
- Clears session cookie
- Returns success response

---

### 4. **MISSING SESSION ENDPOINT** ❌
**Severity:** CRITICAL

**Frontend Expectation:**
- Frontend calls `GET /api/auth/session` to check current session
- Location: `frontend-test/src/context/AuthContext.jsx` line 44

**Backend Reality:**
- No `/api/auth/session` endpoint exists
- Backend has `GET /api/v1/auth/me` but requires Firebase Bearer token

**Impact:**
- Session refresh will fail on page load
- Users will be logged out on every refresh

**Solution Required:**
Create session endpoint that:
- Checks session cookie
- Returns current user data if logged in
- Returns `{ logged_in: false }` if not logged in
- Supports both admin and student sessions

---

### 5. **API PATH MISMATCH** ⚠️
**Severity:** MEDIUM

**Frontend Configuration:**
- Base URL: `http://localhost:5000`
- Calls endpoints like `/api/auth/session`, `/api/auth/google`, etc.

**Backend Configuration:**
- API prefix: `/api/v1`
- Actual endpoints: `/api/v1/auth/register`, `/api/v1/auth/me`, etc.

**Impact:**
- Even if endpoints existed, paths would be wrong
- Frontend expects `/api/auth/*` but backend serves `/api/v1/auth/*`

**Solution Options:**
1. Change backend prefix from `/api/v1` to `/api` (breaking change)
2. Change frontend to use `/api/v1` prefix
3. Add route aliases in backend for backward compatibility

---

### 6. **AUTHENTICATION MECHANISM MISMATCH** ❌
**Severity:** CRITICAL

**Frontend Expectation:**
- Session-based authentication with cookies
- `credentials: 'include'` in all API requests
- No Bearer token required

**Backend Implementation:**
- Firebase Bearer token authentication
- All protected routes require `Authorization: Bearer <firebase-token>`
- No session/cookie support

**Impact:**
- Complete authentication incompatibility
- Frontend cannot authenticate with backend

**Solution Required:**
Backend needs dual authentication support:
1. Session-based auth for admin and Google login
2. Keep Firebase auth as optional alternative
3. Middleware to check both session cookie and Bearer token

---

## Summary of Required Backend Changes

### New Endpoints Needed:
1. `POST /api/auth/admin-login` - Admin username/password login
2. `POST /api/auth/google` - Google OAuth callback (simplified)
3. `POST /api/auth/logout` - Session termination
4. `GET /api/auth/session` - Current session check

### Authentication Changes Needed:
1. Add session management (Flask-Session or similar)
2. Add cookie-based authentication
3. Modify `get_current_user` to support both session and Firebase
4. Add admin credential storage/validation

### API Path Changes Needed:
1. Either change prefix to `/api` or update frontend to use `/api/v1`

---

## Testing Recommendations

After fixes are implemented, test:
1. Admin login flow
2. Student Google login flow
3. Session persistence across page refreshes
4. Logout functionality
5. Protected route access
6. CORS with credentials

---

## Current State Assessment

**Frontend:** ✅ Ready for session-based auth with proper error handling
**Backend:** ❌ Not compatible - requires significant authentication refactoring

The frontend has been properly updated to work with a session-based backend, but the backend still only supports Firebase Bearer token authentication. The two systems are currently incompatible.
