#!/usr/bin/env python3
"""
Health check script for ScholarGrid Backend API.

Usage:
    python scripts/health_check.py [--url URL]

Options:
    --url URL   API base URL (default: http://localhost:8000)

Exit codes:
    0 - All health checks passed
    1 - One or more health checks failed
"""

import sys
import urllib.request
import urllib.error
import json
from typing import Dict, Any


def check_health(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    Check API health endpoint.
    
    Args:
        base_url: Base URL of the API
        
    Returns:
        Dictionary with health check results
    """
    health_url = f"{base_url}/health"
    
    try:
        with urllib.request.urlopen(health_url, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return {
                    "success": True,
                    "status_code": 200,
                    "data": data
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status,
                    "error": f"Unexpected status code: {response.status}"
                }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "status_code": e.code,
            "error": f"HTTP error: {e.code} {e.reason}"
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "status_code": None,
            "error": f"Connection error: {e.reason}"
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": None,
            "error": f"Unexpected error: {str(e)}"
        }


def main():
    """Main health check execution."""
    # Parse command line arguments
    base_url = "http://localhost:8000"
    if "--url" in sys.argv:
        try:
            url_index = sys.argv.index("--url")
            base_url = sys.argv[url_index + 1]
        except (IndexError, ValueError):
            print("Error: --url requires a URL argument", file=sys.stderr)
            sys.exit(1)
    
    print(f"Checking health of API at: {base_url}")
    print("=" * 60)
    
    result = check_health(base_url)
    
    if result["success"]:
        data = result["data"]
        print(f"[OK] API is healthy")
        print(f"  Status: {data.get('status', 'unknown')}")
        print(f"  Database: {data.get('database', 'unknown')}")
        print(f"  Redis: {data.get('redis', 'unknown')}")
        print(f"  Timestamp: {data.get('timestamp', 'unknown')}")
        print("=" * 60)
        print("[OK] All health checks passed")
        sys.exit(0)
    else:
        print(f"[FAIL] API health check failed")
        print(f"  Status code: {result.get('status_code', 'N/A')}")
        print(f"  Error: {result.get('error', 'Unknown error')}")
        print("=" * 60)
        print("[FAIL] Health check failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
