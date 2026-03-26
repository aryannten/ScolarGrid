# ScholarGrid Backend API

Academic note-sharing platform with real-time chat and AI assistance. Production-ready FastAPI backend with comprehensive testing, monitoring, and deployment automation.

## Features

- 🔐 User authentication via Firebase Auth with role-based access control
- 📚 Note upload, download, and rating system with moderation workflow
- 💬 Real-time chat with Socket.io and group management
- 🤖 AI chatbot powered by Google Gemini with conversation history
- 📊 Admin dashboard with analytics and user management
- 🏆 Leaderboard and tier system (Bronze, Silver, Gold, Elite)
- 📝 Complaint tracking and resolution system
- 🔍 Full-text search with PostgreSQL and Redis caching
- 📈 Activity feed and platform statistics
- 🚀 Production-ready with Docker, monitoring, and error tracking

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0 ORM
- **Cache**: Redis 7+
- **Authentication**: Firebase Auth
- **Storage**: Cloudinary (images/files)
- **Real-time**: Socket.io
- **AI**: Google Gemini API
- **Testing**: pytest, Hypothesis (property-based testing)
- **Monitoring**: Sentry error tracking, structured JSON logging
- **Deployment**: Docker, docker-compose

## Project Structure

```
scholargrid-backend-api/
├── app/
│   ├── __init__.py                # Package exports
│   ├── main.py                    # FastAPI application entry point
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Database connection and session
│   │   └── dependencies.py        # FastAPI dependencies
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                # User model
│   │   └── note.py                # Note model
│   ├── schemas/                   # Pydantic request/response models
│   │   └── __init__.py
│   ├── services/                  # Business logic services
│   │   ├── __init__.py
│   │   ├── redis_service.py       # Redis caching service
│   │   └── firebase_service.py    # Firebase Auth & Storage
│   ├── api/                       # API route handlers
│   │   ├── __init__.py
│   │   └── v1/                    # API version 1
│   │       └── __init__.py
│   ├── utils/                     # Utility functions
│   │   └── __init__.py
│   └── middleware/                # Custom middleware
│       └── __init__.py
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_config.py             # Configuration tests
│   ├── test_database.py           # Database tests
│   ├── test_redis_client.py       # Redis tests
│   ├── test_firebase_service.py   # Firebase service tests
│   ├── test_user_model.py         # User model tests
│   └── test_note_model.py         # Note model tests
├── alembic/                       # Database migrations
├── pyproject.toml                 # Project dependencies
├── .env.example                   # Environment variables template
└── README.md
```

## Core Services

### Configuration (app.core.config)

Centralized configuration management with environment variable validation:
- Pydantic-based settings with automatic type conversion
- Production-specific validation (secure keys, no localhost URLs)
- CORS origins parsing and environment detection

### Database (app.core.database)

SQLAlchemy database setup with connection pooling:
- PostgreSQL connection with optimized pool settings
- Session management with FastAPI dependency injection
- Health check utilities for monitoring

### Firebase Service (app.services.firebase_service)

The Firebase service provides authentication capabilities:

**Authentication:**
- Token verification using Firebase Admin SDK
- Extracts user identity (UID, email) from JWT tokens
- Handles token expiration and revocation

**Usage Example:**
```python
from app.services.firebase_service import initialize_firebase, verify_firebase_token

# Initialize Firebase (call once at startup)
initialize_firebase()

# Verify authentication token
decoded_token = await verify_firebase_token(token)
user_id = decoded_token['uid']
```

### Redis Service (app.services.redis_service)

Redis caching with connection pooling and helper functions:
- Cache-aside pattern implementation
- Pattern-based cache invalidation
- TTL management and JSON serialization
- Health check utilities

**Usage Example:**
```python
from app.services.redis_service import get_cache, set_cache, invalidate_pattern

# Cache data with 5 minute TTL
set_cache("user:profile:123", user_data, ttl=300)

# Retrieve from cache
cached_data = get_cache("user:profile:123")

# Invalidate all user profiles
invalidate_pattern("user:profile:*")
```

### Cloudinary Storage (app.services.cloudinary_storage)

File storage service using Cloudinary:
- Upload files with automatic optimization
- Secure URL generation
- File deletion and management
- Support for images and documents
- Organized folder structure

**Usage Example:**
```python
from app.services.cloudinary_storage import upload_file, delete_file

# Upload a file
result = upload_file(file_content, filename, folder="notes")
secure_url = result['secure_url']

# Delete a file
delete_file(public_id)
```

### Scoring Service (app.services.scoring_service)

Score and tier calculation for gamification:
- Calculate user score (uploads + downloads + ratings)
- Determine tier based on score thresholds
- Update user statistics
- Leaderboard generation

### Gemini Service (app.services.gemini_service)

Google Gemini AI integration:
- Conversational AI responses
- Streaming support
- Context-aware assistance
- Rate limiting and safety filters

## Quick Start

### Using Docker (Recommended)

1. **Clone and configure**:
   ```bash
   git clone <repository-url>
   cd scholargrid-backend-api
   cp .env.example .env
   # Edit .env and make sure firebase-credentials.json exists in the project root
   ```

2. **Start services**:
   ```bash
   docker compose up --build
   ```

3. **Access the API**:
   - API: http://localhost:8000
   - Swagger docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run migrations**:
   ```bash
   python scripts/run_migrations.py
   ```

4. **Seed admin user** (optional):
   ```bash
   python scripts/seed_admin.py
   ```

5. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment Variables

Required configuration (see `.env.example` for full list):

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/scholargrid

# Redis
REDIS_URL=redis://localhost:6379/0

# Firebase
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key

# Security
SECRET_KEY=your-secret-key-min-32-chars
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Optional: Error Tracking
SENTRY_DSN=your_sentry_dsn
```

For production deployment, see `.env.production.template` and `DEPLOYMENT.md`.

## Development

### Project Structure

```
scholargrid-backend-api/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── core/                      # Core functionality
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Database connection and session
│   │   ├── logging_config.py      # Structured logging setup
│   │   ├── sentry_config.py       # Error tracking integration
│   │   └── dependencies.py        # FastAPI dependencies
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── user.py                # User model
│   │   ├── note.py                # Note model
│   │   ├── rating.py              # Rating model
│   │   ├── chat.py                # Chat models
│   │   ├── complaint.py           # Complaint models
│   │   └── ai_chatbot.py          # AI chatbot models
│   ├── schemas/                   # Pydantic request/response models
│   ├── services/                  # Business logic services
│   │   ├── redis_service.py       # Redis caching
│   │   ├── firebase_service.py    # Firebase Auth
│   │   ├── cloudinary_storage.py  # File storage
│   │   ├── scoring_service.py     # Score and tier calculation
│   │   └── gemini_service.py      # AI chatbot integration
│   ├── api/v1/                    # API route handlers
│   │   ├── auth.py                # Authentication endpoints
│   │   ├── notes.py               # Notes endpoints
│   │   ├── chat.py                # Chat endpoints
│   │   ├── complaints.py          # Complaints endpoints
│   │   ├── admin.py               # Admin endpoints
│   │   └── ai_chatbot.py          # AI chatbot endpoints
│   ├── utils/                     # Utility functions
│   └── middleware/                # Custom middleware
├── tests/                         # Test suite
│   ├── test_*.py                  # Unit tests
│   ├── test_*_properties.py       # Property-based tests
│   └── test_*_integration.py      # Integration tests
├── scripts/                       # Deployment scripts
│   ├── run_migrations.py          # Database migration runner
│   ├── seed_admin.py              # Admin user seeding
│   ├── verify_env.py              # Environment verification
│   └── health_check.py            # Health check script
├── alembic/                       # Database migrations
├── docs/                          # Documentation
│   ├── DEPLOYMENT.md              # Deployment guide
│   ├── DEPLOYMENT_CHECKLIST.md    # Deployment checklist
│   └── DEPLOYMENT_QUICK_REFERENCE.md
├── Dockerfile                     # Production Docker image
├── docker-compose.yml             # Local development setup
├── pyproject.toml                 # Project dependencies
├── .env.example                   # Development environment template
├── .env.production.template       # Production environment template
└── README.md
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest tests/test_*_properties.py  # Property-based tests
pytest tests/test_*_integration.py # Integration tests

# Run with verbose output
pytest -v
```

### Code Quality

The project uses:
- **pytest** for unit and integration testing
- **Hypothesis** for property-based testing (100+ iterations per test)
- **SQLAlchemy 2.0** for type-safe database operations
- **Pydantic** for data validation and serialization
- **FastAPI** for automatic API documentation
- **Sentry** for error tracking and performance monitoring
- **Structured logging** for production observability

### Development Workflow

1. Create a feature branch
2. Write tests first (TDD approach)
3. Implement the feature
4. Run tests and ensure coverage
5. Check code quality
6. Submit pull request

### Deployment Scripts

```bash
# Verify environment configuration
python scripts/verify_env.py

# Run database migrations
python scripts/run_migrations.py

# Seed initial admin user
python scripts/seed_admin.py

# Health check (local or remote)
python scripts/health_check.py
python scripts/health_check.py https://api.scholargrid.com
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs (interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (clean API reference)
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

### Key Endpoints

**Authentication**
- `POST /api/v1/auth/register` - Register new user
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/me` - Update user profile

**Notes**
- `POST /api/v1/notes` - Upload note
- `GET /api/v1/notes` - Search and filter notes
- `GET /api/v1/notes/{id}` - Get note details
- `POST /api/v1/notes/{id}/download` - Download note
- `POST /api/v1/notes/{id}/rate` - Rate note

**Chat**
- `POST /api/v1/chat/groups` - Create chat group
- `POST /api/v1/chat/groups/join` - Join group with code
- `GET /api/v1/chat/groups` - List user's groups
- `GET /api/v1/chat/groups/{id}/messages` - Get message history

**AI Chatbot**
- `POST /api/v1/ai/chat` - Send message to AI
- `POST /api/v1/ai/chat/stream` - Stream AI response
- `GET /api/v1/ai/conversations` - List conversations
- `GET /api/v1/ai/usage` - Get usage statistics

**Admin**
- `GET /api/v1/admin/analytics` - Platform analytics
- `GET /api/v1/admin/users` - User management
- `PUT /api/v1/notes/{id}/approve` - Approve note
- `PUT /api/v1/notes/{id}/reject` - Reject note

See full API documentation at `/docs` endpoint.

## Production Deployment

### Docker Deployment

```bash
# Build production image
docker build -t scholargrid-api:latest .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

See `DEPLOYMENT.md` for comprehensive deployment guide including:
- Environment configuration
- Database setup and migrations
- SSL/TLS configuration
- Monitoring and alerting
- Scaling considerations
- Backup and recovery

### Pre-Deployment Checklist

See `DEPLOYMENT_CHECKLIST.md` for complete checklist covering:
- Environment verification
- Security configuration
- Database migrations
- Service health checks
- Monitoring setup
- Post-deployment validation

## Monitoring and Observability

### Structured Logging

Production logs are output in JSON format for easy parsing:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Request completed",
  "method": "GET",
  "path": "/api/v1/notes",
  "status_code": 200,
  "duration_ms": 45.2,
  "user_id": "uuid",
  "request_id": "uuid"
}
```

### Error Tracking

Sentry integration provides:
- Real-time error notifications
- Performance monitoring
- User context tracking
- Release tracking
- Custom tags and breadcrumbs

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Performance

- **Response Time**: p95 < 500ms for most endpoints
- **Throughput**: 100+ requests/second per instance
- **Caching**: Redis caching with 5-15 minute TTL
- **Database**: Connection pooling with optimized queries
- **Rate Limiting**: 100 requests/minute per user

## Security

- Firebase Auth token verification
- Role-based access control (RBAC)
- Rate limiting per user
- Input sanitization and validation
- SQL injection prevention
- XSS protection
- CORS configuration
- HTTPS enforcement in production
- Security headers (CSP, X-Frame-Options, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Implement the feature
5. Ensure all tests pass
6. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: See `docs/` folder
- API Docs: http://localhost:8000/docs

## License

MIT
