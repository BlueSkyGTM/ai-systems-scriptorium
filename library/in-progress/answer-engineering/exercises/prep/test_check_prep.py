"""
test_check_prep.py -- Tests for check_prep.py

Proves two cases for each log:
  - A completed dossier passes (validator returns True / exits 0)
  - A placeholder/incomplete dossier fails (validator returns False / exits 1)

M1 tests cover decomposition-log.md and answers-log.md.
M2 tests cover the Hard Cases extension, signal-map.md, practice-log.md,
and audit-log.md, plus --module flag behavior.

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
# Fixture builders: M1 logs
# ---------------------------------------------------------------------------


def make_decomp_log_complete() -> str:
    """
    Return a decomposition-log.md that passes all M1 checks:
    ten Q-entries, all three required fields filled, calibration section.
    Does NOT include a Hard Cases section.
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


def make_decomp_log_with_hard_cases() -> str:
    """
    Return a decomposition-log.md that passes both M1 and M2 Hard Cases checks.
    Includes the base log plus a ## Hard Cases section with three HC entries.
    """
    base = make_decomp_log_complete()
    hard_cases = """
## Hard Cases

### HC1

**Senior reading:** The question collects Ownership at the senior level: the candidate is expected to show they personally drove the initiative, influenced others without authority, and owned the outcome.

**Primary hypothesis (senior):** The interviewer is trying to determine whether the candidate can own a technical direction and move others without relying on formal rank.

**Staff reading:** At staff level, the question collects Communication/Influence as primary: the candidate is expected to show how the initiative changed what other engineers could do, not just what the candidate shipped personally.

**Primary hypothesis (staff):** The interviewer is trying to determine whether the candidate can change organizational behavior and leave a platform, standard, or process that outlasts their direct involvement.

**How the hypothesis shifts:** The shift is from personal ownership of a technical outcome to organizational multiplication. A senior answer proves the candidate can lead; a staff answer proves the candidate can scale.

### HC2

**Senior reading:** The question collects Communication/Influence at the senior level: the candidate must show they converted a lost argument into productive action without relitigating the decision.

**Primary hypothesis (senior):** The interviewer is trying to determine whether the candidate can commit to a decision they disagreed with while protecting the outcome they cared about through legitimate means.

**Staff reading:** At staff level, the question adds a governance signal: the candidate is expected to show how they documented the disagreement and built a record that could surface the risk later, not just that they committed professionally.

**Primary hypothesis (staff):** The interviewer is trying to determine whether the candidate can operate inside a governance structure, build a written record, and convert a lost argument into cheap insurance.

**How the hypothesis shifts:** At senior, the bar is professional commitment. At staff, the bar is institutional risk management: the written disagreement record and the targeted mitigation are the staff artifact.

### HC3

**Senior reading:** The question collects Ownership at the senior level: the candidate must show they took genuine accountability for a call they drove and corrected it publicly.

**Primary hypothesis (senior):** The interviewer is trying to determine whether the candidate owns wrong calls and corrects them without deflecting to external factors.

**Staff reading:** At staff level, the question also collects Judgment: the candidate is expected to show not just that they corrected the call, but that the correction produced a reusable standard or process that changed how the team makes similar calls in the future.

**Primary hypothesis (staff):** The interviewer is trying to determine whether the candidate can extract a reusable organizational lesson from a public failure and install it as a team-level standard, not just a personal lesson.

**How the hypothesis shifts:** The senior bar is clean public accountability. The staff bar requires an organizational artifact: the postmortem rule, the review checklist, the architecture standard that came out of the failure.
"""
    return base + hard_cases


def make_decomp_log_incomplete() -> str:
    """
    Return a decomposition-log.md with only three Q-entries and placeholder text.
    This must fail M1 validation.
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
# Fixture builders: M2 logs
# ---------------------------------------------------------------------------


def make_signal_map_complete() -> str:
    """Return a signal-map.md that passes all M2 checks: three SM entries, all fields filled."""
    return """# Signal Map

### SM1

**Stated signal:** Communication/Influence (primary), Ownership (secondary)

**Latent signal:** The question probes whether the candidate can operate in an organization where influence is the mechanism and authority is not available. A weak answer demonstrates personal technical work; the real probe is whether the candidate changed behavior in other people without being able to order them to change.

**Frontier lab context:** At a frontier lab, the emphasis shifts to whether the candidate's approach to influence included making the safety or alignment reasoning transparent. Bringing others along by making the logic visible is weighted more than showing speed of delivery.

**Enterprise context:** At an enterprise, the emphasis shifts to whether the candidate documented the initiative in a way that survived their departure and whether they looped in compliance or governance stakeholders before acting.

### SM2

**Stated signal:** Communication/Influence (primary), Judgment (secondary)

**Latent signal:** The question probes whether the candidate can convert a lost argument into protective action without relitigating the decision. The weak answer shows professional resignation; the real probe is whether the candidate built a record that could surface the risk later.

**Frontier lab context:** At a frontier lab, the concern flag and the response to being overruled both carry safety weight. The interviewer wants to see that the candidate escalated in writing and proposed a concrete mitigation, not just that they committed gracefully.

**Enterprise context:** At an enterprise, the documentation of the disagreement and the specific mitigation within the launch window are the signal. Compliance and audit trails matter; a verbal commitment to revisit is not enough.

### SM3

**Stated signal:** Communication/Influence (primary), Judgment (secondary)

**Latent signal:** The question probes whether the candidate can work across an organizational boundary defined by different incentives, not just different opinions. Researchers optimize for capability; engineers optimize for production reliability. The real probe is whether the candidate found a shared frame, not just managed the friction.

**Frontier lab context:** At a frontier lab, the research-to-production handoff is structurally important. The interviewer weights whether the candidate established a process or template that changed how the two teams work together, not just that they got one project across the line.

**Enterprise context:** At an enterprise, the emphasis shifts to stakeholder management at the organizational level: did the candidate involve the right approvers, and did the outcome fit inside the governance structure? Showing that a research result was validated against a compliance requirement before productionization is a strong signal.
"""


def make_signal_map_incomplete() -> str:
    """Return a signal-map.md that fails: only one entry and placeholder text."""
    return """# Signal Map

### SM1

**Stated signal:** TODO

**Latent signal:** TODO

**Frontier lab context:** TODO

**Enterprise context:** TODO
"""


def make_practice_log_complete() -> str:
    """Return a practice-log.md that passes: two PL entries, all fields filled."""
    return """# Practice Log

### PL1

**2-minute version:** I pushed hard to replace our retrieval pipeline with a pure long-context approach in two design reviews. The argument was that newer models could handle our corpus in-context without retrieval overhead. The team committed a quarter to the migration on my conviction. When I ran the eval before cutover, quality matched but cost ran four times my projection. Cache hit rates collapsed under our update frequency; p95 latency doubled. I spent two weeks watching for a cost inflection that did not come. After that, I stopped. I wrote a one-page memo stating plainly that my recommendation was wrong on the economics. I proposed a hybrid and presented it to the same audience. We kept it. The postmortem produced one rule: any architecture pitch requires a cost model under realistic update patterns. I still attach kill criteria to my own proposals. (Timed: 1 min 55 sec)

**30-second version:** I pushed a retrieval-to-long-context migration that failed on cost: four times my projection at realistic update frequency. After two weeks without a cost inflection, I wrote a one-page memo calling the recommendation wrong, proposed a hybrid, and got it approved. Lesson: attach a kill criterion to your own proposals. (Timed: 27 sec)

**Delivery self-score:** The long version buries the hybrid-approval result at 1:40; it should arrive by 1:00. No significant filler words detected. The phrase "I spent two weeks watching for a cost inflection that did not come" is stronger than the original "tuning my way out of it" but still slightly passive; the stopping decision should be active. The thirty-second version correctly collapses to result and learning; it does not retain unnecessary situation framing. One sentence to cut from the long version: "The argument was that newer models could handle our corpus in-context without retrieval overhead" -- this is context nobody asked for.

### PL2

**2-minute version:** Before a launch, I flagged that the agent's tool permissions were broader than the feature needed: it could write to systems it only needed to read. Leadership decided to ship as-is with a fast-follow ticket. I disagreed. I converted the lost argument into two cheap mitigations that fit inside the launch window: an audit log on the write paths and an anomaly alert on write volume. I wrote the risk down concretely: specific blast radius if the agent were prompt-injected, with a realistic attack path. I documented my disagreement in the decision record and committed without relitigating. The launch was fine. Three weeks later the alert fired on a misconfigured integration test, proving the monitoring worked. The permission scoping shipped a month later. (Timed: 1 min 48 sec)

**30-second version:** I flagged a permission-scope risk before launch, was overruled, and converted the lost argument into two targeted mitigations: an audit log and an anomaly alert. Both proved their value within a month. Lesson: a lost argument is not the end of the job; cheap guardrails often do more than winning. (Timed: 24 sec)

**Delivery self-score:** The long version is well-paced; the risk framing arrives early and the monitoring payoff arrives naturally at the end. One filler pattern: "I disagree" followed immediately by "I converted" is slightly abrupt; a single connector word helps. The thirty-second version collapses correctly to result and learning. One sentence to tighten in the long version: "I wrote the risk down concretely: specific blast radius if the agent were prompt-injected, with a realistic attack path" could move earlier to frame why the two mitigations were chosen.
"""


def make_practice_log_incomplete() -> str:
    """Return a practice-log.md that fails: only one entry with placeholder text."""
    return """# Practice Log

### PL1

**2-minute version:** TODO

**30-second version:** TODO

**Delivery self-score:** TODO
"""


def make_audit_log_complete() -> str:
    """Return an audit-log.md that passes: two AL entries, all fields filled."""
    return """# Audit Log

### AL1

**Pitfalls present:** Vague ownership: absent -- "I pushed," "I ran the eval," "I wrote the memo" make ownership clear throughout. Buried result: borderline -- the hybrid approval and 60% salvage appear late in the spoken version but are acceptable in the written form. Missing failure signal: absent -- "cost ran four times my projection" and "cache hit rates collapsed under update frequency" are concrete. No structural lesson: absent -- "any architecture pitch must include a cost model under realistic update patterns" is a named practice change with team scope.

**Basic bar verdict:** Passes. The specifics -- "cost ran four times my projection," "two weeks of marginal gains before I stopped," "one-page memo stating plainly the recommendation was wrong" -- block a weak candidate who would say only "I learned to think about costs."

**Staff bar verdict:** Borderline pass. The organizational artifact is present ("the postmortem produced one rule") but understated. A strong staff answer would name the adoption scope: did the rule become a review checklist, a shared template, or a standard that other teams adopted? The current form reads as a personal lesson with team reach, not a platform-level standard.

**Revised sentence:** Original: "I spent two weeks trying to tune my way out of it." Revision: "For two weeks I monitored the hybrid parameters, watching for a cost inflection that did not come." The revision makes the stopping condition explicit and the decision to stop active rather than passive.

### AL2

**Pitfalls present:** Vague ownership: absent -- the candidate is explicitly named as the person who raised the flag and wrote the risk assessment. Buried result: absent -- the alert firing is the payoff and it arrives naturally at the end. Missing failure signal: present in a subtle form -- the answer names the risk concretely but does not name a moment where the permission scope actually caused a problem before launch; the risk is prospective, not realized. No structural lesson: absent -- the audit log and alert are named organizational artifacts; the permission scoping shipping a month later is a follow-through signal.

**Basic bar verdict:** Passes. The specifics -- "specific blast radius if the agent were prompt-injected," "audit log on the write paths," "anomaly alert on write volume," "documented disagreement in the decision record" -- make this unfakeable by a weak candidate who would say only "I raised a concern and moved on."

**Staff bar verdict:** Passes at the low end. The organizational artifacts (audit log, anomaly alert, decision record, permission scoping) are named, and at least one (the monitoring) proved its value. A stronger staff answer would show whether the governance process itself changed: did this incident change how the team reviews permission scope before launches, or did it remain a one-off?

**Revised sentence:** Original: "I disagreed." Revision: "I committed to the launch while protecting the outcome: two cheap mitigations targeted the specific risk." The revision shows the candidate's reasoning, not just their emotional state.
"""


def make_audit_log_incomplete() -> str:
    """Return an audit-log.md that fails: only one entry with placeholder text."""
    return """# Audit Log

### AL1

**Pitfalls present:** TODO

**Basic bar verdict:** TODO

**Staff bar verdict:** TODO

**Revised sentence:** TODO
"""


# ---------------------------------------------------------------------------
# Tests: decomposition-log.md (M1)
# ---------------------------------------------------------------------------


class TestDecompositionLog:
    def test_complete_log_passes(self, tmp_path: Path) -> None:
        """A fully completed decomposition log must pass M1 validation."""
        log = tmp_path / "decomposition-log.md"
        log.write_text(make_decomp_log_complete(), encoding="utf-8")

        # Patch the module's DECOMP_LOG path to our temp file.
        original = check_prep.DECOMP_LOG
        check_prep.DECOMP_LOG = log
        try:
            passed, messages = check_prep.validate_decomposition_log(log, check_hard_cases=False)
        finally:
            check_prep.DECOMP_LOG = original

        assert passed, f"Expected pass; got messages:\n" + "\n".join(messages)

    def test_incomplete_log_fails(self, tmp_path: Path) -> None:
        """A log with too few entries and placeholder text must fail M1 validation."""
        log = tmp_path / "decomposition-log.md"
        log.write_text(make_decomp_log_incomplete(), encoding="utf-8")

        passed, messages = check_prep.validate_decomposition_log(log, check_hard_cases=False)

        assert not passed, "Expected fail; validator incorrectly returned pass."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"

    def test_missing_log_fails(self, tmp_path: Path) -> None:
        """An absent log must return fail with a clear not-started message."""
        missing = tmp_path / "decomposition-log.md"
        # Do not create the file.

        passed, messages = check_prep.validate_decomposition_log(missing, check_hard_cases=False)

        assert not passed
        combined = "\n".join(messages)
        assert "NOT STARTED" in combined or "does not exist" in combined


# ---------------------------------------------------------------------------
# Tests: answers-log.md (M1)
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
# Tests: Hard Cases extension (M2 addition to decomposition-log.md)
# ---------------------------------------------------------------------------


class TestHardCases:
    def test_complete_hard_cases_passes(self, tmp_path: Path) -> None:
        """A decomp log with a complete Hard Cases section must pass M2 checks."""
        log = tmp_path / "decomposition-log.md"
        log.write_text(make_decomp_log_with_hard_cases(), encoding="utf-8")

        passed, messages = check_prep.validate_decomposition_log(log, check_hard_cases=True)

        assert passed, f"Expected pass; got messages:\n" + "\n".join(messages)

    def test_missing_hard_cases_fails(self, tmp_path: Path) -> None:
        """A decomp log with no Hard Cases section must fail when M2 checks are on."""
        log = tmp_path / "decomposition-log.md"
        log.write_text(make_decomp_log_complete(), encoding="utf-8")

        passed, messages = check_prep.validate_decomposition_log(log, check_hard_cases=True)

        assert not passed, "Expected fail; validator incorrectly returned pass."
        combined = "\n".join(messages)
        assert "Hard Cases" in combined, f"Expected 'Hard Cases' in messages; got:\n{combined}"

    def test_m1_only_does_not_require_hard_cases(self, tmp_path: Path) -> None:
        """A log without Hard Cases must pass when check_hard_cases=False."""
        log = tmp_path / "decomposition-log.md"
        log.write_text(make_decomp_log_complete(), encoding="utf-8")

        passed, messages = check_prep.validate_decomposition_log(log, check_hard_cases=False)

        assert passed, f"Expected pass on M1-only check; got:\n" + "\n".join(messages)


# ---------------------------------------------------------------------------
# Tests: signal-map.md (M2)
# ---------------------------------------------------------------------------


class TestSignalMap:
    def test_complete_map_passes(self, tmp_path: Path) -> None:
        """A fully completed signal map must pass validation."""
        log = tmp_path / "signal-map.md"
        log.write_text(make_signal_map_complete(), encoding="utf-8")

        passed, messages = check_prep.validate_signal_map(log)

        assert passed, f"Expected pass; got messages:\n" + "\n".join(messages)

    def test_incomplete_map_fails(self, tmp_path: Path) -> None:
        """A signal map with too few entries and placeholder text must fail."""
        log = tmp_path / "signal-map.md"
        log.write_text(make_signal_map_incomplete(), encoding="utf-8")

        passed, messages = check_prep.validate_signal_map(log)

        assert not passed, "Expected fail; validator incorrectly returned pass."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"

    def test_missing_map_fails(self, tmp_path: Path) -> None:
        """An absent signal map must return fail with a not-started message."""
        missing = tmp_path / "signal-map.md"

        passed, messages = check_prep.validate_signal_map(missing)

        assert not passed
        combined = "\n".join(messages)
        assert "NOT STARTED" in combined or "does not exist" in combined


# ---------------------------------------------------------------------------
# Tests: practice-log.md (M2)
# ---------------------------------------------------------------------------


class TestPracticeLog:
    def test_complete_log_passes(self, tmp_path: Path) -> None:
        """A fully completed practice log must pass validation."""
        log = tmp_path / "practice-log.md"
        log.write_text(make_practice_log_complete(), encoding="utf-8")

        passed, messages = check_prep.validate_practice_log(log)

        assert passed, f"Expected pass; got messages:\n" + "\n".join(messages)

    def test_incomplete_log_fails(self, tmp_path: Path) -> None:
        """A practice log with one entry and placeholder text must fail."""
        log = tmp_path / "practice-log.md"
        log.write_text(make_practice_log_incomplete(), encoding="utf-8")

        passed, messages = check_prep.validate_practice_log(log)

        assert not passed, "Expected fail; validator incorrectly returned pass."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"

    def test_missing_log_fails(self, tmp_path: Path) -> None:
        """An absent practice log must return fail with a not-started message."""
        missing = tmp_path / "practice-log.md"

        passed, messages = check_prep.validate_practice_log(missing)

        assert not passed
        combined = "\n".join(messages)
        assert "NOT STARTED" in combined or "does not exist" in combined


# ---------------------------------------------------------------------------
# Tests: audit-log.md (M2)
# ---------------------------------------------------------------------------


class TestAuditLog:
    def test_complete_log_passes(self, tmp_path: Path) -> None:
        """A fully completed audit log must pass validation."""
        log = tmp_path / "audit-log.md"
        log.write_text(make_audit_log_complete(), encoding="utf-8")

        passed, messages = check_prep.validate_audit_log(log)

        assert passed, f"Expected pass; got messages:\n" + "\n".join(messages)

    def test_incomplete_log_fails(self, tmp_path: Path) -> None:
        """An audit log with one entry and placeholder text must fail."""
        log = tmp_path / "audit-log.md"
        log.write_text(make_audit_log_incomplete(), encoding="utf-8")

        passed, messages = check_prep.validate_audit_log(log)

        assert not passed, "Expected fail; validator incorrectly returned pass."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"

    def test_missing_log_fails(self, tmp_path: Path) -> None:
        """An absent audit log must return fail with a not-started message."""
        missing = tmp_path / "audit-log.md"

        passed, messages = check_prep.validate_audit_log(missing)

        assert not passed
        combined = "\n".join(messages)
        assert "NOT STARTED" in combined or "does not exist" in combined


# ---------------------------------------------------------------------------
# Tests: --module flag behavior
# ---------------------------------------------------------------------------


class TestModuleFlag:
    def test_module1_passes_without_m2_artifacts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 1 must exit 0 when only M1 artifacts are complete."""
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        decomp.write_text(make_decomp_log_complete(), encoding="utf-8")
        answers.write_text(make_answers_log_complete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        # M2 artifacts are absent -- the tmp_path has none.
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", tmp_path / "signal-map.md")
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", tmp_path / "practice-log.md")
        monkeypatch.setattr(check_prep, "AUDIT_LOG", tmp_path / "audit-log.md")
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "1"])

        result = check_prep.main()
        assert result == 0, f"Expected exit 0 with --module 1; got {result}"

    def test_module2_fails_without_m2_artifacts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 2 must exit 1 when M2 artifacts are absent, even if M1 is complete."""
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        decomp.write_text(make_decomp_log_complete(), encoding="utf-8")
        answers.write_text(make_answers_log_complete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", tmp_path / "signal-map.md")
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", tmp_path / "practice-log.md")
        monkeypatch.setattr(check_prep, "AUDIT_LOG", tmp_path / "audit-log.md")
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "2"])

        result = check_prep.main()
        assert result == 1, f"Expected exit 1 with --module 2 and no M2 artifacts; got {result}"

    def test_module2_passes_with_all_artifacts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 2 must exit 0 when all M1 and M2 artifacts are complete."""
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        signal_map = tmp_path / "signal-map.md"
        practice = tmp_path / "practice-log.md"
        audit = tmp_path / "audit-log.md"

        decomp.write_text(make_decomp_log_with_hard_cases(), encoding="utf-8")
        answers.write_text(make_answers_log_complete(), encoding="utf-8")
        signal_map.write_text(make_signal_map_complete(), encoding="utf-8")
        practice.write_text(make_practice_log_complete(), encoding="utf-8")
        audit.write_text(make_audit_log_complete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", signal_map)
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", practice)
        monkeypatch.setattr(check_prep, "AUDIT_LOG", audit)
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "2"])

        result = check_prep.main()
        assert result == 0, f"Expected exit 0 with --module 2 and all artifacts; got {result}"


# ---------------------------------------------------------------------------
# Integration: main() exit codes (M1 subset, backward compat)
# ---------------------------------------------------------------------------


class TestMainExitCode:
    def test_both_complete_exits_zero(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When both M1 logs are complete, main() with --module 1 must return 0."""
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        decomp.write_text(make_decomp_log_complete(), encoding="utf-8")
        answers.write_text(make_answers_log_complete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", tmp_path / "signal-map.md")
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", tmp_path / "practice-log.md")
        monkeypatch.setattr(check_prep, "AUDIT_LOG", tmp_path / "audit-log.md")
        # argparse reads sys.argv; clear it so pytest's own args don't interfere.
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "1"])

        result = check_prep.main()
        assert result == 0, f"Expected exit 0; got {result}"

    def test_both_missing_exits_one(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When both logs are absent, main() must return 1."""
        monkeypatch.setattr(check_prep, "DECOMP_LOG", tmp_path / "decomposition-log.md")
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", tmp_path / "answers-log.md")
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", tmp_path / "signal-map.md")
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", tmp_path / "practice-log.md")
        monkeypatch.setattr(check_prep, "AUDIT_LOG", tmp_path / "audit-log.md")
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "1"])

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
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", tmp_path / "signal-map.md")
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", tmp_path / "practice-log.md")
        monkeypatch.setattr(check_prep, "AUDIT_LOG", tmp_path / "audit-log.md")
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "1"])

        result = check_prep.main()
        assert result == 1, f"Expected exit 1; got {result}"


# ---------------------------------------------------------------------------
# Fixture builders: M3 behavioral bank
# ---------------------------------------------------------------------------


def _make_bank_story(n: int, category: str) -> str:
    """Return one complete ## Story <n> entry with all required fields filled."""
    return f"""## Story {n}

**Category:** {category}

**Situation:** I was the ML engineer responsible for a production recommendation system that underperformed significantly after launch, showing 30% lower engagement than the heuristic baseline.

**Task:** I had to diagnose the issue, decide whether to roll back, and regain stakeholder trust, all under pressure from the product team.

**Action:** I did not hide the problem. I immediately flagged it to leadership with the data showing the gap. I proposed keeping 10% of traffic on the new system while I investigated. I found two issues: the test set was not representative because it drew from high-engagement users only, and cold start was worse than expected. I implemented stratified testing matching production distribution and added a heuristic fallback for cold users.

**Result:** The revised system outperformed the heuristic baseline by 15% after two more weeks of iteration. The testing practice I established caught two similar issues in subsequent projects.

**Learning:** Production is the only true test for ML systems. I now always require a stratified test set matched to production user distribution before any model launch, and I plan for a rapid iteration loop rather than treating launch as a final gate.

**Audit verdict:** Pitfalls checked: vague ownership -- absent ("I flagged," "I found," "I implemented" carry first-person accountability); buried result -- absent (the 15% improvement appears clearly in the Result step); missing failure signal -- absent ("30% lower engagement than heuristic baseline" is concrete and named); no structural lesson -- absent (stratified testing and heuristic fallback for cold users became named practice changes). Basic bar: passes -- "30% lower engagement," "10% traffic hold," "stratified testing matched production user distribution," and "15% after two weeks" are specific enough that a weak candidate cannot replicate them. Staff bar: borderline pass -- the testing practice was reused in subsequent projects but the story does not name a team-level standard or process adopted by others. One specific thing added after audit: the Result step originally ended at "outperformed baseline" with no mention of subsequent projects; the reuse by others was added to reach toward the staff bar.
"""


def make_behavioral_bank_complete() -> str:
    """
    Return a behavioral-bank.md that passes all M3 checks: four stories
    covering all four categories, all required fields filled, no placeholders.
    """
    categories = ["ownership", "conflict", "failure", "influence"]
    stories = [_make_bank_story(i + 1, cat) for i, cat in enumerate(categories)]
    return "# Behavioral Bank\n\n" + "\n".join(stories)


def make_behavioral_bank_incomplete() -> str:
    """
    Return a behavioral-bank.md that fails: only two stories and placeholder text.
    """
    return """# Behavioral Bank

## Story 1

**Category:** ownership

**Situation:** TODO

**Task:** TODO

**Action:** TODO

**Result:** TODO

**Learning:** TODO

**Audit verdict:** TODO

## Story 2

**Category:** conflict

**Situation:** I had a disagreement with a PM about AI capabilities.

**Task:** TODO

**Action:** TODO

**Result:** TODO

**Learning:** TODO

**Audit verdict:** TODO
"""


def make_behavioral_bank_missing_category() -> str:
    """
    Return a behavioral-bank.md that fails because only three of four categories
    appear (ownership appears twice; influence is missing).
    """
    return (
        "# Behavioral Bank\n\n"
        + _make_bank_story(1, "ownership")
        + _make_bank_story(2, "conflict")
        + _make_bank_story(3, "failure")
        + _make_bank_story(4, "ownership")  # duplicate instead of influence
    )


# ---------------------------------------------------------------------------
# Tests: behavioral-bank.md (M3)
# ---------------------------------------------------------------------------


class TestBehavioralBank:
    def test_complete_bank_passes(self, tmp_path: Path) -> None:
        """A fully completed behavioral bank must pass M3 validation."""
        bank = tmp_path / "behavioral-bank.md"
        bank.write_text(make_behavioral_bank_complete(), encoding="utf-8")

        passed, messages = check_prep.validate_behavioral_bank(bank)

        assert passed, f"Expected pass; got messages:\n" + "\n".join(messages)

    def test_incomplete_bank_fails(self, tmp_path: Path) -> None:
        """A bank with placeholder text and too few entries must fail."""
        bank = tmp_path / "behavioral-bank.md"
        bank.write_text(make_behavioral_bank_incomplete(), encoding="utf-8")

        passed, messages = check_prep.validate_behavioral_bank(bank)

        assert not passed, "Expected fail; validator incorrectly returned pass."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"

    def test_missing_bank_fails(self, tmp_path: Path) -> None:
        """An absent behavioral bank must return fail with a not-started message."""
        missing = tmp_path / "behavioral-bank.md"

        passed, messages = check_prep.validate_behavioral_bank(missing)

        assert not passed
        combined = "\n".join(messages)
        assert "NOT STARTED" in combined or "does not exist" in combined

    def test_missing_category_fails(self, tmp_path: Path) -> None:
        """A bank with four entries but only three categories must fail."""
        bank = tmp_path / "behavioral-bank.md"
        bank.write_text(make_behavioral_bank_missing_category(), encoding="utf-8")

        passed, messages = check_prep.validate_behavioral_bank(bank)

        assert not passed, "Expected fail when a category is missing; validator passed incorrectly."
        combined = "\n".join(messages)
        assert "influence" in combined.lower(), (
            f"Expected 'influence' named in failure messages; got:\n{combined}"
        )


# ---------------------------------------------------------------------------
# Tests: --module 3 flag behavior (M3)
# ---------------------------------------------------------------------------


class TestModule3Flag:
    def _patch_m1_m2(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        m1_complete: bool = True,
    ) -> None:
        """Helper: patch all M1 and M2 paths into tmp_path with complete content."""
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        signal_map = tmp_path / "signal-map.md"
        practice = tmp_path / "practice-log.md"
        audit = tmp_path / "audit-log.md"

        if m1_complete:
            decomp.write_text(make_decomp_log_with_hard_cases(), encoding="utf-8")
            answers.write_text(make_answers_log_complete(), encoding="utf-8")
        # else: leave files absent

        signal_map.write_text(make_signal_map_complete(), encoding="utf-8")
        practice.write_text(make_practice_log_complete(), encoding="utf-8")
        audit.write_text(make_audit_log_complete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", signal_map)
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", practice)
        monkeypatch.setattr(check_prep, "AUDIT_LOG", audit)

    def test_module2_passes_without_behavioral_bank(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 2 must exit 0 on a complete M1+M2 dossier even with no behavioral bank."""
        self._patch_m1_m2(tmp_path, monkeypatch)
        monkeypatch.setattr(check_prep, "BEHAVIORAL_BANK", tmp_path / "behavioral-bank.md")
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "2"])

        result = check_prep.main()
        assert result == 0, f"Expected exit 0 with --module 2 and no behavioral bank; got {result}"

    def test_module3_fails_without_behavioral_bank(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 3 must exit 1 when behavioral-bank.md is absent, even if M1+M2 are complete."""
        self._patch_m1_m2(tmp_path, monkeypatch)
        monkeypatch.setattr(check_prep, "BEHAVIORAL_BANK", tmp_path / "behavioral-bank.md")
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "3"])

        result = check_prep.main()
        assert result == 1, (
            f"Expected exit 1 with --module 3 and no behavioral bank; got {result}"
        )

    def test_module3_passes_with_all_artifacts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 3 must exit 0 when all M1, M2, and M3 artifacts are complete."""
        self._patch_m1_m2(tmp_path, monkeypatch)

        bank = tmp_path / "behavioral-bank.md"
        bank.write_text(make_behavioral_bank_complete(), encoding="utf-8")
        monkeypatch.setattr(check_prep, "BEHAVIORAL_BANK", bank)
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "3"])

        result = check_prep.main()
        assert result == 0, f"Expected exit 0 with --module 3 and all artifacts; got {result}"

    def test_module3_passes_without_systems_design_log(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 3 must exit 0 even when systems-design-log.md is absent (backward compat)."""
        self._patch_m1_m2(tmp_path, monkeypatch)

        bank = tmp_path / "behavioral-bank.md"
        bank.write_text(make_behavioral_bank_complete(), encoding="utf-8")
        monkeypatch.setattr(check_prep, "BEHAVIORAL_BANK", bank)
        # systems-design-log.md is absent; --module 3 must not require it.
        monkeypatch.setattr(check_prep, "SYSTEMS_DESIGN_LOG", tmp_path / "systems-design-log.md")
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "3"])

        result = check_prep.main()
        assert result == 0, (
            f"Expected exit 0 with --module 3 when systems-design-log.md is absent; got {result}"
        )


# ---------------------------------------------------------------------------
# Fixture builders: M5 systems design log
# ---------------------------------------------------------------------------


def make_systems_design_log_complete() -> str:
    """
    Return a systems-design-log.md that passes all M5 checks: one Design entry
    with all eight required fields filled in and free of placeholder text.
    """
    return """# Systems Design Log

## Design 1

**Prompt:** Walk me through the architecture of a production RAG system.

**Scope:** Internal knowledge base for a 10,000-employee company; 2M documents from SharePoint
and Confluence; p95 latency target of 3 seconds; soft accuracy bar; no strict compliance
requirement; peak load of 2,000 queries per hour from approximately 5% of employees. Priority
order: latency first, then retrieval quality, then cost.

**Design:** (1) Connector layer: delta-sync agents per source (SharePoint Graph API, Confluence
webhooks) -- required to keep the index fresh without full re-index on every update, which
would be cost-prohibitive at 2M documents. (2) Chunking and embedding service: structure-aware
chunking at 300-500 tokens with header prepended; multilingual embedding model -- justified
because the corpus contains project codenames and acronyms that require BM25 to retrieve
correctly. (3) Vector store: Pinecone with metadata filtering for access control -- chosen over
a relational DB because ANN search at 2M documents requires sub-100ms query latency that a
B-tree index cannot provide. (4) Hybrid retrieval: BM25 + vector search fused with RRF, then
cross-encoder rerank on top 50 -- the RRF fusion step is what raises retrieval hit rate from
70% to 90%+; pure vector search misses exact-match tokens in codenames. (5) Generation with
citation enforcement: if retrieval returns nothing, return "not found" rather than letting the
model improvise. (6) Eval and monitoring layer: offline golden set + 2% production sampling.

**Cost:** Routing: cheap embedding model (text-embedding-3-small at $0.02/1M tokens) for all
queries; frontier LLM (Claude Sonnet 4.6) only for generation. Caching: semantic cache on the
query embedding (cosine > 0.95) targeting 30% hit rate, which eliminates 30% of generation
calls entirely. Dominant cost driver: LLM generation tokens (output tokens cost 3x input
tokens). Named tradeoff: semantic caching reduces cost but adds 50ms per cache miss to check
the cache, which slightly degrades the p95 latency budget -- acceptable given the 3-second
target but would not be acceptable at a 500ms target.

**Latency:** P95 target: 3,000ms. Budget: permission resolution 50ms (cached with 5-min TTL),
embedding 100ms, vector search 100ms, reranking 150ms, LLM generation 1,500ms (streaming so
perceived latency is under 1s), overhead 100ms -- total 2,000ms with buffer. Named tradeoff:
the cross-encoder rerank step adds 150ms but is required to reach the 90%+ retrieval hit rate.
Removing it saves 150ms but drops retrieval quality to 70%, which increases the rate of
"not found" responses and forces users to reformulate queries -- a worse user outcome than the
extra latency.

**Reliability:** Primary failure modes: (1) LLM provider outage -- fallback to a second
provider (GPT-5.5) via circuit breaker after 3 failures; (2) retrieval returning nothing --
return "not found in our docs" rather than hallucinating; (3) data pipeline lag -- accept
up to 24h staleness for daily sync; add webhook-based invalidation for wikis as a named
upgrade. Degradation ladder: Full (hybrid retrieval + frontier LLM) to Reduced (BM25 only +
cheaper model) to Minimal (serve from cache only) to Offline (static FAQ page). Named
tradeoff: multi-provider failover increases latency on the fallback path by ~500ms due to cold
start; this is acceptable because the fallback only fires during an outage.

**Evaluation:** Offline: 200-case golden set drawn from real employee questions, stratified by
intent cluster; metrics: Precision@5, Recall@5, faithfulness (RAGAS), citation accuracy;
LLM-as-judge (Claude Haiku 4.5 with rubric) calibrated monthly against human-graded slice;
CI gate blocks deploy if any metric regresses more than 2pp. Online: sample 2% of production
traffic for judge scoring; trend query reformulation rate, citation click-through, and
thumbs-down rate; alert if reformulation rate rises 15% week-over-week (signals silent
retrieval degradation); monthly human review of 100 sampled traces to keep the judge calibrated.

**Audit verdict:** Pitfalls risked: Pitfall 1 (skipping the data pipeline) was explicitly
addressed by naming the connector layer and delta-sync strategy in the Design field. Pitfall 3
(ignoring the evaluation layer) was addressed by including eval in the Design field and
building out the Evaluation section. Pitfall 19 (ignoring hallucination risk) was addressed by
the citation enforcement and "not found" fallback. The one pitfall left thin: Pitfall 20
(security as an afterthought) -- access control is mentioned via metadata filtering but prompt
injection defense and audit logging are not named. The one change with five more minutes: add
explicit permission filtering at retrieval time (not post-retrieval application-code filtering,
which is the named wrong pattern from asdg-03 Pitfall 4) and add an audit log on all retrieval
queries.
"""


def make_systems_design_log_incomplete() -> str:
    """
    Return a systems-design-log.md that fails: one entry with placeholder text in all fields.
    """
    return """# Systems Design Log

## Design 1

**Prompt:** <fill in: the design question you chose>

**Scope:** <fill in: requirements, scale, constraints, priorities>

**Design:** <fill in: components with justifications>

**Cost:** <fill in: cost reasoning>

**Latency:** <fill in: latency reasoning>

**Reliability:** <fill in: reliability reasoning>

**Evaluation:** <fill in: evaluation reasoning>

**Audit verdict:** <fill in: weak-design red flags and one change>
"""


def make_systems_design_log_missing_field() -> str:
    """
    Return a systems-design-log.md that fails because the Latency field is absent.
    """
    return """# Systems Design Log

## Design 1

**Prompt:** Walk me through the architecture of a production RAG system.

**Scope:** 2M documents, p95 under 3s, 2K queries/hour peak, latency-first priority.

**Design:** Vector store, hybrid retrieval, generation with citation enforcement.

**Cost:** Semantic cache at 0.95 cosine threshold; dominant cost is output tokens.

**Reliability:** Multi-provider failover; not-found fallback; 24h staleness accepted.

**Evaluation:** 200-case golden set; 2% production sampling; reformulation rate alert.

**Audit verdict:** Pitfall 1 addressed via connector layer; Pitfall 19 via not-found fallback.
One change: add retrieval-time permission filtering explicitly.
"""


# ---------------------------------------------------------------------------
# Tests: systems-design-log.md (M5)
# ---------------------------------------------------------------------------


class TestSystemsDesignLog:
    def test_complete_log_passes(self, tmp_path: Path) -> None:
        """A fully completed systems design log must pass M5 validation."""
        log = tmp_path / "systems-design-log.md"
        log.write_text(make_systems_design_log_complete(), encoding="utf-8")

        passed, messages = check_prep.validate_systems_design_log(log)

        assert passed, f"Expected pass; got messages:\n" + "\n".join(messages)

    def test_incomplete_log_fails(self, tmp_path: Path) -> None:
        """A systems design log with placeholder text must fail."""
        log = tmp_path / "systems-design-log.md"
        log.write_text(make_systems_design_log_incomplete(), encoding="utf-8")

        passed, messages = check_prep.validate_systems_design_log(log)

        assert not passed, "Expected fail; validator incorrectly returned pass."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"

    def test_missing_log_fails(self, tmp_path: Path) -> None:
        """An absent systems design log must return fail with a not-started message."""
        missing = tmp_path / "systems-design-log.md"

        passed, messages = check_prep.validate_systems_design_log(missing)

        assert not passed
        combined = "\n".join(messages)
        assert "NOT STARTED" in combined or "does not exist" in combined

    def test_missing_field_fails(self, tmp_path: Path) -> None:
        """A log with a missing required field must fail."""
        log = tmp_path / "systems-design-log.md"
        log.write_text(make_systems_design_log_missing_field(), encoding="utf-8")

        passed, messages = check_prep.validate_systems_design_log(log)

        assert not passed, "Expected fail when a required field is absent."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"
        assert "Latency" in combined, (
            f"Expected the missing 'Latency' field to be named; got:\n{combined}"
        )

    def test_fewer_than_one_entry_fails(self, tmp_path: Path) -> None:
        """A file with no Design entries must fail."""
        log = tmp_path / "systems-design-log.md"
        log.write_text("# Systems Design Log\n\nNo entries here.\n", encoding="utf-8")

        passed, messages = check_prep.validate_systems_design_log(log)

        assert not passed, "Expected fail when no entries are present."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"


# ---------------------------------------------------------------------------
# Tests: --module 5 flag behavior (M5)
# ---------------------------------------------------------------------------


class TestModule5Flag:
    def _patch_all_through_m3(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Helper: patch all M1, M2, and M3 paths with complete content."""
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        signal_map = tmp_path / "signal-map.md"
        practice = tmp_path / "practice-log.md"
        audit = tmp_path / "audit-log.md"
        bank = tmp_path / "behavioral-bank.md"

        decomp.write_text(make_decomp_log_with_hard_cases(), encoding="utf-8")
        answers.write_text(make_answers_log_complete(), encoding="utf-8")
        signal_map.write_text(make_signal_map_complete(), encoding="utf-8")
        practice.write_text(make_practice_log_complete(), encoding="utf-8")
        audit.write_text(make_audit_log_complete(), encoding="utf-8")
        bank.write_text(make_behavioral_bank_complete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", signal_map)
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", practice)
        monkeypatch.setattr(check_prep, "AUDIT_LOG", audit)
        monkeypatch.setattr(check_prep, "BEHAVIORAL_BANK", bank)

    def test_module5_fails_without_systems_design_log(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 5 must exit 1 when systems-design-log.md is absent, even if M1+M2+M3 complete."""
        self._patch_all_through_m3(tmp_path, monkeypatch)
        monkeypatch.setattr(check_prep, "SYSTEMS_DESIGN_LOG", tmp_path / "systems-design-log.md")
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "5"])

        result = check_prep.main()
        assert result == 1, (
            f"Expected exit 1 with --module 5 and no systems-design-log; got {result}"
        )

    def test_module5_fails_when_m3_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 5 must exit 1 when M3 (behavioral-bank.md) is absent, even if M5 log present."""
        # Patch M1 and M2 complete, but leave behavioral-bank.md absent.
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        signal_map = tmp_path / "signal-map.md"
        practice = tmp_path / "practice-log.md"
        audit = tmp_path / "audit-log.md"
        sd_log = tmp_path / "systems-design-log.md"

        decomp.write_text(make_decomp_log_with_hard_cases(), encoding="utf-8")
        answers.write_text(make_answers_log_complete(), encoding="utf-8")
        signal_map.write_text(make_signal_map_complete(), encoding="utf-8")
        practice.write_text(make_practice_log_complete(), encoding="utf-8")
        audit.write_text(make_audit_log_complete(), encoding="utf-8")
        sd_log.write_text(make_systems_design_log_complete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", signal_map)
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", practice)
        monkeypatch.setattr(check_prep, "AUDIT_LOG", audit)
        monkeypatch.setattr(check_prep, "BEHAVIORAL_BANK", tmp_path / "behavioral-bank.md")
        monkeypatch.setattr(check_prep, "SYSTEMS_DESIGN_LOG", sd_log)
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "5"])

        result = check_prep.main()
        assert result == 1, (
            f"Expected exit 1 with --module 5 when behavioral-bank.md absent; got {result}"
        )

    def test_module5_passes_with_all_artifacts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 5 must exit 0 when all M1, M2, M3, and M5 artifacts are complete."""
        self._patch_all_through_m3(tmp_path, monkeypatch)

        sd_log = tmp_path / "systems-design-log.md"
        sd_log.write_text(make_systems_design_log_complete(), encoding="utf-8")
        monkeypatch.setattr(check_prep, "SYSTEMS_DESIGN_LOG", sd_log)
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "5"])

        result = check_prep.main()
        assert result == 0, f"Expected exit 0 with --module 5 and all artifacts; got {result}"


# ---------------------------------------------------------------------------
# Fixture builders: M6 portfolio narrative
# ---------------------------------------------------------------------------


def make_portfolio_narrative_complete() -> str:
    """
    Return a portfolio-narrative.md that passes all M6 checks: one Artifact entry
    with all seven required fields filled in and free of placeholder text.
    """
    return """# Portfolio Narrative

## Artifact 1

**Artifact:** The Production RAG Chatbot -- a citation-enforced, guardrailed retrieval-augmented
generation system for regulated verticals that screens input/output against hardcoded prohibitions,
monitors quality drift, and gates acceptance on retrieval precision and answer faithfulness.

**Overview:** The chatbot is a citation-and-refusal machine, not a chatbot with citations tacked
on. The differentiating decision is the relevance floor: if every retrieved chunk falls below the
minimum score threshold, the system refuses rather than grounding the answer in low-relevance
context. This decision directly prevents hallucinated citations -- the failure mode that collapses
trust in regulated deployments. The cost is that some valid questions receive "I don't have a
source for that" rather than an answer. The tradeoff is proven by the eval gate: inject a
low-relevance corpus and the gate fails; the refusal is tested, not assumed.

**Key decisions:** (1) The relevance floor (CRAG-style refusal). Decision: return no hits if
top-k all fall below min_score, forcing a refusal. Rejected: always returning top-k results.
Tradeoff: valid questions occasionally receive a refusal instead of an answer. Failure mode
guarded: hallucinated citations grounded in low-relevance chunks. (2) The guardrail with
hardcoded-prohibitions floor. Decision: split rules into un-lowerable hardcoded prohibitions
(prompt injection, PII exfiltration) and operator-tunable defaults (topical scope). Rejected:
making all guardrails operator-configurable. Tradeoff: the operator can tune scope but cannot
disable the security floor. Failure mode guarded: a misconfigured or pressured operator lowering
the security floor.

**Tradeoffs:** The two primary tradeoffs compound: the refusal floor trades answer coverage for
citation trustworthiness; the hardcoded guardrail floor trades operator flexibility for
security-floor stability. Both are worth the cost because the system targets regulated verticals
where a hallucinated citation or a PII leak is a compliance event, not a quality demerit. The
tradeoff changes at lower stakes: for an internal wiki with no compliance exposure, both floors
could be relaxed.

**Failure modes handled:** (1) Hallucinated citations grounded in low-relevance context: the
relevance floor structurally prevents this by refusing when no chunk clears the minimum score;
the refusal is tested by injecting a low-relevance corpus and confirming the gate rejects the
build. (2) Operator-induced security regression: the hardcoded-prohibitions floor cannot be
lowered by operator config; the guardrail tests inject a prohibited request and confirm the
system blocks it regardless of operator settings.

**Role tailoring:** **Applied-AI / product engineer:** The system's reliability in production
comes from the citation-and-refusal contract: the Chunk contract binds every downstream layer to
one shape, so a parser change cannot silently degrade citations, and the relevance floor means
users see an honest "no source" rather than a confident hallucination. The drift monitor samples
quality over a rolling window and flags SLO breaches before users report them. **ML-platform /
infra engineer:** The system is built on two protocol seams: the VectorIndex interface (add,
search) lets you swap in Azure AI Search with one constructor change, and the model seam lets
you swap any LLM backend behind the same generation interface. Both seams are tested: the
eval gate runs offline without a live model, so the CI gate is deterministic and cheap.

**Audit verdict:** Checked all six red flags. Passes: no generic lead (Overview opens with the
refusal mechanism, not "I built a RAG chatbot"); rejected alternatives are named (always-top-k
for the relevance floor, fully-configurable guardrails for the prohibitions floor); role tailoring
opens with different decisions (refusal + drift for applied-AI, seams + CI gate for platform).
Risks: the tradeoffs field states costs but does not name the break-even condition explicitly --
at what retrieval quality does the refusal floor become more costly than useful? One specific
change with two more minutes: add one sentence to Tradeoffs naming the metric that would prompt
revisiting the min_score threshold (e.g. if refusal rate exceeds 15% on production queries, the
floor is too aggressive).
"""


def make_portfolio_narrative_incomplete() -> str:
    """
    Return a portfolio-narrative.md that fails: one entry with placeholder text in all fields.
    """
    return """# Portfolio Narrative

## Artifact 1

**Artifact:** <fill in: the artifact you chose>

**Overview:** <fill in: sixty-second overview leading with the differentiator>

**Key decisions:** <fill in: load-bearing decisions>

**Tradeoffs:** <fill in: tradeoffs accepted>

**Failure modes handled:** <fill in: failure modes guarded>

**Role tailoring:** <fill in: two role-tailored framings>

**Audit verdict:** <fill in: weak-walkthrough red flags and one change>
"""


def make_portfolio_narrative_missing_field() -> str:
    """
    Return a portfolio-narrative.md that fails because the Role tailoring field is absent.
    """
    return """# Portfolio Narrative

## Artifact 1

**Artifact:** The Production RAG Chatbot -- a citation-enforced retrieval system.

**Overview:** The chatbot is a citation-and-refusal machine. The differentiator is the relevance
floor: if every retrieved chunk falls below the minimum score, the system refuses rather than
fabricating from low-relevance context. This prevents hallucinated citations.

**Key decisions:** The relevance floor. Decision: refuse when top-k all fall below min_score.
Rejected: always returning top-k. Tradeoff: valid questions occasionally get a refusal. Failure
mode guarded: hallucinated citations from low-relevance chunks.

**Tradeoffs:** The refusal floor trades answer coverage for citation trustworthiness. Worth it
in regulated verticals where a hallucinated citation is a compliance event.

**Failure modes handled:** Hallucinated citations from low-relevance context: structurally
prevented by the relevance floor. Operator-induced security regression: prevented by the
hardcoded-prohibitions floor that operator config cannot lower.

**Audit verdict:** Passes generic-lead check (opens with refusal mechanism). Risks: role
tailoring not present. One change: add two role-tailored framings distinguishing applied-AI
emphasis (refusal + drift) from platform emphasis (seams + CI gate).
"""


# ---------------------------------------------------------------------------
# Tests: portfolio-narrative.md (M6)
# ---------------------------------------------------------------------------


class TestPortfolioNarrative:
    def test_complete_narrative_passes(self, tmp_path: Path) -> None:
        """A fully completed portfolio narrative must pass M6 validation."""
        pn = tmp_path / "portfolio-narrative.md"
        pn.write_text(make_portfolio_narrative_complete(), encoding="utf-8")

        passed, messages = check_prep.validate_portfolio_narrative(pn)

        assert passed, f"Expected pass; got messages:\n" + "\n".join(messages)

    def test_incomplete_narrative_fails(self, tmp_path: Path) -> None:
        """A portfolio narrative with placeholder text must fail."""
        pn = tmp_path / "portfolio-narrative.md"
        pn.write_text(make_portfolio_narrative_incomplete(), encoding="utf-8")

        passed, messages = check_prep.validate_portfolio_narrative(pn)

        assert not passed, "Expected fail; validator incorrectly returned pass."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"

    def test_missing_narrative_fails(self, tmp_path: Path) -> None:
        """An absent portfolio narrative must return fail with a not-started message."""
        missing = tmp_path / "portfolio-narrative.md"

        passed, messages = check_prep.validate_portfolio_narrative(missing)

        assert not passed
        combined = "\n".join(messages)
        assert "NOT STARTED" in combined or "does not exist" in combined

    def test_missing_field_fails(self, tmp_path: Path) -> None:
        """A portfolio narrative with a missing required field must fail."""
        pn = tmp_path / "portfolio-narrative.md"
        pn.write_text(make_portfolio_narrative_missing_field(), encoding="utf-8")

        passed, messages = check_prep.validate_portfolio_narrative(pn)

        assert not passed, "Expected fail when a required field is absent."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"
        assert "Role tailoring" in combined, (
            f"Expected the missing 'Role tailoring' field to be named; got:\n{combined}"
        )

    def test_zero_entries_fails(self, tmp_path: Path) -> None:
        """A file with no Artifact entries must fail."""
        pn = tmp_path / "portfolio-narrative.md"
        pn.write_text("# Portfolio Narrative\n\nNo entries here.\n", encoding="utf-8")

        passed, messages = check_prep.validate_portfolio_narrative(pn)

        assert not passed, "Expected fail when no entries are present."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"


# ---------------------------------------------------------------------------
# Tests: --module 6 flag behavior (M6)
# ---------------------------------------------------------------------------


class TestModule6Flag:
    def _patch_all_through_m5(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Helper: patch all M1, M2, M3, and M5 paths with complete content."""
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        signal_map = tmp_path / "signal-map.md"
        practice = tmp_path / "practice-log.md"
        audit = tmp_path / "audit-log.md"
        bank = tmp_path / "behavioral-bank.md"
        sd_log = tmp_path / "systems-design-log.md"

        decomp.write_text(make_decomp_log_with_hard_cases(), encoding="utf-8")
        answers.write_text(make_answers_log_complete(), encoding="utf-8")
        signal_map.write_text(make_signal_map_complete(), encoding="utf-8")
        practice.write_text(make_practice_log_complete(), encoding="utf-8")
        audit.write_text(make_audit_log_complete(), encoding="utf-8")
        bank.write_text(make_behavioral_bank_complete(), encoding="utf-8")
        sd_log.write_text(make_systems_design_log_complete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", signal_map)
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", practice)
        monkeypatch.setattr(check_prep, "AUDIT_LOG", audit)
        monkeypatch.setattr(check_prep, "BEHAVIORAL_BANK", bank)
        monkeypatch.setattr(check_prep, "SYSTEMS_DESIGN_LOG", sd_log)

    def test_module6_fails_without_portfolio_narrative(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 6 must exit 1 when portfolio-narrative.md is absent, even if M1-M5 complete."""
        self._patch_all_through_m5(tmp_path, monkeypatch)
        monkeypatch.setattr(
            check_prep, "PORTFOLIO_NARRATIVE", tmp_path / "portfolio-narrative.md"
        )
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "6"])

        result = check_prep.main()
        assert result == 1, (
            f"Expected exit 1 with --module 6 and no portfolio-narrative; got {result}"
        )

    def test_module6_fails_when_m5_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 6 must exit 1 when M5 (systems-design-log.md) is absent, even if portfolio present."""
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        signal_map = tmp_path / "signal-map.md"
        practice = tmp_path / "practice-log.md"
        audit = tmp_path / "audit-log.md"
        bank = tmp_path / "behavioral-bank.md"
        pn = tmp_path / "portfolio-narrative.md"

        decomp.write_text(make_decomp_log_with_hard_cases(), encoding="utf-8")
        answers.write_text(make_answers_log_complete(), encoding="utf-8")
        signal_map.write_text(make_signal_map_complete(), encoding="utf-8")
        practice.write_text(make_practice_log_complete(), encoding="utf-8")
        audit.write_text(make_audit_log_complete(), encoding="utf-8")
        bank.write_text(make_behavioral_bank_complete(), encoding="utf-8")
        pn.write_text(make_portfolio_narrative_complete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", signal_map)
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", practice)
        monkeypatch.setattr(check_prep, "AUDIT_LOG", audit)
        monkeypatch.setattr(check_prep, "BEHAVIORAL_BANK", bank)
        monkeypatch.setattr(check_prep, "SYSTEMS_DESIGN_LOG", tmp_path / "systems-design-log.md")
        monkeypatch.setattr(check_prep, "PORTFOLIO_NARRATIVE", pn)
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "6"])

        result = check_prep.main()
        assert result == 1, (
            f"Expected exit 1 with --module 6 when systems-design-log.md absent; got {result}"
        )

    def test_module6_passes_with_all_artifacts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 6 must exit 0 when all M1, M2, M3, M5, and M6 artifacts are complete."""
        self._patch_all_through_m5(tmp_path, monkeypatch)

        pn = tmp_path / "portfolio-narrative.md"
        pn.write_text(make_portfolio_narrative_complete(), encoding="utf-8")
        monkeypatch.setattr(check_prep, "PORTFOLIO_NARRATIVE", pn)
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "6"])

        result = check_prep.main()
        assert result == 0, f"Expected exit 0 with --module 6 and all artifacts; got {result}"

    def test_module5_passes_without_portfolio_narrative(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 5 must exit 0 even when portfolio-narrative.md is absent (backward compat)."""
        self._patch_all_through_m5(tmp_path, monkeypatch)
        # portfolio-narrative.md is absent; --module 5 must not require it.
        monkeypatch.setattr(
            check_prep, "PORTFOLIO_NARRATIVE", tmp_path / "portfolio-narrative.md"
        )
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "5"])

        result = check_prep.main()
        assert result == 0, (
            f"Expected exit 0 with --module 5 when portfolio-narrative.md is absent; got {result}"
        )


# ---------------------------------------------------------------------------
# Fixture builders: M7 deliberate practice log
# ---------------------------------------------------------------------------


def _make_dp_entry(n: int, category: str) -> str:
    """Return one complete ### DP<n> entry with all seven required fields filled."""
    return f"""### DP{n}

**Question:** Tell me about a time you pushed a technical decision that turned out to be wrong. What did you do when you realized it?

**Signal category:** {category}

**Decompose:** strong

**Signal:** strong

**Construct:** strong

**Stress-test:** strong

**Verdict:** Decompose and Signal were both strong; the question maps cleanly to ownership. Construct named a concrete metric (cost ran four times the projection) and a structural lesson (kill criteria on own proposals). No gaps to drill from this rep; next rep should be in a different category.
"""


def make_deliberate_practice_complete() -> str:
    """
    Return a deliberate-practice.md that passes all M7 checks: five DP entries
    covering all five signal categories, all fields filled, valid step scores.
    """
    categories = ["ownership", "conflict", "failure", "influence", "systems-design"]
    entries = [_make_dp_entry(i + 1, cat) for i, cat in enumerate(categories)]
    return (
        "# Deliberate Practice Log\n\n"
        + "\n".join(entries)
    )


def make_deliberate_practice_incomplete() -> str:
    """
    Return a deliberate-practice.md that fails: only two entries with placeholder text.
    """
    return """# Deliberate Practice Log

### DP1

**Question:** <fill in: the interview question you practiced on>

**Signal category:** <fill in: one of ownership, conflict, failure, influence, systems-design>

**Decompose:** <fill in: strong | partial | weak>

**Signal:** <fill in: strong | partial | weak>

**Construct:** <fill in: strong | partial | weak>

**Stress-test:** <fill in: strong | partial | weak>

**Verdict:** <fill in: what the rep revealed and what to drill next>

### DP2

**Question:** Walk me through a production system you designed.

**Signal category:** systems-design

**Decompose:** partial

**Signal:** strong

**Construct:** partial

**Stress-test:** weak

**Verdict:** Construct was thin: named the components but not the load-bearing decision or a concrete metric. Stress-test was weak: did not name what a weak candidate could not replicate. Drill next: Construct step for systems-design questions -- lead with the key tradeoff, not the component list.
"""


def make_deliberate_practice_missing_field() -> str:
    """
    Return a deliberate-practice.md that fails because the Verdict field is absent
    from one entry.
    """
    categories = ["ownership", "conflict", "failure", "influence", "systems-design"]
    entries = []
    for i, cat in enumerate(categories):
        if i == 2:
            # Entry 3 is missing the Verdict field.
            entries.append(f"""### DP{i + 1}

**Question:** Tell me about a project that failed.

**Signal category:** {cat}

**Decompose:** partial

**Signal:** partial

**Construct:** weak

**Stress-test:** weak
""")
        else:
            entries.append(_make_dp_entry(i + 1, cat))
    return "# Deliberate Practice Log\n\n" + "\n".join(entries)


def make_deliberate_practice_missing_category() -> str:
    """
    Return a deliberate-practice.md that fails because only four of five categories
    appear (systems-design is missing; ownership appears twice).
    """
    entries = [
        _make_dp_entry(1, "ownership"),
        _make_dp_entry(2, "conflict"),
        _make_dp_entry(3, "failure"),
        _make_dp_entry(4, "influence"),
        _make_dp_entry(5, "ownership"),  # duplicate instead of systems-design
    ]
    return "# Deliberate Practice Log\n\n" + "\n".join(entries)


def make_deliberate_practice_invalid_step_score() -> str:
    """
    Return a deliberate-practice.md that fails because one step score is invalid
    ('great' is not a valid score value).
    """
    categories = ["ownership", "conflict", "failure", "influence", "systems-design"]
    entries = []
    for i, cat in enumerate(categories):
        if i == 0:
            entries.append(f"""### DP{i + 1}

**Question:** Tell me about a time you owned a wrong call.

**Signal category:** {cat}

**Decompose:** great

**Signal:** strong

**Construct:** strong

**Stress-test:** strong

**Verdict:** Strong across Signal, Construct, and Stress-test. Decompose was solid too.
""")
        else:
            entries.append(_make_dp_entry(i + 1, cat))
    return "# Deliberate Practice Log\n\n" + "\n".join(entries)


def make_deliberate_practice_invalid_category() -> str:
    """
    Return a deliberate-practice.md that fails because one entry has an invalid
    signal category value ('judgment' is not in the allowed set).
    """
    categories = ["ownership", "conflict", "failure", "influence", "systems-design"]
    entries = []
    for i, cat in enumerate(categories):
        if i == 1:
            entries.append(f"""### DP{i + 1}

**Question:** Tell me about a time you had to make a decision with incomplete information.

**Signal category:** judgment

**Decompose:** strong

**Signal:** partial

**Construct:** partial

**Stress-test:** partial

**Verdict:** Signal was partial: I named the category but not the exact hypothesis. Next rep: write the hypothesis in the form "The interviewer is trying to determine whether..."
""")
        else:
            entries.append(_make_dp_entry(i + 1, cat))
    return "# Deliberate Practice Log\n\n" + "\n".join(entries)


def make_deliberate_practice_fewer_than_five() -> str:
    """
    Return a deliberate-practice.md that fails because it has only three entries,
    even though the entries themselves are otherwise valid.
    """
    categories = ["ownership", "conflict", "failure"]
    entries = [_make_dp_entry(i + 1, cat) for i, cat in enumerate(categories)]
    return "# Deliberate Practice Log\n\n" + "\n".join(entries)


# ---------------------------------------------------------------------------
# Tests: deliberate-practice.md (M7)
# ---------------------------------------------------------------------------


class TestDeliberatePractice:
    def test_complete_log_passes(self, tmp_path: Path) -> None:
        """A fully completed deliberate practice log must pass M7 validation."""
        dp = tmp_path / "deliberate-practice.md"
        dp.write_text(make_deliberate_practice_complete(), encoding="utf-8")

        passed, messages = check_prep.validate_deliberate_practice(dp)

        assert passed, f"Expected pass; got messages:\n" + "\n".join(messages)

    def test_missing_log_fails(self, tmp_path: Path) -> None:
        """An absent deliberate practice log must return fail with a not-started message."""
        missing = tmp_path / "deliberate-practice.md"

        passed, messages = check_prep.validate_deliberate_practice(missing)

        assert not passed
        combined = "\n".join(messages)
        assert "NOT STARTED" in combined or "does not exist" in combined

    def test_missing_required_field_fails(self, tmp_path: Path) -> None:
        """A log with a missing required field in one entry must fail."""
        dp = tmp_path / "deliberate-practice.md"
        dp.write_text(make_deliberate_practice_missing_field(), encoding="utf-8")

        passed, messages = check_prep.validate_deliberate_practice(dp)

        assert not passed, "Expected fail when a required field is absent."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"
        assert "Verdict" in combined, (
            f"Expected the missing 'Verdict' field to be named; got:\n{combined}"
        )

    def test_placeholder_fails(self, tmp_path: Path) -> None:
        """A log with placeholder text in fields must fail."""
        dp = tmp_path / "deliberate-practice.md"
        dp.write_text(make_deliberate_practice_incomplete(), encoding="utf-8")

        passed, messages = check_prep.validate_deliberate_practice(dp)

        assert not passed, "Expected fail; validator incorrectly returned pass."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"

    def test_fewer_than_five_entries_fails(self, tmp_path: Path) -> None:
        """A log with only three entries must fail the minimum count check."""
        dp = tmp_path / "deliberate-practice.md"
        dp.write_text(make_deliberate_practice_fewer_than_five(), encoding="utf-8")

        passed, messages = check_prep.validate_deliberate_practice(dp)

        assert not passed, "Expected fail when fewer than five entries present."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"

    def test_missing_category_fails(self, tmp_path: Path) -> None:
        """A log with five entries but only four categories must fail."""
        dp = tmp_path / "deliberate-practice.md"
        dp.write_text(make_deliberate_practice_missing_category(), encoding="utf-8")

        passed, messages = check_prep.validate_deliberate_practice(dp)

        assert not passed, "Expected fail when a signal category is missing."
        combined = "\n".join(messages)
        assert "systems-design" in combined.lower(), (
            f"Expected 'systems-design' named in failure messages; got:\n{combined}"
        )

    def test_invalid_step_score_fails(self, tmp_path: Path) -> None:
        """A log with an invalid step score value must fail."""
        dp = tmp_path / "deliberate-practice.md"
        dp.write_text(make_deliberate_practice_invalid_step_score(), encoding="utf-8")

        passed, messages = check_prep.validate_deliberate_practice(dp)

        assert not passed, "Expected fail when step score is not strong/partial/weak."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"
        assert "great" in combined.lower(), (
            f"Expected invalid score 'great' named in failure messages; got:\n{combined}"
        )

    def test_invalid_signal_category_fails(self, tmp_path: Path) -> None:
        """A log with an invalid signal category value must fail."""
        dp = tmp_path / "deliberate-practice.md"
        dp.write_text(make_deliberate_practice_invalid_category(), encoding="utf-8")

        passed, messages = check_prep.validate_deliberate_practice(dp)

        assert not passed, "Expected fail when signal category is not in the allowed set."
        combined = "\n".join(messages)
        assert "FAIL" in combined, f"Expected FAIL in messages; got:\n{combined}"
        assert "judgment" in combined.lower(), (
            f"Expected invalid category 'judgment' named in failure messages; got:\n{combined}"
        )


# ---------------------------------------------------------------------------
# Tests: --module 7 flag behavior (M7)
# ---------------------------------------------------------------------------


class TestModule7Flag:
    def _patch_all_through_m6(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Helper: patch all M1, M2, M3, M5, and M6 paths with complete content."""
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        signal_map = tmp_path / "signal-map.md"
        practice = tmp_path / "practice-log.md"
        audit = tmp_path / "audit-log.md"
        bank = tmp_path / "behavioral-bank.md"
        sd_log = tmp_path / "systems-design-log.md"
        pn = tmp_path / "portfolio-narrative.md"

        decomp.write_text(make_decomp_log_with_hard_cases(), encoding="utf-8")
        answers.write_text(make_answers_log_complete(), encoding="utf-8")
        signal_map.write_text(make_signal_map_complete(), encoding="utf-8")
        practice.write_text(make_practice_log_complete(), encoding="utf-8")
        audit.write_text(make_audit_log_complete(), encoding="utf-8")
        bank.write_text(make_behavioral_bank_complete(), encoding="utf-8")
        sd_log.write_text(make_systems_design_log_complete(), encoding="utf-8")
        pn.write_text(make_portfolio_narrative_complete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", signal_map)
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", practice)
        monkeypatch.setattr(check_prep, "AUDIT_LOG", audit)
        monkeypatch.setattr(check_prep, "BEHAVIORAL_BANK", bank)
        monkeypatch.setattr(check_prep, "SYSTEMS_DESIGN_LOG", sd_log)
        monkeypatch.setattr(check_prep, "PORTFOLIO_NARRATIVE", pn)

    def test_module7_fails_without_deliberate_practice(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 7 must exit 1 when deliberate-practice.md is absent, even if M1-M6 complete."""
        self._patch_all_through_m6(tmp_path, monkeypatch)
        monkeypatch.setattr(
            check_prep, "DELIBERATE_PRACTICE", tmp_path / "deliberate-practice.md"
        )
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "7"])

        result = check_prep.main()
        assert result == 1, (
            f"Expected exit 1 with --module 7 and no deliberate-practice; got {result}"
        )

    def test_module7_fails_when_m6_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 7 must exit 1 when M6 (portfolio-narrative.md) is absent."""
        decomp = tmp_path / "decomposition-log.md"
        answers = tmp_path / "answers-log.md"
        signal_map = tmp_path / "signal-map.md"
        practice = tmp_path / "practice-log.md"
        audit = tmp_path / "audit-log.md"
        bank = tmp_path / "behavioral-bank.md"
        sd_log = tmp_path / "systems-design-log.md"
        dp = tmp_path / "deliberate-practice.md"

        decomp.write_text(make_decomp_log_with_hard_cases(), encoding="utf-8")
        answers.write_text(make_answers_log_complete(), encoding="utf-8")
        signal_map.write_text(make_signal_map_complete(), encoding="utf-8")
        practice.write_text(make_practice_log_complete(), encoding="utf-8")
        audit.write_text(make_audit_log_complete(), encoding="utf-8")
        bank.write_text(make_behavioral_bank_complete(), encoding="utf-8")
        sd_log.write_text(make_systems_design_log_complete(), encoding="utf-8")
        dp.write_text(make_deliberate_practice_complete(), encoding="utf-8")

        monkeypatch.setattr(check_prep, "DECOMP_LOG", decomp)
        monkeypatch.setattr(check_prep, "ANSWERS_LOG", answers)
        monkeypatch.setattr(check_prep, "SIGNAL_MAP", signal_map)
        monkeypatch.setattr(check_prep, "PRACTICE_LOG", practice)
        monkeypatch.setattr(check_prep, "AUDIT_LOG", audit)
        monkeypatch.setattr(check_prep, "BEHAVIORAL_BANK", bank)
        monkeypatch.setattr(check_prep, "SYSTEMS_DESIGN_LOG", sd_log)
        monkeypatch.setattr(
            check_prep, "PORTFOLIO_NARRATIVE", tmp_path / "portfolio-narrative.md"
        )
        monkeypatch.setattr(check_prep, "DELIBERATE_PRACTICE", dp)
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "7"])

        result = check_prep.main()
        assert result == 1, (
            f"Expected exit 1 with --module 7 when portfolio-narrative.md absent; got {result}"
        )

    def test_module7_passes_with_all_artifacts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 7 must exit 0 when all M1, M2, M3, M5, M6, and M7 artifacts are complete."""
        self._patch_all_through_m6(tmp_path, monkeypatch)

        dp = tmp_path / "deliberate-practice.md"
        dp.write_text(make_deliberate_practice_complete(), encoding="utf-8")
        monkeypatch.setattr(check_prep, "DELIBERATE_PRACTICE", dp)
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "7"])

        result = check_prep.main()
        assert result == 0, f"Expected exit 0 with --module 7 and all artifacts; got {result}"

    def test_module6_passes_without_deliberate_practice(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--module 6 must exit 0 even when deliberate-practice.md is absent (backward compat)."""
        self._patch_all_through_m6(tmp_path, monkeypatch)
        # deliberate-practice.md is absent; --module 6 must not require it.
        monkeypatch.setattr(
            check_prep, "DELIBERATE_PRACTICE", tmp_path / "deliberate-practice.md"
        )
        monkeypatch.setattr(sys, "argv", ["check_prep.py", "--module", "6"])

        result = check_prep.main()
        assert result == 0, (
            f"Expected exit 0 with --module 6 when deliberate-practice.md is absent; got {result}"
        )
