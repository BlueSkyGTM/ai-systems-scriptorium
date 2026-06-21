"""
test_check_prep.py -- Tests for check_prep.py

Proves two cases for each log:
  - A completed dossier passes (validator returns True / exits 0)
  - A placeholder/incomplete dossier fails (validator returns False / exits 1)

Uses pytest tmp_path; does not depend on the learner's real logs.
Standard library + pytest only. Offline and deterministic.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Load check_prep as a module without assuming it is on sys.path.
# ---------------------------------------------------------------------------

SCRIPT_PATH = Path(__file__).resolve().parent / "check_prep.py"


def load_check_prep():
    spec = importlib.util.spec_from_file_location("check_prep", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


check_prep = load_check_prep()


# ---------------------------------------------------------------------------
# Fixture builders: generate valid and invalid log content
# ---------------------------------------------------------------------------


def make_decomp_log_complete() -> str:
    """
    Return a decomposition-log.md that passes all checks:
    ten Q-entries, all three required fields filled, calibration section.
    """
    entries = []
    for n in range(1, 11):
        entries.append(f"""## Q{n}

**Literal parse:** The action verb is "advocated" and the noun is a technical decision that was wrong. No scope constraint specified.

**Signal category:** Ownership (secondary: Judgment Under Uncertainty)

**Primary hypothesis:** The interviewer is trying to determine whether the candidate takes genuine accountability for outcomes they personally drove, including ones that were wrong.
""")

    calibration = """## Calibration

I read Ownership questions consistently well because the "tell me about a time" framing reliably signals first-person accountability. I underweighted Communication/Influence on Q5 and Q10: I initially categorized them as Judgment because both contained a constraint, but the real signal was whether I can operate in an organization. The pattern was conflating an organizational constraint with a technical tradeoff.
"""

    return calibration + "\n".join(entries)


def make_decomp_log_incomplete() -> str:
    """
    Return a decomposition-log.md with only three Q-entries and placeholder text.
    This must fail validation.
    """
    return """## Calibration

TODO: Write your calibration here after completing all ten entries.

## Q1

**Literal parse:** TODO

**Signal category:** TODO

**Primary hypothesis:** TODO

## Q2

**Literal parse:** The framing strips to a technical decision under incomplete information.

**Signal category:** Judgment Under Uncertainty

**Primary hypothesis:** TODO

## Q3

**Literal parse:** TODO

**Signal category:** Ownership

**Primary hypothesis:** The interviewer is trying to determine whether the candidate owns outcomes.
"""


def _make_answer_entry(n: int) -> str:
    """Return one complete ## A<n> entry with all four steps and three scores."""
    return f"""## A{n}

### Step 1: Decompose

**Literal parse:** The action noun is a technical decision that was wrong; the framing asks for a specific past event.

**Signal category:** Ownership (secondary: Judgment Under Uncertainty)

**Primary hypothesis:** The interviewer is trying to determine whether the candidate takes genuine accountability for outcomes they personally drove.

### Step 2: Identify the Signal

**Restated hypothesis:** The candidate must show they owned the original call and the correction, not just that a project was difficult.

**Evidence required:** A named decision, a concrete failure signal, a public correction, and a structural lesson.

### Step 3: Construct the Answer

I pushed to replace our retrieval pipeline with a pure long-context approach across two design reviews. The team committed a quarter to the migration partly on my conviction. When I ran the eval before full cutover, quality matched but cost ran four times my projection: cache hit rates collapsed under our update frequency and p95 latency doubled. After two weeks of marginal tuning gains, I wrote a one-page memo stating plainly that my recommendation was wrong on the economics. I proposed a hybrid, presented it to the same audience, and we kept it. The postmortem produced a team rule: any architecture pitch must include a cost model under realistic update patterns.

### Step 4: Stress-Test

The specifics that block a weak candidate: "cost ran four times my projection," "cache hit rates collapsed under update frequency," "two weeks of marginal gains before I stopped," "one-page memo." A weak candidate would say "I learned to think about costs." This answer passes.

### Scores

**Specificity:** strong
**Structure:** strong
**Completeness:** strong
"""


def make_answers_log_complete() -> str:
    """
    Return an answers-log.md that passes all checks:
    five A-entries, all four steps, all three scores with valid values.
    """
    return "\n".join(_make_answer_entry(n) for n in range(1, 6))


def make_answers_log_incomplete() -> str:
    """
    Return an answers-log.md with only two entries and placeholder scores.
    This must fail validation.
    """
    return """## A1

### Step 1: Decompose

**Literal parse:** TODO

**Signal category:** TODO

**Primary hypothesis:** TODO

### Step 2: Identify the Signal

**Restated hypothesis:** TODO

**Evidence required:** TODO

### Step 3: Construct the Answer

TODO

### Step 4: Stress-Test

TODO

### Scores

**Specificity:** TODO
**Structure:** TODO
**Completeness:** TODO

## A2

### Step 1: Decompose

**Literal parse:** A project that failed; the framing asks for a past event.

**Signal category:** Ownership

**Primary hypothesis:** The interviewer is trying to determine whether the candidate owns failure outcomes.

### Step 2: Identify the Signal

**Restated hypothesis:** The candidate must show genuine accountability and a structural lesson.

**Evidence required:** Named failure signal, candidate-owned action, concrete lesson.

### Step 3: Construct the Answer

A short answer that would not survive a stress test.

### Step 4: Stress-Test

This answer is too general; a weak candidate could give it. Revision needed: add the specific metric that signaled failure and the exact decision point.

### Scores

**Specificity:** weak
**Structure:** partial
**Completeness:** weak
"""


# ---------------------------------------------------------------------------
# Tests: decomposition-log.md
# ---------------------------------------------------------------------------


class TestDecompositionLog:
    def test_complete_log_passes(self, tmp_path: Path) -> None:
        """A fully completed decomposition log must pass validation."""
        log = tmp_path / "decomposition-log.md"
        log.write_text(make_decomp_log_complete(), encoding="utf-8")

        # Patch the module's DECOMP_LOG path to our temp file.
        original = check_prep.DECOMP_LOG
        check_prep.DECOMP_LOG = log
        try:
            passed, messages = check_prep.validate_decomposition_log(log)
        finally:
            check_prep.DECOMP_LOG = original

        assert passed, f"Expected pass; got messages:\n" + "\n".join(messages)

    def test_incomplete_log_fails(self, tmp_path: Path) -> None:
        """A log with too few entries and placeholder text must fail validation."""
        log = tmp_path / "decomposition-log.md"
        log.write_text(make_decomp_log_incomplete(), encoding="utf-8")

        passed, messages = check_prep.validate_decomposition_log(log)

        assert not passed, "Expected fail; validator incorrectly returned pass."
        # Confirm the report mentions the entry count or placeholder issue.
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"

    def test_missing_log_fails(self, tmp_path: Path) -> None:
        """An absent log must return fail with a clear not-started message."""
        missing = tmp_path / "decomposition-log.md"
        # Do not create the file.

        passed, messages = check_prep.validate_decomposition_log(missing)

        assert not passed
        combined = "\n".join(messages)
        assert "NOT STARTED" in combined or "does not exist" in combined


# ---------------------------------------------------------------------------
# Tests: answers-log.md
# ---------------------------------------------------------------------------


class TestAnswersLog:
    def test_complete_log_passes(self, tmp_path: Path) -> None:
        """A fully completed answers log must pass validation."""
        log = tmp_path / "answers-log.md"
        log.write_text(make_answers_log_complete(), encoding="utf-8")

        passed, messages = check_prep.validate_answers_log(log)

        assert passed, f"Expected pass; got messages:\n" + "\n".join(messages)

    def test_incomplete_log_fails(self, tmp_path: Path) -> None:
        """A log with too few entries and placeholder scores must fail."""
        log = tmp_path / "answers-log.md"
        log.write_text(make_answers_log_incomplete(), encoding="utf-8")

        passed, messages = check_prep.validate_answers_log(log)

        assert not passed, "Expected fail; validator incorrectly returned pass."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"

    def test_missing_log_fails(self, tmp_path: Path) -> None:
        """An absent answers log must return fail with a clear not-started message."""
        missing = tmp_path / "answers-log.md"

        passed, messages = check_prep.validate_answers_log(missing)

        assert not passed
        combined = "\n".join(messages)
        assert "NOT STARTED" in combined or "does not exist" in combined


# ---------------------------------------------------------------------------
# Integration: main() exit codes
# ---------------------------------------------------------------------------


class TestMainExitCode:
    def test_both_complete_exits_zero(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When both logs are complete, main() must return 0."""
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        decomp.write_text(make_decomp_log_complete(), encoding="utf-8")
        answers.write_text(make_answers_log_complete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        # argparse reads sys.argv; clear it so pytest's own args don't interfere.
        monkeypatch.setattr(sys, "argv", ["check_prep.py"])

        result = check_prep.main()
        assert result == 0, f"Expected exit 0; got {result}"

    def test_both_missing_exits_one(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When both logs are absent, main() must return 1."""
        monkeypatch.setattr(check_prep, "DECOMP_LOG", tmp_path / "decomposition-log.md")
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", tmp_path / "answers-log.md")
        monkeypatch.setattr(sys, "argv", ["check_prep.py"])

        result = check_prep.main()
        assert result == 1, f"Expected exit 1; got {result}"

    def test_one_incomplete_exits_one(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When decomp log is complete but answers log is not, main() must return 1."""
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        decomp.write_text(make_decomp_log_complete(), encoding="utf-8")
        answers.write_text(make_answers_log_incomplete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        monkeypatch.setattr(sys, "argv", ["check_prep.py"])

        result = check_prep.main()
        assert result == 1, f"Expected exit 1; got {result}"
