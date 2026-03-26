# ScholarGrid Backend API — Quick Reference

Quick commands for common deployment and maintenance tasks.

## Local Development

```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Verify environment
python scripts/verify_env.py
```

## Docker Commands

```bash
# Build image
docker build -t scholargrid-api:latest .

# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f api

# Restart API service
docker compose restart api

# Run migrations in container
docker compose exec api alembic upgrade head

# Create admin user in container
docker compose exec api python scripts/seed_admin.py

# Shell into container
docker compose exec api bash
```

## Database Operations

```bash
# Connect to database
psql $DATABASE_URL

# Backup database
pg_dump $DATABASE_URL > backup.sql

# Restore database
psql $DATABASE_URL < backup.sql

# Check migration status
alembic current

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision>
```

## Health Checks

```bash
# Local health check
curl http://localhost:8000/health

# Remote health check
python scripts/health_check.py --url https://api.example.com

# Check API version
curl http://localhost:8000/

# View metrics
curl http://localhost:8000/metrics
```

## Monitoring

```bash
# View application logs (Docker)
docker compose logs -f api

# View last 100 log lines
docker compose logs --tail=100 api

# View logs with timestamps
docker compose logs -f -t api

# View PostgreSQL logs
docker compose logs -f postgres

# View Redis logs
docker compose logs -f redis
```

## Troubleshooting

```bash
# Check container status
docker compose ps

# Check container resource usage
docker stats

# Inspect container
docker compose exec api env

# Test database connection
docker compose exec api python -c "from app.core.database import check_db_connection; print(check_db_connection())"

# Test Redis connection
docker compose exec api python -c "from app.services.redis_service import check_redis_connection; print(check_redis_connection())"

# Clear Redis cache
docker compose exec redis redis-cli FLUSHALL
```

## Production Deployment

```bash
# Pull latest code
git pull origin main

# Build production image
docker build -t scholargrid-api:v1.0.0 .

# Tag for registry
docker tag scholargrid-api:v1.0.0 registry.example.com/scholargrid-api:v1.0.0

# Push to registry
docker push registry.example.com/scholargrid-api:v1.0.0

# Deploy with docker-compose
docker compose -f docker-compose.prod.yml up -d

# Run migrations
docker compose exec api alembic upgrade head

# Verify deployment
python scripts/health_check.py --url https://api.example.com
```

## Scaling

```bash
# Scale API containers (Docker Swarm)
docker service scale scholargrid_api=4

# Scale API containers (Kubernetes)
kubectl scale deployment scholargrid-api --replicas=4

# Update Uvicorn workers
# Edit docker-compose.yml or Dockerfile CMD:
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Backup and Restore

```bash
# Backup database
docker compose exec postgres pg_dump -U scholargrid scholargrid > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker compose exec -T postgres psql -U scholargrid scholargrid < backup.sql

# Backup Redis data
docker compose exec redis redis-cli SAVE
docker cp scholargrid_redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d_%H%M%S).rdb

# Restore Redis data
docker cp redis_backup.rdb scholargrid_redis:/data/dump.rdb
docker compose restart redis
```

## Security

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check for security vulnerabilities
pip install safety
safety check

# Update dependencies
pip install --upgrade -r requirements.txt

# Scan Docker image for vulnerabilities
docker scan scholargrid-api:latest
```

## Performance

```bash
# Check database query performance
docker compose exec postgres psql -U scholargrid -d scholargrid -c "SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;"

# Check Redis memory usage
docker compose exec redis redis-cli INFO memory

# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Load test with Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health
```

## Useful SQL Queries

```sql
-- Count users by role
SELECT role, COUNT(*) FROM users GROUP BY role;

-- Count notes by status
SELECT status, COUNT(*) FROM notes GROUP BY status;

-- Top uploaders
SELECT u.name, u.uploads_count FROM users u ORDER BY uploads_count DESC LIMIT 10;

-- Recent activity
SELECT * FROM activities ORDER BY created_at DESC LIMIT 20;

-- Database size
SELECT pg_size_pretty(pg_database_size('scholargrid'));

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Environment Variables Quick Reference

| Variable | Example |
|----------|---------|
| `DATABASE_URL` | `postgresql+psycopg://user:pass@host:5432/db` |
| `REDIS_URL` | `redis://host:6379/0` |
| `FIREBASE_CREDENTIALS_PATH` | `/app/firebase-credentials.json` |
| `GEMINI_API_KEY` | `AIza...` |
| `SECRET_KEY` | `32+ character random string` |
| `CORS_ORIGINS` | `https://app.example.com,https://www.example.com` |
| `ENVIRONMENT` | `development` or `production` |
| `SENTRY_DSN` | `https://key@sentry.io/project` |

## Common Issues

### Issue: Database connection failed
```bash
# Check database is running
docker compose ps postgres

# Check database logs
docker compose logs postgres

# Test connection
docker compose exec postgres psql -U scholargrid -d scholargrid -c "SELECT 1;"
```

### Issue: Redis connection failed
```bash
# Check Redis is running
docker compose ps redis

# Check Redis logs
docker compose logs redis

# Test connection
docker compose exec redis redis-cli ping
```

### Issue: API not responding
```bash
# Check API logs
docker compose logs api

# Check API is running
docker compose ps api

# Restart API
docker compose restart api
```

### Issue: Migrations failed
```bash
# Check current migration version
alembic current

# Check migration history
alembic history

# Rollback and retry
alembic downgrade -1
alembic upgrade head
```

## Support

- **Documentation**: See `DEPLOYMENT.md` for detailed information
- **Checklist**: See `DEPLOYMENT_CHECKLIST.md` for deployment steps
- **Issues**: Report issues on GitHub
