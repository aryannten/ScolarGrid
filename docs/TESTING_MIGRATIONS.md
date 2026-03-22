# Testing Database Migrations

This guide explains how to test the Alembic database migrations for the ScholarGrid Backend API.

## Prerequisites

1. PostgreSQL 16+ installed and running
2. Python virtual environment activated
3. Environment variables configured in `.env` file

## Quick Start

### 1. Start PostgreSQL Database

Using Docker Compose (recommended):

```bash
docker-compose up -d postgres
```

Or start PostgreSQL manually:

```bash
# On macOS with Homebrew
brew services start postgresql@16

# On Ubuntu/Debian
sudo systemctl start postgresql

# On Windows
# Start PostgreSQL service from Services app
```

### 2. Create Database

```bash
# Using psql
psql -U postgres -c "CREATE DATABASE scholargrid;"
psql -U postgres -c "CREATE USER scholargrid WITH PASSWORD 'scholargrid_pass';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE scholargrid TO scholargrid;"
```

Or let Docker Compose handle it (if using docker-compose).

### 3. Verify Database Connection

```bash
# Test connection
psql -U scholargrid -d scholargrid -h localhost -p 5432
```

## Testing Migration Upgrade

### Apply the Migration

```bash
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial_schema
```

### Verify Tables Were Created

```bash
psql -U scholargrid -d scholargrid -c "\dt"
```

Expected output should show 13 tables:
```
                    List of relations
 Schema |         Name          | Type  |   Owner    
--------+-----------------------+-------+------------
 public | activities            | table | scholargrid
 public | ai_conversations      | table | scholargrid
 public | ai_messages           | table | scholargrid
 public | ai_usage_tracking     | table | scholargrid
 public | alembic_version       | table | scholargrid
 public | chat_groups           | table | scholargrid
 public | chat_memberships      | table | scholargrid
 public | complaint_responses   | table | scholargrid
 public | complaints            | table | scholargrid
 public | downloads             | table | scholargrid
 public | messages              | table | scholargrid
 public | notes                 | table | scholargrid
 public | ratings               | table | scholargrid
 public | users                 | table | scholargrid
```

### Verify Table Structure

Check a specific table structure:

```bash
psql -U scholargrid -d scholargrid -c "\d users"
```

Expected output should show:
- UUID primary key
- All columns from the User model
- Check constraints for role, status, tier
- Indexes on email, firebase_uid, score, tier, role

### Verify Indexes

```bash
psql -U scholargrid -d scholargrid -c "\di"
```

Should show indexes for:
- Primary keys
- Foreign keys
- Frequently queried columns (email, firebase_uid, score, etc.)

### Verify Foreign Keys

```bash
psql -U scholargrid -d scholargrid -c "
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
"
```

## Testing Migration Downgrade

### Rollback the Migration

```bash
alembic downgrade base
```

Expected output:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running downgrade 001 -> , initial_schema
```

### Verify Tables Were Dropped

```bash
psql -U scholargrid -d scholargrid -c "\dt"
```

Expected output should show only the `alembic_version` table:
```
                 List of relations
 Schema |      Name       | Type  |   Owner    
--------+-----------------+-------+------------
 public | alembic_version | table | scholargrid
```

## Testing Migration Re-application

### Re-apply the Migration

```bash
alembic upgrade head
```

This tests that the migration can be applied multiple times (idempotency).

### Verify Current Revision

```bash
alembic current
```

Expected output:
```
001 (head)
```

## Testing with Sample Data

### Insert Test Data

```sql
-- Connect to database
psql -U scholargrid -d scholargrid

-- Insert a test user
INSERT INTO users (id, firebase_uid, email, name, role)
VALUES (
    gen_random_uuid(),
    'test_firebase_uid_123',
    'test@example.com',
    'Test User',
    'student'
);

-- Verify insertion
SELECT id, email, name, role, tier, score FROM users;
```

### Test Foreign Key Constraints

```sql
-- Try to insert a note with invalid uploader_id (should fail)
INSERT INTO notes (id, title, description, subject, file_url, file_name, file_size, file_type, uploader_id)
VALUES (
    gen_random_uuid(),
    'Test Note',
    'Test Description',
    'Computer Science',
    'https://example.com/file.pdf',
    'file.pdf',
    1024,
    'application/pdf',
    gen_random_uuid()  -- Invalid UUID, not in users table
);
-- Expected: ERROR: insert or update on table "notes" violates foreign key constraint
```

### Test Check Constraints

```sql
-- Try to insert user with invalid role (should fail)
INSERT INTO users (id, firebase_uid, email, name, role)
VALUES (
    gen_random_uuid(),
    'test_firebase_uid_456',
    'test2@example.com',
    'Test User 2',
    'invalid_role'  -- Invalid role
);
-- Expected: ERROR: new row for relation "users" violates check constraint "check_user_role"
```

### Test Cascade Delete

```sql
-- Insert a user and a note
INSERT INTO users (id, firebase_uid, email, name, role)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'test_firebase_uid_789',
    'test3@example.com',
    'Test User 3',
    'student'
);

INSERT INTO notes (id, title, description, subject, file_url, file_name, file_size, file_type, uploader_id)
VALUES (
    gen_random_uuid(),
    'Test Note',
    'Test Description',
    'Computer Science',
    'https://example.com/file.pdf',
    'file.pdf',
    1024,
    'application/pdf',
    '00000000-0000-0000-0000-000000000001'
);

-- Delete the user (should cascade delete the note)
DELETE FROM users WHERE id = '00000000-0000-0000-0000-000000000001';

-- Verify note was deleted
SELECT COUNT(*) FROM notes WHERE uploader_id = '00000000-0000-0000-0000-000000000001';
-- Expected: 0
```

## Automated Testing Script

Create a test script `test_migrations.sh`:

```bash
#!/bin/bash

set -e

echo "==================================="
echo "Testing Database Migrations"
echo "==================================="

# Test upgrade
echo ""
echo "1. Testing migration upgrade..."
alembic upgrade head
echo "✓ Upgrade successful"

# Verify tables
echo ""
echo "2. Verifying tables..."
TABLE_COUNT=$(psql -U scholargrid -d scholargrid -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name != 'alembic_version';")
if [ "$TABLE_COUNT" -eq 13 ]; then
    echo "✓ All 13 tables created"
else
    echo "✗ Expected 13 tables, found $TABLE_COUNT"
    exit 1
fi

# Test downgrade
echo ""
echo "3. Testing migration downgrade..."
alembic downgrade base
echo "✓ Downgrade successful"

# Verify tables removed
echo ""
echo "4. Verifying tables removed..."
TABLE_COUNT=$(psql -U scholargrid -d scholargrid -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name != 'alembic_version';")
if [ "$TABLE_COUNT" -eq 0 ]; then
    echo "✓ All tables removed"
else
    echo "✗ Expected 0 tables, found $TABLE_COUNT"
    exit 1
fi

# Re-apply migration
echo ""
echo "5. Re-applying migration..."
alembic upgrade head
echo "✓ Re-application successful"

echo ""
echo "==================================="
echo "✓ All migration tests passed!"
echo "==================================="
```

Make it executable and run:

```bash
chmod +x test_migrations.sh
./test_migrations.sh
```

## Troubleshooting

### Connection Refused

If you get "connection refused" errors:

1. Check PostgreSQL is running: `pg_isready`
2. Verify port: `lsof -i :5432` (macOS/Linux)
3. Check DATABASE_URL in `.env` file

### Permission Denied

If you get permission errors:

```bash
# Grant permissions
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE scholargrid TO scholargrid;"
psql -U postgres -d scholargrid -c "GRANT ALL ON SCHEMA public TO scholargrid;"
```

### Migration Already Applied

If migration is already applied:

```bash
# Check current revision
alembic current

# Downgrade first
alembic downgrade base

# Then upgrade
alembic upgrade head
```

### Schema Drift

If database schema doesn't match models:

```bash
# Generate a new migration to sync
alembic revision --autogenerate -m "sync schema"

# Review the generated migration
cat alembic/versions/<new_revision>.py

# Apply if correct
alembic upgrade head
```

## CI/CD Integration

For automated testing in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Test Migrations

on: [push, pull_request]

jobs:
  test-migrations:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: scholargrid
          POSTGRES_USER: scholargrid
          POSTGRES_PASSWORD: scholargrid_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Test migrations
        env:
          DATABASE_URL: postgresql+psycopg://scholargrid:scholargrid_pass@localhost:5432/scholargrid
        run: |
          alembic upgrade head
          alembic downgrade base
          alembic upgrade head
```

## Best Practices

1. **Always test migrations** on a development database first
2. **Backup production data** before running migrations
3. **Review autogenerated migrations** carefully
4. **Test both upgrade and downgrade** paths
5. **Verify data integrity** after migrations
6. **Monitor migration performance** on large tables
7. **Use transactions** for data migrations (Alembic does this by default)

## Additional Resources

- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Core](https://docs.sqlalchemy.org/en/20/core/)
