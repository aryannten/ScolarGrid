# Testing Guide for ScholarGrid Backend API

## Prerequisites

### 1. PostgreSQL Test Database

The tests require a PostgreSQL database. Create a test database:

```bash
# Using psql
createdb scholargrid_test

# Or using SQL
psql -U postgres
CREATE DATABASE scholargrid_test;
```

### 2. Redis (Optional but Recommended)

Redis is used for caching. If Redis is not running, caching tests will be skipped but other tests will pass.

```bash
# Install Redis (Windows)
# Download from https://github.com/microsoftarchive/redis/releases
# Or use WSL/Docker

# Start Redis
redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:latest
```

### 3. Environment Configuration

Copy the test environment file:

```bash
cp .env.test .env
```

Update the database connection string if needed:

```
TEST_DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/scholargrid_test
```

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Files

```bash
# Run only property tests
pytest tests/test_*_properties.py -v

# Run only integration tests
pytest tests/test_integration_*.py -v

# Run specific test file
pytest tests/test_auth_properties.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Specific Test

```bash
pytest tests/test_auth_properties.py::test_property_token_verification_round_trip -v
```

## Test Database Management

### Reset Test Database

If you need to reset the test database:

```bash
# Drop and recreate
dropdb scholargrid_test
createdb scholargrid_test
```

### Run Migrations on Test Database

```bash
# Set test database URL
export DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/scholargrid_test"

# Run migrations
alembic upgrade head
```

## Troubleshooting

### SQLite Error: "no such function: to_char"

This means tests are using SQLite instead of PostgreSQL. Ensure:
1. PostgreSQL is installed and running
2. Test database exists
3. `TEST_DATABASE_URL` is set correctly in `.env`

### Redis Connection Errors

If you see "Error 10061 connecting to localhost:6379":
1. Redis is not running - start Redis server
2. Or tests will continue with degraded caching (this is expected behavior)

### Database Connection Errors

If you see "could not connect to server":
1. Ensure PostgreSQL is running
2. Check database credentials in `.env`
3. Verify database exists: `psql -l | grep scholargrid_test`

### Permission Errors

If you see permission denied errors:
1. Grant permissions: `GRANT ALL PRIVILEGES ON DATABASE scholargrid_test TO your_user;`
2. Or create database with your user: `createdb -O your_user scholargrid_test`

## Test Structure

- `tests/conftest.py` - Shared fixtures and test configuration
- `tests/test_*_properties.py` - Property-based tests using Hypothesis
- `tests/test_integration_*.py` - Integration tests for API endpoints
- `tests/test_*_model.py` - Unit tests for database models

## CI/CD

For CI/CD pipelines, ensure:
1. PostgreSQL service is available
2. Test database is created before running tests
3. Environment variables are set
4. Redis service is optional (tests will skip caching if unavailable)

Example GitHub Actions:

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: scholargrid_test
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 5432:5432
  
  redis:
    image: redis:7
    ports:
      - 6379:6379

steps:
  - name: Run tests
    env:
      TEST_DATABASE_URL: postgresql+psycopg://postgres:postgres@localhost:5432/scholargrid_test
      REDIS_URL: redis://localhost:6379/1
    run: pytest tests/ -v
```
