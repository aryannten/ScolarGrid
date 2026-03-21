# ScholarGrid Backend API

Academic note-sharing platform with real-time chat and AI assistance.

## Features

- User authentication via Firebase Auth
- Note upload, download, and rating system
- Real-time chat with Socket.io
- AI chatbot powered by Google Gemini
- Admin dashboard and analytics
- Leaderboard and tier system

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis
- **Authentication**: Firebase Auth
- **Storage**: Firebase Storage
- **Real-time**: Socket.io
- **AI**: Google Gemini API
- **Testing**: pytest, Hypothesis

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

The Firebase service provides authentication and file storage capabilities:

**Authentication:**
- Token verification using Firebase Admin SDK
- Extracts user identity (UID, email) from JWT tokens
- Handles token expiration and revocation

**File Storage:**
- Upload files to Firebase Storage with automatic UUID naming
- Download files from storage
- Delete files from storage
- Organized folder structure: `notes/`, `avatars/`, `chat_files/`, `complaint_attachments/`
- File type validation and content type detection

**Usage Example:**
```python
from app.services.firebase_service import (
    initialize_firebase,
    verify_firebase_token,
    upload_file_to_storage,
    STORAGE_FOLDERS,
    ALLOWED_EXTENSIONS
)

# Initialize Firebase (call once at startup)
initialize_firebase()

# Verify authentication token
decoded_token = await verify_firebase_token(token)
user_id = decoded_token['uid']

# Upload a file
download_url, filename, file_size = await upload_file_to_storage(
    file=upload_file,
    folder=STORAGE_FOLDERS['notes'],
    allowed_extensions=ALLOWED_EXTENSIONS['notes']
)
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

### Models (app.models)

SQLAlchemy ORM models with proper relationships and constraints:
- **User**: Student and admin accounts with tier system
- **Note**: Educational materials with ratings and moderation
- More models coming: ratings, downloads, chat, complaints, activities

## Setup

1. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `REDIS_URL`: Redis connection string
   - `FIREBASE_CREDENTIALS_PATH`: Path to Firebase service account JSON
   - `GEMINI_API_KEY`: Google Gemini API key (required in production)
   - `SECRET_KEY`: Secret key for JWT tokens (must be 32+ chars in production)
   - `CORS_ORIGINS`: Comma-separated list of allowed origins
   - `RATE_LIMIT`: API rate limit per minute (default: 100)
   - `ENVIRONMENT`: Environment name (development/staging/production)

3. **Run the development server**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Swagger docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Development

### Code Organization

The codebase follows a clean architecture pattern with clear separation of concerns:

- **core/**: Configuration, database, and dependency injection
- **models/**: Database models (SQLAlchemy ORM)
- **schemas/**: Request/response models (Pydantic)
- **services/**: Business logic and external integrations
- **api/**: API route handlers organized by version
- **utils/**: Shared utility functions
- **middleware/**: Custom middleware components

### Running Tests

```bash
pytest
```

### Running with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Code Quality

The project uses:
- **pytest** for unit and integration testing
- **Hypothesis** for property-based testing
- **SQLAlchemy 2.0** for type-safe database operations
- **Pydantic** for data validation
- **FastAPI** for automatic API documentation

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT
