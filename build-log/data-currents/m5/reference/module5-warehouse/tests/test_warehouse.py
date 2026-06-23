"""
tests/test_warehouse.py
Pytest suite — DuckDB warehouse-query assertions.

Tests run entirely in-memory; no Delta table is needed.
"""

from __future__ import annotations

import pytest

from corpus_seed import EXPECTED_CATEGORY_COUNTS_V0, build_gold_corpus_v0
from warehouse import doc_count_by_category, query, unique_hash_count_by_category


@pytest.fixture(scope="module")
def corpus_v0():
    return build_gold_corpus_v0()


# ---------------------------------------------------------------------------
# Assertion 3: Warehouse query — category counts
# ---------------------------------------------------------------------------

class TestDocCountByCategory:
    def test_returns_dataframe_with_expected_columns(self, corpus_v0):
        result = doc_count_by_category(corpus_v0)
        assert "category" in result.columns
        assert "doc_count" in result.columns

    def test_row_count_equals_distinct_categories(self, corpus_v0):
        result = doc_count_by_category(corpus_v0)
        expected_cats = len(EXPECTED_CATEGORY_COUNTS_V0)
        assert len(result) == expected_cats

    @pytest.mark.parametrize("category,expected", list(EXPECTED_CATEGORY_COUNTS_V0.items()))
    def test_category_count(self, corpus_v0, category, expected):
        result = doc_count_by_category(corpus_v0)
        row = result[result["category"] == category]
        assert not row.empty, f"Category '{category}' not found in result"
        actual = int(row.iloc[0]["doc_count"])
        assert actual == expected, f"Expected {expected} docs for '{category}', got {actual}"

    def test_total_doc_count(self, corpus_v0):
        result = doc_count_by_category(corpus_v0)
        total = result["doc_count"].sum()
        expected_total = sum(EXPECTED_CATEGORY_COUNTS_V0.values())
        assert total == expected_total


class TestUniqueHashCountByCategory:
    def test_returns_expected_columns(self, corpus_v0):
        result = unique_hash_count_by_category(corpus_v0)
        assert "category" in result.columns
        assert "unique_hashes" in result.columns

    def test_unique_hashes_lte_doc_count(self, corpus_v0):
        counts   = doc_count_by_category(corpus_v0).set_index("category")
        uniq     = unique_hash_count_by_category(corpus_v0).set_index("category")
        for cat in counts.index:
            if cat in uniq.index:
                assert uniq.loc[cat, "unique_hashes"] <= counts.loc[cat, "doc_count"]


class TestArbitraryQuery:
    def test_filter_by_category(self, corpus_v0):
        result = query("SELECT doc_id FROM df WHERE category = 'mlops'", corpus_v0)
        assert len(result) == EXPECTED_CATEGORY_COUNTS_V0["mlops"]

    def test_all_rows(self, corpus_v0):
        result = query("SELECT COUNT(*) AS n FROM df", corpus_v0)
        expected = sum(EXPECTED_CATEGORY_COUNTS_V0.values())
        assert result.iloc[0]["n"] == expected
