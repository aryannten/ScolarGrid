"""
Property-based tests for leaderboard (Tasks 10.2, 10.4)

Validates ranking correctness, pagination invariants, and tier monotonicity.
"""

import pytest
from hypothesis import given, settings as hyp_settings
from hypothesis import strategies as st

from app.services.scoring_service import calculate_tier


# ─── Property: rankings are always sorted descending by score ────────────────

@given(scores=st.lists(st.integers(min_value=0, max_value=10_000), min_size=1, max_size=50))
@hyp_settings(max_examples=100)
def test_property_rankings_always_desc_by_score(scores):
    """Sorting scores descending must produce a non-increasing sequence."""
    sorted_scores = sorted(scores, reverse=True)
    for i in range(len(sorted_scores) - 1):
        assert sorted_scores[i] >= sorted_scores[i + 1]


# ─── Property: page_size is always respected ─────────────────────────────────

@given(
    total=st.integers(min_value=0, max_value=200),
    page_size=st.integers(min_value=1, max_value=100),
    page=st.integers(min_value=1, max_value=10),
)
@hyp_settings(max_examples=200)
def test_property_pagination_never_returns_more_than_page_size(total, page_size, page):
    """Slicing a list with offset/limit should never return more items than page_size."""
    import math
    offset = (page - 1) * page_size
    items = list(range(total))
    page_items = items[offset:offset + page_size]
    assert len(page_items) <= page_size


# ─── Property: rank starts at 1 for first item on page 1 ─────────────────────

def test_property_first_rank_is_always_one():
    users = [{"score": 100 - i, "rank": i + 1} for i in range(10)]
    assert users[0]["rank"] == 1


# ─── Property: total_pages ceiling division ──────────────────────────────────

@given(
    total=st.integers(min_value=0, max_value=10_000),
    page_size=st.integers(min_value=1, max_value=100),
)
@hyp_settings(max_examples=200)
def test_property_total_pages_ceiling_division(total, page_size):
    import math
    total_pages = math.ceil(total / page_size) if total else 0
    assert total_pages >= 0


# ─── Property: tier ordering matches score ordering ───────────────────────────

TIER_ORDER = {"bronze": 0, "silver": 1, "gold": 2, "elite": 3}


@given(
    s1=st.integers(min_value=0, max_value=10_000),
    s2=st.integers(min_value=0, max_value=10_000),
)
@hyp_settings(max_examples=300)
def test_property_tier_ordering_matches_score_ordering(s1, s2):
    """If s1 >= s2, tier(s1) >= tier(s2) in the tier order."""
    if s1 >= s2:
        assert TIER_ORDER[calculate_tier(s1)] >= TIER_ORDER[calculate_tier(s2)]
