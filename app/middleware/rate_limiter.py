"""
Redis-based rate limiting middleware for ScholarGrid Backend API

Limits each authenticated user to RATE_LIMIT requests per minute (default: 100).
Unauthenticated requests are tracked by IP address.
"""

import time
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter backed by Redis.

    Tracks request counts per user (by firebase UID or IP) within a 60-second window.
    Returns HTTP 429 with Retry-After header when the limit is exceeded.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health/docs/metrics endpoints
        skip_paths = {"/", "/health", "/metrics", "/docs", "/redoc", "/openapi.json"}
        if request.url.path in skip_paths:
            return await call_next(request)

        try:
            from app.services.redis_service import redis_client

            # Determine rate-limit key: prefer user ID from token, fall back to IP
            identifier = self._get_identifier(request)
            window_key = f"rate_limit:{identifier}:{int(time.time()) // 60}"

            current = redis_client.client.incr(window_key)
            if current == 1:
                # Set TTL on first request in this window
                redis_client.client.expire(window_key, 60)

            if current > settings.rate_limit:
                retry_after = 60 - (int(time.time()) % 60)
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "rate_limit_exceeded",
                        "message": f"Too many requests. Limit: {settings.rate_limit}/minute.",
                        "retry_after": retry_after,
                    },
                    headers={"Retry-After": str(retry_after)},
                )
        except Exception:
            # If Redis is unavailable, allow the request through
            pass

        return await call_next(request)

    def _get_identifier(self, request: Request) -> str:
        """Extract rate-limit identifier from request (JWT sub or client IP)."""
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            # Use first 32 chars of token as a rough key (avoids decoding)
            return f"token:{auth[7:39]}"
        # Fall back to client IP
        client = request.client
        return f"ip:{client.host if client else 'unknown'}"
