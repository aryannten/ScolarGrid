# ScholarGrid Backend API — Deployment Guide

## Quick Start (Local Development)

```bash
# 1. Clone and enter project
cd ScolarGrid

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate    # Windows
source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -e .

# 4. Copy and configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL, REDIS_URL, FIREBASE_CREDENTIALS_PATH, GEMINI_API_KEY

# 5. Verify configuration
python scripts/verify_env.py

# 6. Run migrations
alembic upgrade head

# 7. (Optional) Seed admin user
ADMIN_FIREBASE_UID=your-uid ADMIN_EMAIL=admin@yourschool.com python scripts/seed_admin.py

# 8. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Docker (Recommended for Production)

```bash
# Start all services (API + PostgreSQL + Redis + auto-migrate)
docker compose up -d

# View logs
docker compose logs -f api

# Stop all services
docker compose down

# Stop and remove volumes (CAUTION: deletes all data)
docker compose down -v
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | `postgresql+psycopg://user:pass@host:5432/db` |
| `REDIS_URL` | ✅ | `redis://host:6379/0` |
| `FIREBASE_CREDENTIALS_PATH` | ✅ | Path to Firebase service account JSON |
| `GEMINI_API_KEY` | ✅ prod | Google Gemini API key |
| `SECRET_KEY` | ✅ prod | Min 32-char secret for JWT signing |
| `CORS_ORIGINS` | ✅ | Comma-separated allowed origins |
| `ENVIRONMENT` | ❌ | `development` (default) or `production` |
| `RATE_LIMIT` | ❌ | Requests per user per minute (default: 100) |

---

## Database Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Check current migration version
alembic current

# Generate new migration (after model changes)
alembic revision --autogenerate -m "description_here"

# Rollback one step
alembic downgrade -1
```

---

## Running Tests

```bash
# All tests with coverage
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Only unit tests (fast, no external services)
python -m pytest tests/ -m "not integration" -v

# Only integration tests
python -m pytest tests/ -m integration -v

# Only property-based tests (Hypothesis)
python -m pytest tests/ -m property -v

# Single file
python -m pytest tests/test_ai_chatbot_models.py -v
```

---

## API Documentation

Once running, navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Health Check

```bash
curl http://localhost:8000/health
# Returns: {"status":"healthy","database":"connected","redis":"connected","timestamp":"..."}
```

---

## Performance Considerations (Task 30)

| Area | Recommendation |
|---|---|
| DB Indexes | All FK columns indexed; composite index on `(user_id, date)` for AI usage |
| Caching | Leaderboard (5 min), Analytics (10 min), User profiles (15 min), Notes (10 min) |
| Pagination | All list endpoints paginated; default page_size = 20, max = 100 |
| Connection pooling | SQLAlchemy: pool_size=10, max_overflow=20, pool_recycle=3600 |
| Redis | maxmemory=256mb, allkeys-lru eviction policy |
| Uvicorn | 4 workers in production; scale with `--workers` based on CPU count |

---

## Scaling

- **Horizontal**: Run multiple API containers behind a load balancer (nginx, Caddy, AWS ALB)
- **DB**: Use PostgreSQL read replicas for heavy read workloads
- **Socket.io**: Use `python-socketio` Redis adapter for multi-process real-time support
- **File storage**: Firebase Storage auto-scales; no action needed
