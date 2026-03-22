#!/usr/bin/env python3
"""
Seed script — creates the initial admin user in the database.

Usage:
    python scripts/seed_admin.py

Environment variables required:
    DATABASE_URL — PostgreSQL connection string
    ADMIN_FIREBASE_UID — Firebase UID of the admin user
    ADMIN_EMAIL — Admin email address
    ADMIN_NAME — Admin display name (default: "Admin")
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
import uuid


def seed_admin():
    firebase_uid = os.environ.get("ADMIN_FIREBASE_UID")
    email = os.environ.get("ADMIN_EMAIL")
    name = os.environ.get("ADMIN_NAME", "Admin")

    if not firebase_uid or not email:
        print("ERROR: ADMIN_FIREBASE_UID and ADMIN_EMAIL must be set.", file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if existing:
            if existing.role != "admin":
                existing.role = "admin"
                db.commit()
                print(f"✓ Existing user '{email}' promoted to admin.")
            else:
                print(f"✓ Admin user '{email}' already exists. No changes made.")
            return

        admin = User(
            firebase_uid=firebase_uid,
            email=email,
            name=name,
            role="admin",
            status="active",
            score=0,
            tier="bronze",
            uploads_count=0,
            downloads_count=0,
        )
        db.add(admin)
        db.commit()
        print(f"✓ Admin user '{email}' created successfully (id={admin.id}).")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
