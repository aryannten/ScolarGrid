#!/usr/bin/env python
"""
Script to generate initial Alembic migration.

Run this after starting PostgreSQL:
    python scripts/generate_migration.py
"""
import subprocess
import sys

def main():
    """Generate initial migration using Alembic."""
    try:
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial schema with all models"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Migration generated successfully!")
            print(result.stdout)
        else:
            print("❌ Migration generation failed:")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
