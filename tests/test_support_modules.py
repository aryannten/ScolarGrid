from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request

from app.core import dependencies, exception_handlers
from app.core import database as core_database
from app.utils.helpers import (
    is_valid_uuid,
    normalize_subject,
    paginate,
    sanitize_string,
    truncate_title,
)


def _make_request(path: str = "/test") -> Request:
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [],
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 12345),
    }
    return Request(scope)


def test_paginate_calculates_offset_and_total_pages():
    assert paginate(page=3, page_size=10, total=95) == (20, 10)
    assert paginate(page=1, page_size=25, total=0) == (0, 0)


def test_sanitize_string_trims_and_truncates():
    assert sanitize_string("  hello world  ") == "hello world"
    assert sanitize_string("abcdef", max_length=4) == "abcd"


def test_is_valid_uuid_accepts_and_rejects_inputs():
    assert is_valid_uuid("123e4567-e89b-12d3-a456-426614174000") is True
    assert is_valid_uuid("not-a-uuid") is False
    assert is_valid_uuid(None) is False


def test_truncate_title_handles_short_and_long_text():
    assert truncate_title("short", max_length=10) == "short"
    assert truncate_title("abcdefghij", max_length=7) == "abcd..."


def test_normalize_subject_capitalizes_words_and_collapses_whitespace():
    assert normalize_subject("  computer   science ") == "Computer Science"


def test_dependencies_get_db_yields_session_and_closes_it():
    mock_session = MagicMock()

    with patch("app.core.dependencies.SessionLocal", return_value=mock_session):
        generator = dependencies.get_db()
        yielded = next(generator)
        assert yielded is mock_session

        with pytest.raises(StopIteration):
            next(generator)

    mock_session.close.assert_called_once()


def test_make_error_returns_standard_payload():
    response = exception_handlers.make_error(
        _make_request("/errors/example"),
        418,
        "teapot",
        "Short and stout",
        {"reason": "demo"},
    )

    assert response.status_code == 418
    assert b'"error":"teapot"' in response.body
    assert b'"message":"Short and stout"' in response.body
    assert b'"path":"/errors/example"' in response.body


@pytest.mark.asyncio
async def test_validation_exception_handler_returns_validation_error():
    exc = RequestValidationError(
        [{"loc": ("body", "name"), "msg": "Field required", "type": "missing"}]
    )

    response = await exception_handlers.validation_exception_handler(_make_request(), exc)

    assert response.status_code == 422
    assert b'"error":"validation_error"' in response.body


@pytest.mark.asyncio
async def test_http_exception_handler_handles_http_and_non_http_errors():
    http_response = await exception_handlers.http_exception_handler(
        _make_request(),
        HTTPException(status_code=404, detail="Missing"),
    )
    assert http_response.status_code == 404
    assert b'"error":"http_error"' in http_response.body

    generic_response = await exception_handlers.http_exception_handler(
        _make_request(),
        RuntimeError("boom"),
    )
    assert generic_response.status_code == 500
    assert b'"error":"internal_error"' in generic_response.body


@pytest.mark.asyncio
async def test_generic_exception_handler_returns_internal_error():
    with patch("builtins.print") as mock_print:
        response = await exception_handlers.generic_exception_handler(
            _make_request(),
            ValueError("bad"),
        )

    assert response.status_code == 500
    assert b'"error":"internal_error"' in response.body
    mock_print.assert_called_once()


def test_init_db_calls_create_all():
    with patch.object(core_database.Base.metadata, "create_all") as mock_create_all:
        core_database.init_db()

    mock_create_all.assert_called_once_with(bind=core_database.engine)


def test_check_db_connection_returns_false_on_error():
    with patch.object(core_database.engine, "connect", side_effect=RuntimeError("db down")):
        assert core_database.check_db_connection() is False
