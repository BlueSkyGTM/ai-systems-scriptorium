"""The acceptance rubric — the strong-project bar applied to a SYSTEM.

Module 6 graded a single agent: does it run, is it eval-gated, does it have
operator surfaces and tests? The exam grades a *system the fleet ships* against the
same hireability bar, now at the scale of governed infrastructure. Seven criteria,
each a pass/fail check against the captured ``ExamRun`` — and each one MATCHES,
clause for clause, the rubric written in the guide ``03-operating-and-grading.md``.
If you change a criterion here, change it there. The guide and this file are one
rubric in two forms; the exam is graded by code so the grade is not a matter of
opinion.

    R1  RUNS            — the fleet shipped the system end to end (status merged).
    R2  EVAL-GATED      — the merge passed the tester ACCEPT + reviewer gate.
    R3  AUDITED         — the audit answers all four clauses (which/authority/task/evidence).
    R4  BUDGET-BOUNDED  — team spend within the team cap; no per-agent breach.
    R5  HITL-GOVERNED   — the merge was human-approved through the inbox by id (no auto-merge).
    R6  PROBLEM-FRAMED  — the spec names the track, the reference architecture, and the problem.
    R7  TESTED+VERSIONED— the spec declares acceptance criteria and a version.

A deficient run fails the criterion it offends — an unapproved merge fails R5, an
incomplete audit fails R3, a blown budget fails R4 — so the rubric is a real gate,
not a rubber stamp.
"""

from __future__ import annotations

from dataclasses import dataclass


# The seven criteria, in order. (id, one-line statement) — the SAME seven the
# guide's rubric table lists. This tuple is the single source of truth for both.
CRITERIA = (
    ("R1", "RUNS: the fleet shipped the system end to end (merge committed)"),
    ("R2", "EVAL-GATED: the merge passed the tester ACCEPT and the reviewer gate"),
    ("R3", "AUDITED: the cross-agent audit answers all four accountability clauses"),
    ("R4", "BUDGET-BOUNDED: team spend stayed within the team cap; no per-agent breach"),
    ("R5", "HITL-GOVERNED: the merge was human-approved through the inbox by id (no auto-merge)"),
    ("R6", "PROBLEM-FRAMED: the spec names the track, the reference architecture, and the problem"),
    ("R7", "TESTED+VERSIONED: the spec declares acceptance criteria and a version"),
)


@dataclass
class CriterionResult:
    rid: str
    statement: str
    passed: bool
    detail: str


@dataclass
class RubricReport:
    """The graded result: pass/fail per criterion, plus the overall verdict."""

    results: list
    passed: bool

    def failed(self) -> list:
        return [r for r in self.results if not r.passed]

    def as_lines(self) -> list:
        lines = []
        for r in self.results:
            mark = "PASS" if r.passed else "FAIL"
            lines.append(f"  [{mark}] {r.rid}  {r.statement}")
            if not r.passed:
                lines.append(f"         -> {r.detail}")
        lines.append("")
        lines.append(f"  VERDICT: {'PASS' if self.passed else 'FAIL'} "
                     f"({sum(r.passed for r in self.results)}/{len(self.results)} criteria)")
        return lines


def grade(exam) -> RubricReport:
    """Grade a captured ``ExamRun`` against the seven criteria. Returns a report
    whose ``passed`` is True only when every criterion passes.

    ``exam`` is the ``run_exam.ExamRun`` — graded by reading its captured fields,
    never by re-running the fleet. The grade is reproducible from the record."""
    spec = exam.spec
    budget = exam.budget or {}
    clauses = exam.audit_clauses or {}

    # R1 RUNS — the produced system actually shipped: the merge committed.
    r1 = exam.status == "merged"
    r1_detail = f"status={exam.status!r} ({exam.detail})"

    # R2 EVAL-GATED — reaching a committed merge means the tester ACCEPTed and the
    # reviewer approved: the orchestrator only proposes a merge after both gates,
    # and a merge cannot commit without the proposal. A blocked run failed a gate.
    r2 = exam.status == "merged" and exam.merge_inbox_id is not None
    r2_detail = (f"no merge proposal reached — a gate (tester/reviewer) blocked the run: {exam.detail}"
                 if not r2 else "tester ACCEPT + reviewer gate cleared before the merge proposal")

    # R3 AUDITED — the four accountability clauses are all answered for the run.
    r3 = bool(clauses.get("complete"))
    r3_detail = ("audit incomplete — a clause (which/authority/task/evidence) is empty"
                 if not r3 else
                 f"{len(clauses.get('evidenced_by_what', []))} evidence records across "
                 f"{len(set(clauses.get('which_agents', [])))} agents")

    # R4 BUDGET-BOUNDED — team spend within the team cap (and, since the run did
    # not breach, no per-agent cap fired). A budget_breach status fails outright.
    spent = float(budget.get("team_spent_usd", 0.0))
    cap = float(budget.get("team_daily_usd", 0.0)) if budget.get("team_daily_usd") is not None else 0.0
    r4 = (exam.status != "budget_breach") and (cap > 0) and (spent <= cap)
    r4_detail = (f"budget breach: {exam.detail}" if exam.status == "budget_breach"
                 else f"${spent} / ${cap} team cap")

    # R5 HITL-GOVERNED — the merge was approved by a named human through the inbox.
    r5 = bool(exam.merge_approved_by) and exam.merge_inbox_id is not None
    r5_detail = ("no human approval on record — the merge was not committed through the inbox"
                 if not r5 else f"approved by {exam.merge_approved_by} via {exam.merge_inbox_id}")

    # R6 PROBLEM-FRAMED — the spec frames the problem (track + ref arch + one-liner).
    r6 = spec.has_framing()
    r6_detail = ("spec is missing the track, the reference architecture, or the business problem"
                 if not r6 else f"{spec.track} / {spec.reference_architecture}")

    # R7 TESTED+VERSIONED — the spec declares acceptance criteria and a version.
    r7 = spec.declares_tests() and spec.is_versioned()
    r7_detail = ("spec is missing acceptance criteria or a version"
                 if not r7 else
                 f"{len(spec.acceptance_criteria)} acceptance criteria, v{spec.version}")

    flags = {"R1": (r1, r1_detail), "R2": (r2, r2_detail), "R3": (r3, r3_detail),
             "R4": (r4, r4_detail), "R5": (r5, r5_detail), "R6": (r6, r6_detail),
             "R7": (r7, r7_detail)}

    results = [
        CriterionResult(rid, statement, flags[rid][0], flags[rid][1])
        for rid, statement in CRITERIA
    ]
    return RubricReport(results=results, passed=all(r.passed for r in results))
