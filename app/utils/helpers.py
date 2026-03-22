"""
Utility functions for ScholarGrid Backend API

Common helpers used across multiple routes and services.
"""

import math
import re
from typing import Tuple, Optional
from uuid import UUID


def paginate(page: int, page_size: int, total: int) -> Tuple[int, int]:
    """
    Calculate offset and total_pages for pagination.

    Args:
        page: 1-indexed page number
        page_size: Items per page
        total: Total number of items

    Returns:
        Tuple[offset, total_pages]
    """
    offset = (page - 1) * page_size
    total_pages = math.ceil(total / page_size) if total else 0
    return offset, total_pages


def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    Sanitize a string by stripping leading/trailing whitespace and truncating.

    Args:
        value: Input string
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    return value.strip()[:max_length]


def is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        UUID(str(value))
        return True
    except (ValueError, AttributeError):
        return False


def truncate_title(text: str, max_length: int = 100) -> str:
    """
    Truncate text to max_length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum character length

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def normalize_subject(subject: str) -> str:
    """
    Normalize a subject string — capitalize each word, strip extra whitespace.
    """
    return " ".join(word.capitalize() for word in subject.strip().split())
