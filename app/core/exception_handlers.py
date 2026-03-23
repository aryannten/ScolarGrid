"""
Global exception handlers for ScholarGrid Backend API

Returns consistent JSON error responses for all error types.
"""

from datetime import datetime, timezone
from uuid import uuid4
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


def make_error(request: Request, status_code: int, error_code: str, message: str, details=None):
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(
            {
                "error": error_code,
                "message": message,
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": str(uuid4()),
                "path": str(request.url.path),
            }
        ),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return make_error(request, 422, "validation_error", "Request validation failed.", exc.errors())


async def http_exception_handler(request: Request, exc):
    from fastapi import HTTPException
    if not isinstance(exc, HTTPException):
        return make_error(request, 500, "internal_error", "An unexpected error occurred.")
    return make_error(request, exc.status_code, "http_error", str(exc.detail))


async def generic_exception_handler(request: Request, exc: Exception):
    import traceback
    print(f"Unhandled exception: {traceback.format_exc()}")
    return make_error(request, 500, "internal_error", "An unexpected error occurred.")
