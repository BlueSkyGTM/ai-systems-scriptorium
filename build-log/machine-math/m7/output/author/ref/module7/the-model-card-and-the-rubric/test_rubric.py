"""Acceptance gate: rubric grader correctness.

Tests
-----
1. Good run -> rubric.grade(result) is all True (6/6).
2. rubric.main() with a good run exits 0.
3. DEFICIENT RUN (no_encoding): R2 fails, rubric.main() exits nonzero.
4. DEFICIENT RUN (no_slicing): R4 fails, rubric.main() exits nonzero.
5. DEFICIENT RUN (stub_card): R6 fails, rubric.main() exits nonzero.
6. Each deficient run fails exactly the expected criterion and no others
   (all other criteria remain True, confirming the rubric is criterion-specific).
"""
import os
import sys

# Path setup: ref/ for ml package, ref/module7/ for pipeline/rubric
_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE7 = os.path.dirname(_HERE)
_REF = os.path.dirname(_MODULE7)

for _p in [_REF, _MODULE7]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest
import pipeline
import rubric

DATA_PATH = os.path.join(_MODULE7, "data.csv")


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def good_result():
    return pipeline.run(DATA_PATH)


@pytest.fixture(scope="module")
def deficient_no_encoding():
    """Omits encoding + scaling -- R2 should fail."""
    return pipeline.run_deficient(DATA_PATH, failure_mode="no_encoding")


@pytest.fixture(scope="module")
def deficient_no_slicing():
    """Omits subgroup slicing -- R4 should fail."""
    return pipeline.run_deficient(DATA_PATH, failure_mode="no_slicing")


@pytest.fixture(scope="module")
def deficient_stub_card():
    """Writes a stub model card -- R6 should fail."""
    return pipeline.run_deficient(DATA_PATH, failure_mode="stub_card")


# ---------------------------------------------------------------------------
# 1. Good run: all 6 criteria pass
# ---------------------------------------------------------------------------

def test_good_run_all_pass(good_result):
    scores = rubric.grade(good_result)
    failing = [cid for cid, passed in scores.items() if not passed]
    assert len(failing) == 0, f"Expected 0 failures on good run; got failures: {failing}"


def test_good_run_six_criteria(good_result):
    scores = rubric.grade(good_result)
    assert len(scores) == 6, f"Expected 6 criteria, got {len(scores)}"


# ---------------------------------------------------------------------------
# 2. rubric.main() exits 0 on a good run
# ---------------------------------------------------------------------------

def test_main_exits_zero_on_good_run(good_result):
    exit_code = rubric.main(result=good_result)
    assert exit_code == 0, f"Expected exit 0 on good run, got {exit_code}"


# ---------------------------------------------------------------------------
# 3. Deficient run: no_encoding fails R2 only
# ---------------------------------------------------------------------------

def test_no_encoding_fails_r2(deficient_no_encoding):
    scores = rubric.grade(deficient_no_encoding)
    assert scores["R2"] is False, "Expected R2 to fail when encoding is skipped"


def test_no_encoding_only_fails_r2(deficient_no_encoding):
    """R1, R3, R4, R5, R6 should still pass when only encoding is skipped."""
    scores = rubric.grade(deficient_no_encoding)
    for cid in ["R1", "R3", "R4", "R5", "R6"]:
        assert scores[cid] is True, (
            f"Criterion {cid} unexpectedly failed in no_encoding run: {scores}"
        )


def test_no_encoding_main_exits_nonzero(deficient_no_encoding):
    exit_code = rubric.main(result=deficient_no_encoding)
    assert exit_code != 0, "Expected nonzero exit when R2 fails"


# ---------------------------------------------------------------------------
# 4. Deficient run: no_slicing fails R4 only
# ---------------------------------------------------------------------------

def test_no_slicing_fails_r4(deficient_no_slicing):
    scores = rubric.grade(deficient_no_slicing)
    assert scores["R4"] is False, "Expected R4 to fail when slicing is skipped"


def test_no_slicing_only_fails_r4(deficient_no_slicing):
    """R1, R2, R3, R5, R6 should still pass when only slicing is skipped."""
    scores = rubric.grade(deficient_no_slicing)
    for cid in ["R1", "R2", "R3", "R5", "R6"]:
        assert scores[cid] is True, (
            f"Criterion {cid} unexpectedly failed in no_slicing run: {scores}"
        )


def test_no_slicing_main_exits_nonzero(deficient_no_slicing):
    exit_code = rubric.main(result=deficient_no_slicing)
    assert exit_code != 0, "Expected nonzero exit when R4 fails"


# ---------------------------------------------------------------------------
# 5. Deficient run: stub_card fails R6 only
# ---------------------------------------------------------------------------

def test_stub_card_fails_r6(deficient_stub_card):
    scores = rubric.grade(deficient_stub_card)
    assert scores["R6"] is False, "Expected R6 to fail when stub card is written"


def test_stub_card_only_fails_r6(deficient_stub_card):
    """R1, R2, R3, R4, R5 should still pass when only the card is stubbed."""
    scores = rubric.grade(deficient_stub_card)
    for cid in ["R1", "R2", "R3", "R4", "R5"]:
        assert scores[cid] is True, (
            f"Criterion {cid} unexpectedly failed in stub_card run: {scores}"
        )


def test_stub_card_main_exits_nonzero(deficient_stub_card):
    exit_code = rubric.main(result=deficient_stub_card)
    assert exit_code != 0, "Expected nonzero exit when R6 fails"
