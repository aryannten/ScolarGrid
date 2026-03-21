"""
Redis client and caching utilities for ScholarGrid Backend API

Provides connection management, caching operations, and cache invalidation patterns.
"""

import redis
from typing import Optional, Any, List
import json
from app.core.config import settings


class RedisClient:
    """Redis client with connection pooling and caching utilities"""
    
    def __init__(self):
        """Initialize Redis connection pool"""
        self._pool = None
        self._client = None
    
    def connect(self):
        """
        Establish Redis connection with connection pooling.
        
        Creates a connection pool for efficient connection reuse across requests.
        """
        if self._pool is None:
            self._pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                decode_responses=True,
                max_connections=10,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            self._client = redis.Redis(connection_pool=self._pool)
    
    def disconnect(self):
        """Close Redis connection pool"""
        if self._pool:
            self._pool.disconnect()
            self._pool = None
            self._client = None
    
    @property
    def client(self) -> redis.Redis:
        """
        Get Redis client instance.
        
        Returns:
            redis.Redis: Connected Redis client
            
        Raises:
            RuntimeError: If client is not connected
        """
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client
    
    def ping(self) -> bool:
        """
        Check Redis connection health.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            return self.client.ping()
        except Exception:
            return False


# Cache helper functions

def get_cache(key: str) -> Optional[Any]:
    """
    Get value from cache.
    
    Args:
        key: Cache key
        
    Returns:
        Cached value if found and not expired, None otherwise
    """
    try:
        value = redis_client.client.get(key)
        if value is None:
            return None
        
        # Try to parse as JSON, return raw string if parsing fails
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    except Exception as e:
        # Log error but don't fail the request
        print(f"Cache get error for key {key}: {e}")
        return None


def set_cache(key: str, value: Any, ttl: int = 300) -> bool:
    """
    Set value in cache with TTL.
    
    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized if not a string)
        ttl: Time to live in seconds (default: 5 minutes)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Serialize value to JSON if it's not a string
        if not isinstance(value, str):
            value = json.dumps(value)
        
        redis_client.client.setex(key, ttl, value)
        return True
    except Exception as e:
        # Log error but don't fail the request
        print(f"Cache set error for key {key}: {e}")
        return False


def delete_cache(key: str) -> bool:
    """
    Delete a single cache entry.
    
    Args:
        key: Cache key to delete
        
    Returns:
        bool: True if key was deleted, False otherwise
    """
    try:
        redis_client.client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error for key {key}: {e}")
        return False


def invalidate_pattern(pattern: str) -> int:
    """
    Invalidate all cache keys matching a pattern.
    
    Args:
        pattern: Redis key pattern (e.g., "leaderboard:*", "user:profile:*")
        
    Returns:
        int: Number of keys deleted
        
    Example:
        # Invalidate all leaderboard pages
        invalidate_pattern("leaderboard:*")
        
        # Invalidate specific user profile
        invalidate_pattern(f"user:profile:{user_id}")
    """
    try:
        # Find all keys matching the pattern
        keys = redis_client.client.keys(pattern)
        
        if not keys:
            return 0
        
        # Delete all matching keys
        deleted = redis_client.client.delete(*keys)
        return deleted
    except Exception as e:
        print(f"Cache invalidate pattern error for pattern {pattern}: {e}")
        return 0


# Global Redis client instance
redis_client = RedisClient()


def check_redis_connection() -> bool:
    """
    Check if Redis connection is healthy.
    
    Used by health check endpoints to verify Redis availability.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        redis_client.connect()
        return redis_client.ping()
    except Exception:
        return False
