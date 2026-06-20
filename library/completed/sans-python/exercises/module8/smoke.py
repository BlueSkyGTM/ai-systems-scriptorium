"""Final-exam smoke run — point the REAL M7 fleet at the sample spec, then grade.

The exam end to end, offline, on the standard library alone:

    1. load the sample task spec (agentic-system / #07 autonomous coding agent);
    2. point the SHIPPED M7 governed fleet at it (imported, not rebuilt);
    3. the fleet ships a version of the system under the operator console — plan,
       parallel coders (the M6 loop), tester ACCEPT, reviewer gate, merge PROPOSED
       to the HITL inbox, human approval, merge committed;
    4. run the acceptance rubric over the captured run and print the graded result.

No network, no API key, no Docker — the M7 fleet's smoke path is stdlib-only on a
deterministic mock, and this reuses it. This is the exam's BUILD->TEST gate:

    python smoke.py

Exit 0 only when the fleet shipped the system AND the rubric passes the honest run.
"""

from __future__ import annotations

import os
import sys

from rubric import grade
from run_exam import run_exam

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "sample_spec.md")


def main() -> int:
    print("Final Systems Engineering Exam — smoke run")
    print("=" * 68)
    print("Pointing the SHIPPED M7 governed fleet at the sample spec (offline mock).")
    print("-" * 68)

    # 1-3) The real fleet ships a version of the system under the operator console.
    exam = run_exam(SAMPLE)

    print(f"track            : {exam.spec.track}")
    print(f"reference arch   : {exam.spec.reference_architecture}")
    print(f"feature shipped  : {exam.spec.feature!r}")
    print(f"plan (slices)    : {[s.get('slice') for s in exam.plan]}")
    print(f"fleet status     : {exam.status}  ->  {exam.detail}")
    print(f"merge approved by: {exam.merge_approved_by}  (via {exam.merge_inbox_id})")
    print(f"audit complete   : {exam.audit_clauses.get('complete')}  "
          f"({len(exam.audit_clauses.get('evidenced_by_what', []))} evidence records, "
          f"{len(set(exam.audit_clauses.get('which_agents', [])))} agents)")
    print(f"fleet budget     : ${exam.budget.get('team_spent_usd')} / "
          f"${exam.budget.get('team_daily_usd')} team cap")
    print("-" * 68)

    # 4) Grade the produced run against the acceptance rubric.
    print("ACCEPTANCE RUBRIC — the strong-project bar applied to a system:")
    report = grade(exam)
    for line in report.as_lines():
        print(line)

    shipped = exam.status == "merged"
    ok = shipped and report.passed
    print("=" * 68)
    print(f"EXAM: the M7 fleet {'SHIPPED' if shipped else 'did NOT ship'} the system; "
          f"the rubric {'PASSED' if report.passed else 'FAILED'} the run.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
