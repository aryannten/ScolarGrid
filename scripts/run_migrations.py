#!/usr/bin/env python3
"""
Run Alembic database migrations.

Usage:
    python scripts/run_migrations.py [--check]

Options:
    --check   Don't apply; just print pending migrations.
"""

import os
import sys

def run():
    action = "check" if "--check" in sys.argv else "upgrade head"
    cmd = f"alembic {action}"
    print(f"Running: {cmd}")
    exit_code = os.system(cmd)
    if exit_code != 0:
        print("Migration failed.", file=sys.stderr)
        sys.exit(1)
    print("✓ Migrations complete.")

if __name__ == "__main__":
    run()
