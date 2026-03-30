# Quick Start Guide - Integration Branch

## What's Been Done

✅ Session-based authentication implemented
✅ 4 new authentication endpoints added
✅ Frontend-compatible API routes configured
✅ CORS configured for local development
✅ ThemeContext added to frontend

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL running on localhost:5432
- Redis running on localhost:6379 (optional for development)

## Quick Test (Recommended)

Run the automated integration test to verify everything works:

```bash
# Make sure backend is running first (see below)
python test_integration.py
```

This will test all authentication endpoints and verify the integration.

## Manual Setup

### 1. Start the Backend (Port 5000)

```bash
# Make sure you're on the integration branch
git checkout integration

# Install dependencies (if not already installed)
pip install -e .

# Run the backend on port 5000 (to match frontend config)
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

Backend will be available at: http://localhost:5000

**Important**: The backend MUST run on port 5000 (not 8000) to match the frontend configuration.

### 2. Start the Frontend (Port 5173)

Open a new terminal:

```bash
# Install frontend dependencies (if not already installed)
npm install

# Start the frontend dev server
npm run dev
```

Frontend will be available at: http://localhost:5173

### 3. Test in Browser

1. Open http://localhost:5173
2. Try admin login:
   - Username: `admin`
   - Password: `admin123`
3. Try student login:
   - Use any name and email (no real Google auth required)
   - Example: Name: "John Doe", Email: "john@example.com"
4. Test logout
5. Refresh the page to verify session persistence

## New Authentication Endpoints

1. **GET /api/auth/session** - Check current session status
2. **POST /api/auth/admin-login** - Admin login (username/password)
3. **POST /api/auth/google** - Student Google login (name/email)
4. **POST /api/auth/logout** - Clear session and logout

All endpoints support both `/api/auth/*` and `/api/v1/auth/*` for backward compatibility.

## API Documentation

Full API documentation is available at:
- http://localhost:5000/docs (Swagger UI)
- http://localhost:5000/redoc (ReDoc)

## Session Management

- Sessions are stored in-memory (development only)
- Session cookies are HTTP-only and secure
- Sessions expire after 7 days
- For production, implement Redis-based session storage

## Troubleshooting

### Backend not accessible from frontend

**Problem**: Frontend shows "Unable to reach the backend"

**Solution**: Make sure the backend is running on port 5000:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

### CORS Errors

**Problem**: Browser console shows CORS errors

**Solution**: Make sure the backend `.env` file has:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Import Errors in Frontend

**Problem**: "Failed to resolve import" errors

**Solution**: Install frontend dependencies:
```bash
npm install
```

### Database Connection Errors

**Problem**: Backend fails to start with database errors

**Solution**: 
1. Make sure PostgreSQL is running
2. Check the `DATABASE_URL` in `.env` file
3. Run migrations: `python scripts/run_migrations.py`

## Files Modified

- `app/core/session.py` - Session management system (NEW)
- `app/api/v1/auth.py` - New authentication endpoints
- `app/main.py` - Route aliases for frontend compatibility
- `src/context/ThemeContext.jsx` - Added missing context file (NEW)

## Next Steps

1. ✅ Test all authentication flows
2. Test other features (notes, chat, leaderboard, etc.)
3. Implement Redis-based session storage for production
4. Add comprehensive error handling
5. Write unit tests for new endpoints

## Need Help?

See `TESTING_GUIDE.md` for detailed testing instructions and troubleshooting.
