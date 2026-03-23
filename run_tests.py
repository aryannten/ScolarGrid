"""Simple test runner to verify all tests pass."""
import os
import sys
import subprocess

# Set the test database URL
os.environ["TEST_DATABASE_URL"] = "postgresql+psycopg://postgres:Aryan@localhost:5432/scholargrid_test"

# Run pytest
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
    capture_output=False
)

sys.exit(result.returncode)
