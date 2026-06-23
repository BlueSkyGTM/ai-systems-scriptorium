"""
smoke.py
Module 5 Warehouse and Lakehouse — smoke test.

Run:    python smoke.py
Exits:  0 if all assertions pass; non-zero otherwise.

Each assertion prints PASS or FAIL followed by a short description.
The six assertions mirror the oracle defined in the module spec:

  1. Delta write + version   : v0 write -> version 0; v1 write -> version 1.
  2. Time-travel             : v0 read returns original; latest returns updated.
  3. Warehouse query         : DuckDB category counts match expected oracle.
  4. Tier decision           : choose_tier returns correct tier for BI and ML patterns.
  5. Lineage / M6 preview    : content_hash of doc_0000 differs between v0 and v1
                               (basis for "what did this answer cite last week?").
  6. Negatives               : choose_tier("nonsense") raises; reading a non-existent
                               Delta version raises without corrupting the table.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import traceback

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
    get_version_num,
    read_latest,
    read_version,
    write_corpus_v0,
    write_corpus_v1,
)
from warehouse import doc_count_by_category
from choose_tier import choose_tier


# ---------------------------------------------------------------------------
# Assertion helpers
# ---------------------------------------------------------------------------

_results: list[tuple[str, bool, str]] = []   # (label, passed, detail)


def _assert(label: str, condition: bool, detail: str = "") -> None:
    _results.append((label, condition, detail))
    status = "PASS" if condition else "FAIL"
    suffix = f"  [{detail}]" if detail else ""
    print(f"  {status}  {label}{suffix}")


# ---------------------------------------------------------------------------
# Main smoke harness
# ---------------------------------------------------------------------------

def run_smoke(delta_path: str | None = None) -> bool:
    """Run all smoke assertions.  Returns True iff every assertion passes."""

    # Use a temporary directory so the smoke run is always clean and
    # deterministic.  Callers may pass delta_path to target a specific dir
    # (used by the pytest integration test).
    _owned_tmp = delta_path is None
    tmp_dir = tempfile.mkdtemp(prefix="m5_smoke_") if _owned_tmp else None
    path = tmp_dir if _owned_tmp else delta_path

    try:
        print("\n--- Assertion 1: Delta write + version ---")
        df_v0 = build_gold_corpus_v0()
        ver_after_v0 = write_corpus_v0(df_v0, path)
        _assert(
            "version after first write is 0",
            ver_after_v0 == 0,
            f"got {ver_after_v0}",
        )

        df_v1 = build_gold_corpus_v1()
        ver_after_v1 = write_corpus_v1(df_v1, path)
        _assert(
            "version after second write is 1",
            ver_after_v1 == 1,
            f"got {ver_after_v1}",
        )

        current = get_version_num(path)
        _assert(
            "get_version_num() returns 1",
            current == 1,
            f"got {current}",
        )

        history = get_history(path)
        _assert(
            "history contains 2 entries",
            len(history) == 2,
            f"got {len(history)}",
        )

        print("\n--- Assertion 2: Time-travel ---")
        df_latest = read_latest(path)
        df_tt_v0  = read_version(0, path)

        # The updated document's text in the latest snapshot differs from v0
        latest_text = df_latest.loc[df_latest["doc_id"] == UPDATED_DOC_ID, "text"].iloc[0]
        v0_text     = df_tt_v0.loc[df_tt_v0["doc_id"] == UPDATED_DOC_ID, "text"].iloc[0]

        _assert(
            "latest snapshot has updated text for changed doc",
            latest_text == UPDATED_TEXT_V1,
            f"text[:60]={latest_text[:60]!r}",
        )
        _assert(
            "v0 snapshot has original text for changed doc",
            v0_text != UPDATED_TEXT_V1,
            f"text[:60]={v0_text[:60]!r}",
        )
        _assert(
            "v0 and latest snapshots differ",
            not df_tt_v0.equals(df_latest),
        )
        _assert(
            "v0 and latest snapshots have the same row count",
            len(df_tt_v0) == len(df_latest),
            f"v0={len(df_tt_v0)}, latest={len(df_latest)}",
        )

        print("\n--- Assertion 3: Warehouse query (DuckDB category counts) ---")
        counts_df = doc_count_by_category(df_v0)
        counts = dict(zip(counts_df["category"], counts_df["doc_count"]))

        all_counts_match = True
        for cat, expected in EXPECTED_CATEGORY_COUNTS_V0.items():
            actual = counts.get(cat, 0)
            ok = actual == expected
            all_counts_match = all_counts_match and ok
            _assert(
                f"category '{cat}' count == {expected}",
                ok,
                f"got {actual}",
            )
        _assert(
            "all category counts match oracle",
            all_counts_match,
        )

        print("\n--- Assertion 4: Tier decision ---")
        # BI / structured patterns -> warehouse
        for pattern in [
            "bi dashboard for sales reporting",
            "t-sql multi-table join for quarterly finance report",
            "power-bi directquery compliance dashboard",
            "olap reporting endpoint for dimensional model",
        ]:
            tier = choose_tier(pattern)
            _assert(
                f"choose_tier({pattern!r}) == 'warehouse'",
                tier == "warehouse",
                f"got {tier!r}",
            )

        # ML / open-format patterns -> lakehouse
        for pattern in [
            "rag corpus update with embedding refresh",
            "ml feature-store pipeline in spark",
            "open-format delta parquet for data-science exploration",
            "time-travel lineage audit for model training",
        ]:
            tier = choose_tier(pattern)
            _assert(
                f"choose_tier({pattern!r}) == 'lakehouse'",
                tier == "lakehouse",
                f"got {tier!r}",
            )

        print("\n--- Assertion 5: Lineage / M6 preview ---")
        hash_v0 = get_content_hash_at_version(UPDATED_DOC_ID, 0, path)
        hash_latest = get_content_hash_at_version(UPDATED_DOC_ID, 1, path)

        _assert(
            f"content_hash of {UPDATED_DOC_ID} at v0 is not None",
            hash_v0 is not None,
        )
        _assert(
            f"content_hash of {UPDATED_DOC_ID} at v1 is not None",
            hash_latest is not None,
        )
        _assert(
            f"content_hash differs between v0 and v1 (document changed)",
            hash_v0 != hash_latest,
            f"v0={hash_v0}, v1={hash_latest}",
        )

        print("\n--- Assertion 6: Negatives ---")
        # 6a: unknown access pattern raises
        raised_value_error = False
        try:
            choose_tier("nonsense")
        except ValueError:
            raised_value_error = True
        _assert(
            "choose_tier('nonsense') raises ValueError",
            raised_value_error,
        )

        # 6b: reading a non-existent Delta version raises without corrupting table
        raised_on_bad_version = False
        try:
            read_version(999, path)
        except Exception:
            raised_on_bad_version = True

        _assert(
            "read_version(999) raises on non-existent version",
            raised_on_bad_version,
        )

        # Table still intact after the bad read
        version_still_valid = get_version_num(path) == 1
        _assert(
            "table version still 1 after failed time-travel read",
            version_still_valid,
        )

    except Exception:
        print("\n[smoke] UNEXPECTED EXCEPTION — aborting remaining assertions")
        traceback.print_exc()
        return False
    finally:
        if _owned_tmp and tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    passed = all(r[1] for r in _results)
    return passed


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("M5 Module 5 — Warehouses and Lakehouses — Smoke Test")
    print("=" * 60)

    ok = run_smoke()

    total  = len(_results)
    passed = sum(1 for r in _results if r[1])
    failed = total - passed

    print()
    print("=" * 60)
    if ok:
        print(f"RESULT: ALL PASS ({passed}/{total})")
    else:
        print(f"RESULT: FAIL — {failed} assertion(s) failed ({passed}/{total} passed)")
    print("=" * 60)

    sys.exit(0 if ok else 1)
