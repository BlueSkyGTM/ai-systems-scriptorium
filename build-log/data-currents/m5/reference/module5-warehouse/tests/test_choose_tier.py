"""
tests/test_choose_tier.py
Pytest suite — tier-selection logic assertions.
"""

from __future__ import annotations

import pytest

from choose_tier import choose_tier


# ---------------------------------------------------------------------------
# Assertion 4: Tier decision — warehouse patterns
# ---------------------------------------------------------------------------

class TestWarehierPatterns:
    @pytest.mark.parametrize("pattern", [
        "bi dashboard for quarterly reporting",
        "t-sql multi-table join for the finance team",
        "tsql stored procedure for compliance audit",
        "power-bi directquery over dimensional model",
        "powerbi report for sales leaders",
        "olap cube aggregation",
        "reporting endpoint for business intelligence",
        "multi-table acid transaction",
        "dml update on fact-table",
        "sql-endpoint for structured-query workload",
    ])
    def test_returns_warehouse(self, pattern):
        assert choose_tier(pattern) == "warehouse", f"Pattern {pattern!r} should map to 'warehouse'"


# ---------------------------------------------------------------------------
# Assertion 4: Tier decision — lakehouse patterns
# ---------------------------------------------------------------------------

class TestLakehousePatterns:
    @pytest.mark.parametrize("pattern", [
        "rag corpus refresh for embedding pipeline",
        "ml model training on feature-store",
        "machine-learning data-science exploration",
        "open-format delta parquet read by spark",
        "zero-copy streaming ingestion",
        "time-travel lineage for model debugging",
        "exploratory semi-structured data analysis",
        "corpus update with parquet",
        "embedding index rebuild",
    ])
    def test_returns_lakehouse(self, pattern):
        assert choose_tier(pattern) == "lakehouse", f"Pattern {pattern!r} should map to 'lakehouse'"


# ---------------------------------------------------------------------------
# Assertion 6 (partial): negative — unknown pattern raises
# ---------------------------------------------------------------------------

class TestNegativeChooseTier:
    def test_nonsense_raises_value_error(self):
        with pytest.raises(ValueError):
            choose_tier("nonsense")

    def test_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            choose_tier("")

    def test_unrelated_string_raises_value_error(self):
        with pytest.raises(ValueError):
            choose_tier("I want to eat pizza")

    def test_error_message_mentions_pattern(self):
        with pytest.raises(ValueError, match="Unknown access pattern"):
            choose_tier("this is gibberish")
