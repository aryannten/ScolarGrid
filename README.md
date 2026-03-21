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
│   ├── __init__.py
│   └── main.py          # FastAPI application entry point
├── tests/
│   └── __init__.py
├── alembic/             # Database migrations
├── pyproject.toml       # Project dependencies
├── .env.example         # Environment variables template
└── README.md
```

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

### Running Tests

```bash
pytest
```

### Running with Coverage

```bash
pytest --cov=app --cov-report=html
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT
