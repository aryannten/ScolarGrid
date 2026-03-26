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
| `CLOUDINARY_CLOUD_NAME` | ✅ | Cloudinary cloud name for file storage |
| `CLOUDINARY_API_KEY` | ✅ | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | ✅ | Cloudinary API secret |
| `SENTRY_DSN` | ❌ | Sentry DSN for error tracking (recommended for production) |
| `ENABLE_METRICS` | ❌ | Enable Prometheus metrics (default: false) |
| `LOG_LEVEL` | ❌ | Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO) |

### Production Environment Setup

For production deployment, use `.env.production.template` as a starting point:

```bash
# Copy production template
cp .env.production.template .env

# Edit with your production values
nano .env  # or vim, code, etc.
```

**Production Checklist:**
- ✓ `SECRET_KEY` is a secure random string (min 32 chars)
- ✓ `DATABASE_URL` points to production database (not localhost)
- ✓ `REDIS_URL` points to production Redis (not localhost)
- ✓ `CORS_ORIGINS` contains only HTTPS URLs (no localhost)
- ✓ `SENTRY_DSN` is configured for error tracking
- ✓ All passwords are strong and unique
- ✓ Firebase credentials file is securely mounted
- ✓ SSL/TLS certificates are valid

---

## Production Logging

The application uses structured JSON logging in production for easy parsing and analysis.

### Log Format

**Production (JSON):**
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "scholargrid.api",
  "message": "GET /api/v1/notes → 200 [45.2ms]",
  "method": "GET",
  "path": "/api/v1/notes",
  "status_code": 200,
  "duration_ms": 45.2,
  "request_id": "abc123",
  "user_id": "user-uuid"
}
```

**Development (Human-readable):**
```
2024-01-15 10:30:45 | INFO     | scholargrid.api      | GET /api/v1/notes → 200 [45.2ms]
```

### Log Levels

- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages (default in production)
- `WARNING`: Warning messages for potentially harmful situations
- `ERROR`: Error messages for serious problems
- `CRITICAL`: Critical messages for very serious errors

### Viewing Logs

**Docker:**
```bash
# View all logs
docker compose logs -f api

# View last 100 lines
docker compose logs --tail=100 api

# View logs with timestamps
docker compose logs -f -t api
```

**Production (systemd):**
```bash
# View logs
journalctl -u scholargrid-api -f

# View logs with JSON formatting
journalctl -u scholargrid-api -o json-pretty
```

---

## Error Tracking (Sentry)

Sentry provides real-time error tracking and performance monitoring.

### Setup

1. Create a Sentry account at https://sentry.io
2. Create a new project for your API
3. Copy the DSN from project settings
4. Add to `.env`:
   ```
   SENTRY_DSN=https://your-key@sentry.io/project-id
   ```

### Features

- **Error Tracking**: Automatic capture of unhandled exceptions
- **Performance Monitoring**: Track API endpoint performance
- **Release Tracking**: Associate errors with specific releases
- **User Context**: Link errors to specific users
- **Breadcrumbs**: See the sequence of events leading to errors

### Installation

```bash
pip install sentry-sdk[fastapi]
```

### Viewing Errors

1. Log in to https://sentry.io
2. Navigate to your project
3. View errors, performance metrics, and alerts

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

## Monitoring and Alerting

### Health Checks

The API provides health check endpoints for monitoring:

```bash
# Basic health check
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

**Automated Health Checks:**
```bash
# Run health check script
python scripts/health_check.py

# Check remote API
python scripts/health_check.py --url https://api.example.com
```

### Metrics Endpoint

Basic metrics are available at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

For production monitoring, integrate with:
- **Prometheus**: Scrape `/metrics` endpoint
- **Grafana**: Visualize metrics and create dashboards
- **Datadog**: APM and infrastructure monitoring
- **New Relic**: Application performance monitoring

### Recommended Alerts

Set up alerts for:

1. **API Health**
   - Alert when `/health` returns non-200 status
   - Check interval: 1 minute
   - Alert threshold: 3 consecutive failures

2. **Database Connectivity**
   - Alert when database connection fails
   - Check via health endpoint
   - Alert threshold: 2 consecutive failures

3. **Redis Connectivity**
   - Alert when Redis connection fails
   - Check via health endpoint
   - Alert threshold: 2 consecutive failures

4. **Error Rate**
   - Alert when error rate > 5% of requests
   - Window: 5 minutes
   - Alert threshold: sustained for 2 minutes

5. **Response Time**
   - Alert when p95 latency > 1000ms
   - Window: 5 minutes
   - Alert threshold: sustained for 3 minutes

6. **Disk Space**
   - Alert when disk usage > 80%
   - Check interval: 5 minutes

7. **Memory Usage**
   - Alert when memory usage > 85%
   - Check interval: 1 minute

### Log Aggregation

For production, use a log aggregation service:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Datadog Logs**
- **CloudWatch Logs** (AWS)
- **Google Cloud Logging** (GCP)

**Example: Shipping logs to CloudWatch**
```bash
# Install CloudWatch agent
# Configure to tail Docker logs
# Logs will appear in CloudWatch Logs console
```

---

## Scaling

- **Horizontal**: Run multiple API containers behind a load balancer (nginx, Caddy, AWS ALB)
- **DB**: Use PostgreSQL read replicas for heavy read workloads
- **Socket.io**: Use `python-socketio` Redis adapter for multi-process real-time support
- **File storage**: Firebase Storage auto-scales; no action needed
