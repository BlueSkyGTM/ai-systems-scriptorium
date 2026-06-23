"""
tests/test_lakehouse.py
Pytest suite — Delta Lake (lakehouse) assertions.

Tests are isolated: each test gets its own tmp directory via the
`delta_dir` fixture, so runs are always reproducible and clean.
"""

from __future__ import annotations

import pytest

from corpus_seed import (
    EXPECTED_CATEGORY_COUNTS_V0,
    UPDATED_DOC_ID,
    UPDATED_TEXT_V1,
    build_gold_corpus_v0,
    build_gold_corpus_v1,
)
from lakehouse import (
    get_content_hash_at_version,
    get_history,
    get_schema,
    get_version_num,
    read_latest,
    read_version,
    write_corpus_v0,
    write_corpus_v1,
)


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def delta_dir(tmp_path):
    """Return a fresh temporary directory path for a Delta table."""
    return str(tmp_path / "corpus_delta")


@pytest.fixture()
def populated_delta(delta_dir):
    """Write v0 and v1 into a temp Delta table; return the path."""
    write_corpus_v0(build_gold_corpus_v0(), delta_dir)
    write_corpus_v1(build_gold_corpus_v1(), delta_dir)
    return delta_dir


# ---------------------------------------------------------------------------
# Assertion 1: Delta write + version
# ---------------------------------------------------------------------------

class TestDeltaWrite:
    def test_v0_write_returns_version_0(self, delta_dir):
        ver = write_corpus_v0(build_gold_corpus_v0(), delta_dir)
        assert ver == 0

    def test_v1_write_returns_version_1(self, delta_dir):
        write_corpus_v0(build_gold_corpus_v0(), delta_dir)
        ver = write_corpus_v1(build_gold_corpus_v1(), delta_dir)
        assert ver == 1

    def test_get_version_num_after_two_writes(self, populated_delta):
        assert get_version_num(populated_delta) == 1

    def test_history_has_two_entries(self, populated_delta):
        h = get_history(populated_delta)
        assert len(h) == 2

    def test_schema_has_expected_columns(self, delta_dir):
        write_corpus_v0(build_gold_corpus_v0(), delta_dir)
        schema = get_schema(delta_dir)
        field_names = {f.name for f in schema.fields}
        expected = {"doc_id", "title", "text", "content_hash", "category", "last_modified_at"}
        assert expected.issubset(field_names), f"Missing fields: {expected - field_names}"

    def test_v0_row_count_matches_corpus_seed(self, delta_dir):
        df_v0 = build_gold_corpus_v0()
        write_corpus_v0(df_v0, delta_dir)
        df_read = read_latest(delta_dir)
        assert len(df_read) == len(df_v0)

    def test_total_expected_doc_count(self, delta_dir):
        df_v0 = build_gold_corpus_v0()
        write_corpus_v0(df_v0, delta_dir)
        df_read = read_latest(delta_dir)
        expected_total = sum(EXPECTED_CATEGORY_COUNTS_V0.values())
        assert len(df_read) == expected_total


# ---------------------------------------------------------------------------
# Assertion 2: Time-travel
# ---------------------------------------------------------------------------

class TestTimeTravel:
    def test_latest_has_updated_text(self, populated_delta):
        df = read_latest(populated_delta)
        text = df.loc[df["doc_id"] == UPDATED_DOC_ID, "text"].iloc[0]
        assert text == UPDATED_TEXT_V1

    def test_v0_snapshot_has_original_text(self, populated_delta):
        df = read_version(0, populated_delta)
        text = df.loc[df["doc_id"] == UPDATED_DOC_ID, "text"].iloc[0]
        assert text != UPDATED_TEXT_V1

    def test_v0_and_latest_differ(self, populated_delta):
        df_v0 = read_version(0, populated_delta)
        df_latest = read_latest(populated_delta)
        assert not df_v0.reset_index(drop=True).equals(df_latest.reset_index(drop=True))

    def test_v0_and_latest_same_row_count(self, populated_delta):
        df_v0 = read_version(0, populated_delta)
        df_latest = read_latest(populated_delta)
        assert len(df_v0) == len(df_latest)

    def test_unchanged_doc_identical_across_versions(self, populated_delta):
        """A document that was NOT updated should be byte-identical in v0 and v1."""
        stable_doc = "doc_0001"   # not in UPDATED_DOC_ID
        df_v0     = read_version(0, populated_delta)
        df_latest = read_latest(populated_delta)

        row_v0     = df_v0.loc[df_v0["doc_id"] == stable_doc]
        row_latest = df_latest.loc[df_latest["doc_id"] == stable_doc]

        assert not row_v0.empty, f"{stable_doc} missing from v0"
        assert not row_latest.empty, f"{stable_doc} missing from latest"

        # content_hash and text must be the same
        assert row_v0.iloc[0]["content_hash"] == row_latest.iloc[0]["content_hash"]
        assert row_v0.iloc[0]["text"]         == row_latest.iloc[0]["text"]


# ---------------------------------------------------------------------------
# Assertion 5: Lineage / M6 preview
# ---------------------------------------------------------------------------

class TestLineage:
    def test_hash_at_v0_is_not_none(self, populated_delta):
        h = get_content_hash_at_version(UPDATED_DOC_ID, 0, populated_delta)
        assert h is not None

    def test_hash_at_v1_is_not_none(self, populated_delta):
        h = get_content_hash_at_version(UPDATED_DOC_ID, 1, populated_delta)
        assert h is not None

    def test_hash_differs_between_versions(self, populated_delta):
        h0 = get_content_hash_at_version(UPDATED_DOC_ID, 0, populated_delta)
        h1 = get_content_hash_at_version(UPDATED_DOC_ID, 1, populated_delta)
        assert h0 != h1, "content_hash should change when document body changes"

    def test_hash_unchanged_for_stable_doc(self, populated_delta):
        stable_doc = "doc_0001"
        h0 = get_content_hash_at_version(stable_doc, 0, populated_delta)
        h1 = get_content_hash_at_version(stable_doc, 1, populated_delta)
        assert h0 == h1, "hash must not change for a document that was not updated"

    def test_missing_doc_returns_none(self, populated_delta):
        result = get_content_hash_at_version("doc_DOES_NOT_EXIST", 0, populated_delta)
        assert result is None


# ---------------------------------------------------------------------------
# Assertion 6 (partial): bad version number
# ---------------------------------------------------------------------------

class TestNegativeDelta:
    def test_read_nonexistent_version_raises(self, populated_delta):
        with pytest.raises(Exception):
            read_version(999, populated_delta)

    def test_table_intact_after_bad_read(self, populated_delta):
        try:
            read_version(999, populated_delta)
        except Exception:
            pass
        assert get_version_num(populated_delta) == 1
