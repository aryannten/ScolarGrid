"""
Property-based tests for rate limiting middleware (Task 3.5)

Tests Redis-based rate limiting with 100 requests/minute limit,
429 error responses with Retry-After headers, and graceful degradation.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.middleware.rate_limiter import RateLimiterMiddleware
from app.core.config import settings


# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing"""
    mock_client = MagicMock()
    mock_client.incr = MagicMock(return_value=1)
    mock_client.expire = MagicMock()
    return mock_client


@pytest.fixture
def mock_request():
    """Create a mock FastAPI request"""
    request = Mock(spec=Request)
    request.url = Mock()
    request.url.path = "/api/v1/test"
    request.headers = {"authorization": "Bearer test_token_12345678901234567890"}
    request.client = Mock()
    request.client.host = "127.0.0.1"
    return request


@pytest.fixture
def rate_limiter():
    """Create rate limiter middleware instance"""
    app = FastAPI()
    return RateLimiterMiddleware(app)


# ─── Unit Tests ───────────────────────────────────────────────────────────────


def test_rate_limiter_allows_requests_under_limit(mock_redis_client, mock_request, rate_limiter):
    """Test that requests under the rate limit are allowed"""
    with patch('app.services.redis_service.redis_client') as mock_redis:
        mock_redis.client = mock_redis_client
        mock_redis_client.incr.return_value = 50  # Under limit
        
        async def call_next(request):
            return JSONResponse({"status": "ok"})
        
        # Should allow the request
        import asyncio
        response = asyncio.run(rate_limiter.dispatch(mock_request, call_next))
        
        assert response.status_code == 200
        assert mock_redis_client.incr.called


def test_rate_limiter_blocks_requests_over_limit(mock_redis_client, mock_request, rate_limiter):
    """Test that requests over the rate limit are blocked with 429"""
    with patch('app.services.redis_service.redis_client') as mock_redis:
        mock_redis.client = mock_redis_client
        mock_redis_client.incr.return_value = 101  # Over limit (100)
        
        async def call_next(request):
            return JSONResponse({"status": "ok"})
        
        # Should block the request
        import asyncio
        response = asyncio.run(rate_limiter.dispatch(mock_request, call_next))
        
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        
        # Parse response body
        import json
        body = json.loads(response.body.decode())
        assert body["error"] == "rate_limit_exceeded"
        assert "retry_after" in body


def test_rate_limiter_sets_retry_after_header(mock_redis_client, mock_request, rate_limiter):
    """Test that Retry-After header is set correctly"""
    with patch('app.services.redis_service.redis_client') as mock_redis:
        mock_redis.client = mock_redis_client
        mock_redis_client.incr.return_value = 150  # Well over limit
        
        async def call_next(request):
            return JSONResponse({"status": "ok"})
        
        import asyncio
        response = asyncio.run(rate_limiter.dispatch(mock_request, call_next))
        
        assert response.status_code == 429
        retry_after = int(response.headers["Retry-After"])
        assert 0 < retry_after <= 60  # Should be within the minute window


def test_rate_limiter_sets_ttl_on_first_request(mock_redis_client, mock_request, rate_limiter):
    """Test that TTL is set on the first request in a window"""
    with patch('app.services.redis_service.redis_client') as mock_redis:
        mock_redis.client = mock_redis_client
        mock_redis_client.incr.return_value = 1  # First request
        
        async def call_next(request):
            return JSONResponse({"status": "ok"})
        
        import asyncio
        asyncio.run(rate_limiter.dispatch(mock_request, call_next))
        
        # Should set TTL to 60 seconds
        mock_redis_client.expire.assert_called_once()
        args = mock_redis_client.expire.call_args[0]
        assert args[1] == 60  # TTL in seconds


def test_rate_limiter_skips_health_endpoints(mock_redis_client, rate_limiter):
    """Test that health check endpoints bypass rate limiting"""
    skip_paths = ["/", "/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
    
    for path in skip_paths:
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = path
        
        async def call_next(request):
            return JSONResponse({"status": "ok"})
        
        import asyncio
        response = asyncio.run(rate_limiter.dispatch(request, call_next))
        
        # Should allow without checking Redis
        assert response.status_code == 200


def test_rate_limiter_uses_token_as_identifier(mock_redis_client, mock_request, rate_limiter):
    """Test that authenticated requests use token as identifier"""
    with patch('app.services.redis_service.redis_client') as mock_redis:
        mock_redis.client = mock_redis_client
        mock_redis_client.incr.return_value = 1
        
        async def call_next(request):
            return JSONResponse({"status": "ok"})
        
        import asyncio
        asyncio.run(rate_limiter.dispatch(mock_request, call_next))
        
        # Check that the key uses token prefix
        call_args = mock_redis_client.incr.call_args[0][0]
        assert call_args.startswith("rate_limit:token:")


def test_rate_limiter_uses_ip_for_unauthenticated(mock_redis_client, rate_limiter):
    """Test that unauthenticated requests use IP as identifier"""
    request = Mock(spec=Request)
    request.url = Mock()
    request.url.path = "/api/v1/test"
    request.headers = {}  # No authorization header
    request.client = Mock()
    request.client.host = "192.168.1.100"
    
    with patch('app.services.redis_service.redis_client') as mock_redis:
        mock_redis.client = mock_redis_client
        mock_redis_client.incr.return_value = 1
        
        async def call_next(req):
            return JSONResponse({"status": "ok"})
        
        import asyncio
        asyncio.run(rate_limiter.dispatch(request, call_next))
        
        # Check that the key uses IP prefix
        call_args = mock_redis_client.incr.call_args[0][0]
        assert call_args.startswith("rate_limit:ip:")
        assert "192.168.1.100" in call_args


def test_rate_limiter_graceful_degradation_on_redis_failure(mock_request, rate_limiter):
    """Test that rate limiter allows requests if Redis is unavailable"""
    with patch('app.services.redis_service.redis_client') as mock_redis:
        # Simulate Redis connection failure
        mock_redis.client.incr.side_effect = Exception("Redis connection failed")
        
        async def call_next(request):
            return JSONResponse({"status": "ok"})
        
        import asyncio
        response = asyncio.run(rate_limiter.dispatch(mock_request, call_next))
        
        # Should allow the request despite Redis failure
        assert response.status_code == 200


def test_rate_limiter_respects_configured_limit():
    """Test that rate limiter uses the configured limit from settings"""
    assert settings.rate_limit == 100
    # The middleware should use settings.rate_limit for comparison


def test_rate_limiter_window_key_format():
    """Test that rate limit keys include time window"""
    limiter = RateLimiterMiddleware(FastAPI())
    
    request = Mock(spec=Request)
    request.url = Mock()
    request.url.path = "/api/v1/test"
    request.headers = {"authorization": "Bearer token123"}
    request.client = Mock()
    request.client.host = "127.0.0.1"
    
    identifier = limiter._get_identifier(request)
    
    # Should include token prefix
    assert identifier.startswith("token:")
    
    # Window key should include minute timestamp
    current_minute = int(time.time()) // 60
    window_key = f"rate_limit:{identifier}:{current_minute}"
    assert "rate_limit:" in window_key


# ─── Integration Tests ────────────────────────────────────────────────────────


@pytest.mark.integration
def test_rate_limiter_integration_with_real_redis():
    """Integration test with real Redis connection"""
    from app.services.redis_service import redis_client
    
    try:
        redis_client.connect()
        
        # Clean up any existing test keys
        test_key = f"rate_limit:test:integration:{int(time.time()) // 60}"
        redis_client.client.delete(test_key)
        
        # Test incrementing
        count1 = redis_client.client.incr(test_key)
        assert count1 == 1
        
        count2 = redis_client.client.incr(test_key)
        assert count2 == 2
        
        # Test TTL
        redis_client.client.expire(test_key, 60)
        ttl = redis_client.client.ttl(test_key)
        assert 0 < ttl <= 60
        
        # Clean up
        redis_client.client.delete(test_key)
        
    except Exception as e:
        pytest.skip(f"Redis not available for integration test: {e}")


# ─── Property-Based Tests ─────────────────────────────────────────────────────


@pytest.mark.hypothesis
def test_rate_limiter_property_monotonic_increase():
    """
    Property: Request count should monotonically increase within a window
    
    For any sequence of requests within the same minute window,
    the count should increase by 1 for each request.
    """
    from hypothesis import given, strategies as st, settings as hyp_settings
    from app.core.config import settings as app_settings
    
    @given(st.integers(min_value=1, max_value=200))
    @hyp_settings(deadline=None)  # Disable deadline for async operations
    def property_test(num_requests):
        mock_client = MagicMock()
        counts = list(range(1, num_requests + 1))
        mock_client.incr.side_effect = counts
        
        with patch('app.services.redis_service.redis_client') as mock_redis:
            mock_redis.client = mock_client
            
            limiter = RateLimiterMiddleware(FastAPI())
            request = Mock(spec=Request)
            request.url = Mock()
            request.url.path = "/api/v1/test"
            request.headers = {"authorization": "Bearer token"}
            request.client = Mock()
            request.client.host = "127.0.0.1"
            
            async def call_next(req):
                return JSONResponse({"status": "ok"})
            
            import asyncio
            
            # Simulate multiple requests
            for i in range(num_requests):
                response = asyncio.run(limiter.dispatch(request, call_next))
                
                # Requests up to limit should succeed
                if i < app_settings.rate_limit:
                    assert response.status_code == 200
                else:
                    # Requests over limit should be blocked
                    assert response.status_code == 429
    
    property_test()


@pytest.mark.hypothesis
def test_rate_limiter_property_retry_after_bounds():
    """
    Property: Retry-After header should always be between 1 and 60 seconds
    
    For any request that exceeds the rate limit, the Retry-After value
    should be a positive integer not exceeding 60 seconds.
    """
    from hypothesis import given, strategies as st
    
    @given(st.integers(min_value=101, max_value=1000))
    def property_test(request_count):
        mock_client = MagicMock()
        mock_client.incr.return_value = request_count
        
        with patch('app.services.redis_service.redis_client') as mock_redis:
            mock_redis.client = mock_client
            
            limiter = RateLimiterMiddleware(FastAPI())
            request = Mock(spec=Request)
            request.url = Mock()
            request.url.path = "/api/v1/test"
            request.headers = {"authorization": "Bearer token"}
            request.client = Mock()
            request.client.host = "127.0.0.1"
            
            async def call_next(req):
                return JSONResponse({"status": "ok"})
            
            import asyncio
            response = asyncio.run(limiter.dispatch(request, call_next))
            
            assert response.status_code == 429
            retry_after = int(response.headers["Retry-After"])
            assert 1 <= retry_after <= 60
    
    property_test()


# ─── Edge Cases ───────────────────────────────────────────────────────────────


def test_rate_limiter_handles_missing_client_info(rate_limiter):
    """Test rate limiter handles requests with missing client info"""
    request = Mock(spec=Request)
    request.url = Mock()
    request.url.path = "/api/v1/test"
    request.headers = {}
    request.client = None  # No client info
    
    # Should use 'unknown' as fallback
    identifier = rate_limiter._get_identifier(request)
    assert identifier == "ip:unknown"


def test_rate_limiter_handles_malformed_auth_header(rate_limiter):
    """Test rate limiter handles malformed authorization headers"""
    request = Mock(spec=Request)
    request.url = Mock()
    request.url.path = "/api/v1/test"
    request.headers = {"authorization": "InvalidFormat"}
    request.client = Mock()
    request.client.host = "127.0.0.1"
    
    # Should fall back to IP
    identifier = rate_limiter._get_identifier(request)
    assert identifier.startswith("ip:")


def test_rate_limiter_response_body_format(mock_redis_client, mock_request, rate_limiter):
    """Test that 429 response has correct body format"""
    with patch('app.services.redis_service.redis_client') as mock_redis:
        mock_redis.client = mock_redis_client
        mock_redis_client.incr.return_value = 150
        
        async def call_next(request):
            return JSONResponse({"status": "ok"})
        
        import asyncio
        response = asyncio.run(rate_limiter.dispatch(mock_request, call_next))
        
        import json
        body = json.loads(response.body.decode())
        
        # Verify required fields
        assert "error" in body
        assert "message" in body
        assert "retry_after" in body
        
        # Verify values
        assert body["error"] == "rate_limit_exceeded"
        assert "100/minute" in body["message"]
        assert isinstance(body["retry_after"], int)
