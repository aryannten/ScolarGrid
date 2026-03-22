#!/usr/bin/env python3
"""
Verify environment configuration before starting the application.

Usage:
    python scripts/verify_env.py

Exits with code 0 if all required variables are set and valid, 1 otherwise.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    env = os.environ.get("ENVIRONMENT", "development")
    errors = []

    print(f"Verifying environment: {env}")
    print("=" * 50)

    # Check required vars
    for key, desc in REQUIRED.items():
        val = os.environ.get(key)
        if not val:
            errors.append(f"  ✗ {key} — {desc}")
        else:
            print(f"  ✓ {key}")

    # Check Firebase credentials file exists
    creds_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")
    if not os.path.exists(creds_path):
        errors.append(f"  ✗ Firebase credentials file not found at: {creds_path}")

    # Production checks
    if env.lower() == "production":
        for key, desc in PRODUCTION_REQUIRED.items():
            val = os.environ.get(key)
            if not val:
                errors.append(f"  ✗ {key} (production required) — {desc}")
            elif key == "SECRET_KEY" and len(val) < 32:
                errors.append(f"  ✗ {key} must be at least 32 characters")
            else:
                print(f"  ✓ {key}")

    print("=" * 50)
    if errors:
        print("\nConfiguration errors found:")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("\n✓ All configuration checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    verify()
