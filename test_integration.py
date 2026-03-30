#!/usr/bin/env python3
"""
Integration Test Script for ScholarGrid

Tests the authentication endpoints to verify frontend-backend integration.
Run this script to quickly verify that the backend is working correctly.

Usage:
    python test_integration.py
"""

import requests
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
TEST_STUDENT_NAME = "Test Student"
TEST_STUDENT_EMAIL = "test@example.com"


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test(name: str):
    """Print test name"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing: {name}{Colors.RESET}")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def test_health_check() -> bool:
    """Test the health check endpoint"""
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is healthy: {data.get('status')}")
            print(f"  Database: {data.get('database')}")
            print(f"  Redis: {data.get('redis')}")
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend. Is it running on port 5000?")
        print_warning("Start the backend with: uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload")
        return False
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def test_session_check() -> bool:
    """Test the session check endpoint"""
    print_test("Session Check (No Session)")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/session", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if not data.get("logged_in"):
                print_success("Session check works (not logged in)")
                return True
            else:
                print_warning("Unexpected: Already logged in")
                return True
        else:
            print_error(f"Session check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Session check failed: {e}")
        return False


def test_admin_login() -> tuple[bool, requests.Session]:
    """Test admin login"""
    print_test("Admin Login")
    session = requests.Session()
    try:
        response = session.post(
            f"{BASE_URL}/api/auth/admin-login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            admin = data.get("admin", {})
            print_success(f"Admin login successful: {admin.get('username')}")
            print(f"  Display Name: {admin.get('display_name')}")
            print(f"  Session ID: {data.get('session_id')[:16]}...")
            return True, session
        else:
            print_error(f"Admin login failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False, session
    except Exception as e:
        print_error(f"Admin login failed: {e}")
        return False, session


def test_session_persistence(session: requests.Session) -> bool:
    """Test that session persists after login"""
    print_test("Session Persistence")
    try:
        response = session.get(f"{BASE_URL}/api/auth/session", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("logged_in") and data.get("type") == "admin":
                print_success("Session persists correctly")
                print(f"  User: {data.get('admin', {}).get('username')}")
                return True
            else:
                print_error("Session not persisted correctly")
                return False
        else:
            print_error(f"Session check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Session persistence check failed: {e}")
        return False


def test_logout(session: requests.Session) -> bool:
    """Test logout"""
    print_test("Logout")
    try:
        response = session.post(f"{BASE_URL}/api/auth/logout", json={}, timeout=5)
        if response.status_code == 200:
            print_success("Logout successful")
            
            # Verify session is cleared
            response = session.get(f"{BASE_URL}/api/auth/session", timeout=5)
            data = response.json()
            if not data.get("logged_in"):
                print_success("Session cleared correctly")
                return True
            else:
                print_error("Session not cleared after logout")
                return False
        else:
            print_error(f"Logout failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Logout failed: {e}")
        return False


def test_student_login() -> tuple[bool, requests.Session]:
    """Test student login"""
    print_test("Student Login (Google)")
    session = requests.Session()
    try:
        response = session.post(
            f"{BASE_URL}/api/auth/google",
            json={"name": TEST_STUDENT_NAME, "email": TEST_STUDENT_EMAIL},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            print_success(f"Student login successful: {user.get('name')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Session ID: {data.get('session_id')[:16]}...")
            return True, session
        else:
            print_error(f"Student login failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False, session
    except Exception as e:
        print_error(f"Student login failed: {e}")
        return False, session


def main():
    """Run all integration tests"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("ScholarGrid Integration Tests")
    print(f"{'='*60}{Colors.RESET}\n")
    print(f"Backend URL: {BASE_URL}")
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))
    if not results[-1][1]:
        print_error("\nBackend is not running. Please start it first.")
        sys.exit(1)
    
    # Test 2: Session Check (No Session)
    results.append(("Session Check", test_session_check()))
    
    # Test 3: Admin Login
    admin_login_success, admin_session = test_admin_login()
    results.append(("Admin Login", admin_login_success))
    
    # Test 4: Session Persistence (Admin)
    if admin_login_success:
        results.append(("Session Persistence", test_session_persistence(admin_session)))
        
        # Test 5: Logout
        results.append(("Logout", test_logout(admin_session)))
    
    # Test 6: Student Login
    student_login_success, student_session = test_student_login()
    results.append(("Student Login", student_login_success))
    
    # Test 7: Session Persistence (Student)
    if student_login_success:
        results.append(("Session Persistence (Student)", test_session_persistence(student_session)))
        
        # Cleanup: Logout student
        test_logout(student_session)
    
    # Print Summary
    print(f"\n{Colors.BOLD}{'='*60}")
    print("Test Summary")
    print(f"{'='*60}{Colors.RESET}\n")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if success else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status}  {test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All tests passed! Integration is working correctly.{Colors.RESET}")
        print(f"\n{Colors.BLUE}Next steps:{Colors.RESET}")
        print("  1. Start the frontend: npm run dev")
        print("  2. Open http://localhost:5173 in your browser")
        print("  3. Test the login flows in the UI")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some tests failed. Please check the errors above.{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
