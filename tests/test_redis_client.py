"""
Unit tests for Redis client and caching utilities
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app.services.redis_service import (
    RedisClient,
    get_cache,
    set_cache,
    delete_cache,
    invalidate_pattern,
    redis_client
)


class TestRedisClient:
    """Test RedisClient class"""
    
    def test_connect_creates_pool_and_client(self):
        """Test that connect() creates connection pool and client"""
        client = RedisClient()
        
        with patch('redis.ConnectionPool.from_url') as mock_pool, \
             patch('redis.Redis') as mock_redis:
            
            mock_pool_instance = Mock()
            mock_pool.return_value = mock_pool_instance
            mock_redis_instance = Mock()
            mock_redis.return_value = mock_redis_instance
            
            client.connect()
            
            # Verify pool was created with correct parameters
            mock_pool.assert_called_once()
            call_kwargs = mock_pool.call_args[1]
            assert call_kwargs['decode_responses'] is True
            assert call_kwargs['max_connections'] == 10
            assert call_kwargs['socket_connect_timeout'] == 5
            assert call_kwargs['socket_timeout'] == 5
            assert call_kwargs['retry_on_timeout'] is True
            
            # Verify Redis client was created with pool
            mock_redis.assert_called_once_with(connection_pool=mock_pool_instance)
            assert client._pool == mock_pool_instance
            assert client._client == mock_redis_instance
    
    def test_connect_idempotent(self):
        """Test that calling connect() multiple times doesn't create multiple pools"""
        client = RedisClient()
        
        with patch('redis.ConnectionPool.from_url') as mock_pool, \
             patch('redis.Redis'):
            
            mock_pool.return_value = Mock()
            
            client.connect()
            client.connect()  # Second call
            
            # Should only be called once
            assert mock_pool.call_count == 1
    
    def test_disconnect_closes_pool(self):
        """Test that disconnect() closes the connection pool"""
        client = RedisClient()
        
        with patch('redis.ConnectionPool.from_url') as mock_pool, \
             patch('redis.Redis'):
            
            mock_pool_instance = Mock()
            mock_pool.return_value = mock_pool_instance
            
            client.connect()
            client.disconnect()
            
            # Verify pool was disconnected
            mock_pool_instance.disconnect.assert_called_once()
            assert client._pool is None
            assert client._client is None
    
    def test_client_property_returns_client(self):
        """Test that client property returns the Redis client"""
        client = RedisClient()
        
        with patch('redis.ConnectionPool.from_url'), \
             patch('redis.Redis') as mock_redis:
            
            mock_redis_instance = Mock()
            mock_redis.return_value = mock_redis_instance
            
            client.connect()
            
            assert client.client == mock_redis_instance
    
    def test_client_property_raises_if_not_connected(self):
        """Test that accessing client property before connect() raises error"""
        client = RedisClient()
        
        with pytest.raises(RuntimeError, match="Redis client not connected"):
            _ = client.client
    
    def test_ping_returns_true_when_healthy(self):
        """Test that ping() returns True when connection is healthy"""
        client = RedisClient()
        
        with patch('redis.ConnectionPool.from_url'), \
             patch('redis.Redis') as mock_redis:
            
            mock_redis_instance = Mock()
            mock_redis_instance.ping.return_value = True
            mock_redis.return_value = mock_redis_instance
            
            client.connect()
            
            assert client.ping() is True
            mock_redis_instance.ping.assert_called_once()
    
    def test_ping_returns_false_on_exception(self):
        """Test that ping() returns False when connection fails"""
        client = RedisClient()
        
        with patch('redis.ConnectionPool.from_url'), \
             patch('redis.Redis') as mock_redis:
            
            mock_redis_instance = Mock()
            mock_redis_instance.ping.side_effect = Exception("Connection failed")
            mock_redis.return_value = mock_redis_instance
            
            client.connect()
            
            assert client.ping() is False


class TestCacheHelpers:
    """Test cache helper functions"""
    
    def test_get_cache_returns_json_value(self):
        """Test that get_cache() returns deserialized JSON value"""
        test_data = {"key": "value", "number": 42}
        
        with patch.object(redis_client, '_client') as mock_client:
            mock_client.get.return_value = json.dumps(test_data)
            
            result = get_cache("test:key")
            
            assert result == test_data
            mock_client.get.assert_called_once_with("test:key")
    
    def test_get_cache_returns_string_value(self):
        """Test that get_cache() returns raw string if not JSON"""
        test_value = "simple string"
        
        with patch.object(redis_client, '_client') as mock_client:
            mock_client.get.return_value = test_value
            
            result = get_cache("test:key")
            
            assert result == test_value
    
    def test_get_cache_returns_none_when_not_found(self):
        """Test that get_cache() returns None when key doesn't exist"""
        with patch.object(redis_client, '_client') as mock_client:
            mock_client.get.return_value = None
            
            result = get_cache("nonexistent:key")
            
            assert result is None
    
    def test_get_cache_returns_none_on_exception(self):
        """Test that get_cache() returns None on error"""
        with patch.object(redis_client, '_client') as mock_client:
            mock_client.get.side_effect = Exception("Redis error")
            
            result = get_cache("test:key")
            
            assert result is None
    
    def test_set_cache_stores_json_value(self):
        """Test that set_cache() serializes and stores JSON value"""
        test_data = {"key": "value", "number": 42}
        
        with patch.object(redis_client, '_client') as mock_client:
            result = set_cache("test:key", test_data, ttl=300)
            
            assert result is True
            mock_client.setex.assert_called_once_with(
                "test:key",
                300,
                json.dumps(test_data)
            )
    
    def test_set_cache_stores_string_value(self):
        """Test that set_cache() stores string value directly"""
        test_value = "simple string"
        
        with patch.object(redis_client, '_client') as mock_client:
            result = set_cache("test:key", test_value, ttl=600)
            
            assert result is True
            mock_client.setex.assert_called_once_with("test:key", 600, test_value)
    
    def test_set_cache_uses_default_ttl(self):
        """Test that set_cache() uses default TTL of 300 seconds"""
        with patch.object(redis_client, '_client') as mock_client:
            set_cache("test:key", "value")
            
            # Check that TTL is 300 (default)
            call_args = mock_client.setex.call_args[0]
            assert call_args[1] == 300
    
    def test_set_cache_returns_false_on_exception(self):
        """Test that set_cache() returns False on error"""
        with patch.object(redis_client, '_client') as mock_client:
            mock_client.setex.side_effect = Exception("Redis error")
            
            result = set_cache("test:key", "value")
            
            assert result is False
    
    def test_delete_cache_removes_key(self):
        """Test that delete_cache() removes the specified key"""
        with patch.object(redis_client, '_client') as mock_client:
            result = delete_cache("test:key")
            
            assert result is True
            mock_client.delete.assert_called_once_with("test:key")
    
    def test_delete_cache_returns_false_on_exception(self):
        """Test that delete_cache() returns False on error"""
        with patch.object(redis_client, '_client') as mock_client:
            mock_client.delete.side_effect = Exception("Redis error")
            
            result = delete_cache("test:key")
            
            assert result is False
    
    def test_invalidate_pattern_deletes_matching_keys(self):
        """Test that invalidate_pattern() deletes all matching keys"""
        matching_keys = ["user:1", "user:2", "user:3"]
        
        with patch.object(redis_client, '_client') as mock_client:
            mock_client.keys.return_value = matching_keys
            mock_client.delete.return_value = 3
            
            result = invalidate_pattern("user:*")
            
            assert result == 3
            mock_client.keys.assert_called_once_with("user:*")
            mock_client.delete.assert_called_once_with(*matching_keys)
    
    def test_invalidate_pattern_returns_zero_when_no_matches(self):
        """Test that invalidate_pattern() returns 0 when no keys match"""
        with patch.object(redis_client, '_client') as mock_client:
            mock_client.keys.return_value = []
            
            result = invalidate_pattern("nonexistent:*")
            
            assert result == 0
            mock_client.keys.assert_called_once_with("nonexistent:*")
            mock_client.delete.assert_not_called()
    
    def test_invalidate_pattern_returns_zero_on_exception(self):
        """Test that invalidate_pattern() returns 0 on error"""
        with patch.object(redis_client, '_client') as mock_client:
            mock_client.keys.side_effect = Exception("Redis error")
            
            result = invalidate_pattern("test:*")
            
            assert result == 0
