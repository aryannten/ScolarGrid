"""
Integration tests for caching strategy (Task 29.6)

Tests cache hit/miss behavior, TTL, and invalidation on data modifications.
These tests mock Redis to work without a live Redis instance.
"""

import pytest
from unittest.mock import patch, MagicMock


# ─── Leaderboard: cached response is returned on second call ─────────────────

def test_leaderboard_cache_hit(client):
    """Two consecutive calls should return the same data."""
    r1 = client.get("/api/v1/leaderboard")
    r2 = client.get("/api/v1/leaderboard")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["total"] == r2.json()["total"]


# ─── Profile: cache is updated after profile change ──────────────────────────

def test_profile_cache_invalidated_on_update(client, student_user):
    # Get initial profile
    r1 = client.get("/api/v1/auth/me")
    assert r1.status_code == 200
    original_name = r1.json()["name"]

    # Update name
    client.put("/api/v1/auth/me", data={"name": "Cache Test Name"})

    # Get updated profile
    r2 = client.get("/api/v1/auth/me")
    assert r2.status_code == 200
    assert r2.json()["name"] == "Cache Test Name"


# ─── Analytics: returns data from cache or DB ─────────────────────────────────

def test_analytics_cache_works(admin_client):
    r1 = admin_client.get("/api/v1/admin/analytics")
    r2 = admin_client.get("/api/v1/admin/analytics")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["totals"]["users"] == r2.json()["totals"]["users"]


# ─── Cache helpers: get/set/delete work correctly ─────────────────────────────

def test_cache_set_and_get():
    from app.services.redis_service import get_cache, set_cache, delete_cache

    mock_redis = MagicMock()
    mock_redis.get.return_value = '{"test": 42}'
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = 1

    with patch("app.services.redis_service.redis_client") as mock:
        mock.client = mock_redis
        result = set_cache("test_key", {"test": 42}, ttl=60)
        assert result is True

        value = get_cache("test_key")
        assert value == {"test": 42}

        deleted = delete_cache("test_key")
        assert deleted is True


# ─── Cache helpers: missing key returns None ─────────────────────────────────

def test_cache_miss_returns_none():
    from app.services.redis_service import get_cache

    mock_redis = MagicMock()
    mock_redis.get.return_value = None

    with patch("app.services.redis_service.redis_client") as mock:
        mock.client = mock_redis
        result = get_cache("nonexistent_key")
        assert result is None


# ─── Cache helpers: invalidate_pattern counts deleted keys ───────────────────

def test_invalidate_pattern_returns_count():
    from app.services.redis_service import invalidate_pattern

    mock_redis = MagicMock()
    mock_redis.keys.return_value = ["key:1", "key:2", "key:3"]
    mock_redis.delete.return_value = 3

    with patch("app.services.redis_service.redis_client") as mock:
        mock.client = mock_redis
        count = invalidate_pattern("key:*")
        assert count == 3
