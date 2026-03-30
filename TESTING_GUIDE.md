# Testing Guide - Integration Branch

This guide will help you test the integrated frontend and backend on the `integration` branch.

## Current Status

✅ Backend session-based authentication implemented
✅ Frontend ThemeContext added
✅ API routes configured for frontend compatibility
✅ CORS configured for local development

## Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** and npm installed
3. **PostgreSQL** running on localhost:5432
4. **Redis** running on localhost:6379 (optional for development)

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Start all services (PostgreSQL, Redis, Backend API)
docker-compose up -d

# The backend will be available at http://localhost:8000
```

### Option 2: Manual Setup

#### 1. Start Backend (Port 5000)

```bash
# Install Python dependencies (if not already installed)
pip install -e .

# Run the backend on port 5000 (to match frontend config)
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

The backend will be available at: http://localhost:5000

#### 2. Start Frontend (Port 5173)

Open a new terminal:

```bash
# Install frontend dependencies (if not already installed)
npm install

# Start the frontend dev server
npm run dev
```

The frontend will be available at: http://localhost:5173

## Testing Authentication

### 1. Admin Login

1. Go to http://localhost:5173
2. Click "Admin Login" or navigate to the admin login page
3. Use these credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
4. You should be logged in as an admin

### 2. Student Login (Google)

1. Go to http://localhost:5173
2. Click "Student Login" or the Google login button
3. Enter any name and email (no real Google auth required)
4. You should be logged in as a student

### 3. Session Persistence

1. After logging in, refresh the page
2. You should remain logged in (session cookie persists)

### 4. Logout

1. Click the logout button
2. You should be logged out and redirected to the login page

## API Endpoints

The backend now supports both URL patterns for backward compatibility:

- `/api/auth/session` - Check session status
- `/api/auth/admin-login` - Admin login
- `/api/auth/google` - Student Google login
- `/api/auth/logout` - Logout
- `/api/v1/auth/*` - All original endpoints still work

## Testing with cURL

### Check Session
```bash
curl -X GET http://localhost:5000/api/auth/session \
  -H "Content-Type: application/json" \
  --cookie-jar cookies.txt \
  --cookie cookies.txt
```

### Admin Login
```bash
curl -X POST http://localhost:5000/api/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  --cookie-jar cookies.txt \
  --cookie cookies.txt
```

### Student Login
```bash
curl -X POST http://localhost:5000/api/auth/google \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com"}' \
  --cookie-jar cookies.txt \
  --cookie cookies.txt
```

### Logout
```bash
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Content-Type: application/json" \
  --cookie-jar cookies.txt \
  --cookie cookies.txt
```

## Common Issues

### Issue: Backend runs on port 8000 instead of 5000

**Solution**: Make sure you're running the backend with `--port 5000`:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

### Issue: CORS errors in browser console

**Solution**: Check that:
1. Backend is running on port 5000
2. Frontend is running on port 5173
3. `.env` file has `CORS_ORIGINS=http://localhost:3000,http://localhost:5173`

### Issue: "Failed to resolve import" errors

**Solution**: Make sure all frontend dependencies are installed:
```bash
npm install
```

### Issue: Database connection errors

**Solution**: 
1. Make sure PostgreSQL is running
2. Check the `DATABASE_URL` in `.env` file
3. Run migrations: `python scripts/run_migrations.py`

### Issue: Redis connection errors

**Solution**: Redis is optional for development. The session system will use in-memory storage if Redis is not available.

## Next Steps

After confirming everything works:

1. Test all authentication flows
2. Test session persistence across page refreshes
3. Test logout functionality
4. Test that protected routes work correctly
5. Push changes to GitHub: `git push origin integration`

## Production Notes

⚠️ **Important**: The current session implementation uses in-memory storage, which is suitable for development but NOT for production.

For production, you need to:
1. Implement Redis-based session storage
2. Use secure session cookies (HTTPS only)
3. Set proper session expiry times
4. Implement session cleanup/garbage collection
