#!/usr/bin/env python3
"""
Verify environment configuration before starting the application.

Usage:
    python scripts/verify_env.py

Exits with code 0 if all required variables are set and valid, 1 otherwise.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import Settings

REQUIRED = {
    "DATABASE_URL": "PostgreSQL connection string",
    "REDIS_URL": "Redis connection string",
    "FIREBASE_CREDENTIALS_PATH": "Path to firebase-credentials.json",
}

PRODUCTION_REQUIRED = {
    "GEMINI_API_KEY": "Google Gemini API key",
    "SECRET_KEY": "JWT secret key (min 32 chars)",
}


def verify():
    settings = Settings()
    env = settings.environment
    errors = []
    project_root = Path(__file__).resolve().parent.parent

    print(f"Verifying environment: {env}")
    print("=" * 50)

    values = {
        "DATABASE_URL": settings.database_url,
        "REDIS_URL": settings.redis_url,
        "FIREBASE_CREDENTIALS_PATH": settings.firebase_credentials_path,
        "GEMINI_API_KEY": settings.gemini_api_key,
        "SECRET_KEY": settings.secret_key,
    }

    for key, desc in REQUIRED.items():
        val = values.get(key)
        if not val:
            errors.append(f"  [FAIL] {key} - {desc}")
        else:
            print(f"  [OK]   {key}")

    creds_path = Path(settings.firebase_credentials_path)
    if not creds_path.is_absolute():
        creds_path = project_root / creds_path
    if not creds_path.exists():
        errors.append(f"  [FAIL] Firebase credentials file not found at: {creds_path}")

    if env.lower() == "production":
        for key, desc in PRODUCTION_REQUIRED.items():
            val = values.get(key)
            if not val:
                errors.append(f"  [FAIL] {key} (production required) - {desc}")
            elif key == "SECRET_KEY" and len(val) < 32:
                errors.append(f"  [FAIL] {key} must be at least 32 characters")
            else:
                print(f"  [OK]   {key}")

    print("=" * 50)
    if errors:
        print("\nConfiguration errors found:")
        for error in errors:
            print(error)
        sys.exit(1)

    print("\n[OK] All configuration checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    verify()
