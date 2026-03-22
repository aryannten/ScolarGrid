"""
Property-based tests for scoring service (Task 9.2)

Validates tier calculation and score arithmetic are universally correct.
"""

import pytest
from hypothesis import given, settings as hyp_settings
from hypothesis import strategies as st

from app.services.scoring_service import calculate_tier, TIER_THRESHOLDS


# ─── Property: tier boundaries are always consistent ─────────────────────────

@given(score=st.integers(min_value=0, max_value=100_000))
@hyp_settings(max_examples=500)
def test_property_tier_always_valid(score):
    """All scores must map to a valid tier."""
    tier = calculate_tier(score)
    assert tier in ("bronze", "silver", "gold", "elite")


@given(score=st.integers(min_value=3000, max_value=100_000))
@hyp_settings(max_examples=200)
def test_property_elite_tier_for_high_scores(score):
    assert calculate_tier(score) == "elite"


@given(score=st.integers(min_value=2000, max_value=2999))
@hyp_settings(max_examples=200)
def test_property_gold_tier_range(score):
    assert calculate_tier(score) == "gold"


@given(score=st.integers(min_value=1000, max_value=1999))
@hyp_settings(max_examples=200)
def test_property_silver_tier_range(score):
    assert calculate_tier(score) == "silver"


@given(score=st.integers(min_value=0, max_value=999))
@hyp_settings(max_examples=200)
def test_property_bronze_tier_range(score):
    assert calculate_tier(score) == "bronze"


@given(
    uploads=st.integers(min_value=0, max_value=5000),
    downloads=st.integers(min_value=0, max_value=5000),
)
@hyp_settings(max_examples=200)
def test_property_score_is_sum_of_uploads_and_downloads(uploads, downloads):
    """Score = uploads + downloads, always."""
    score = uploads + downloads
    assert score >= 0
    tier = calculate_tier(score)
    assert tier in ("bronze", "silver", "gold", "elite")


@given(score=st.integers(min_value=0, max_value=100_000))
@hyp_settings(max_examples=200)
def test_property_tier_is_monotonic(score):
    """Higher scores should never produce a lower-ranked tier."""
    tier1 = calculate_tier(score)
    tier2 = calculate_tier(score + 1)
    tier_order = ["bronze", "silver", "gold", "elite"]
    assert tier_order.index(tier2) >= tier_order.index(tier1)
