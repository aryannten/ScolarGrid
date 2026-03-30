# Quick Start Guide - Integration Branch

## Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL running
- Redis running (optional, will warn if not available)

## Backend Setup

1. **Install Python dependencies:**
```bash
pip install -e .
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. **Run database migrations:**
```bash
alembic upgrade head
```

4. **Start backend server:**
```bash
python -m uvicorn app.main:app --reload --port 5000
```

Backend will be available at: http://localhost:5000

## Frontend Setup

1. **Install Node dependencies:**
```bash
npm install
```

2. **Start frontend dev server:**
```bash
npm run dev
```

Frontend will be available at: http://localhost:5173

## Test the Integration

### Admin Login
1. Go to http://localhost:5173/login
2. Click "Admin" tab
3. Username: `admin`
4. Password: `admin123`
5. Click "Sign In"
6. You should be redirected to admin dashboard

### Student Login
1. Go to http://localhost:5173/login
2. Click "Student" tab
3. Enter any name (e.g., "John Doe")
4. Enter any email (e.g., "john@example.com")
5. Click "Continue with Google"
6. You should be redirected to student dashboard

## Verify It's Working

✅ No 404 errors on login
✅ Session persists on page refresh
✅ Logout works
✅ Protected routes are accessible after login
✅ Backend logs show successful authentication

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Run migrations: `alembic upgrade head`

### Frontend won't start
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check port 5173 is not in use

### Login fails with 404
- Verify backend is running on port 5000
- Check VITE_API_BASE_URL in frontend .env

### CORS errors
- Verify CORS_ORIGINS in backend .env includes http://localhost:5173

## API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc
