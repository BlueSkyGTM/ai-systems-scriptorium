"""Verification gate — an agent does not mark its own work done.

Reused unchanged from the M6 coding agent. Deterministic code — no model, no
judgment — that runs the project's tests in the sandbox and returns one verdict.
Default REJECT: it accepts only on a clean test run. Failing tests, a timeout, an
import error all reject.

This is the load-bearing interface of the whole fleet: it is *why the reviewer
can trust the coder*. The coder hands over a verdict from running the tests, not
a promise that it fixed the bug. The tester node runs this gate; the reviewer
reads its verdict. One source of truth — the loop, the operator, and CI all read
the same ``Verdict``.
"""

from __future__ import annotations

from dataclasses import dataclass

import sandbox


@dataclass
class Verdict:
    accepted: bool
    detail: str
    exit_code: int

    @property
    def label(self) -> str:
        return "ACCEPT" if self.accepted else "REJECT"


def verify(project_dir: str, timeout_s: float = 30.0) -> Verdict:
    """Run the project's tests and return ACCEPT only on a clean pass.

    Default REJECT: every path that is not a zero-exit test run is a rejection,
    including timeouts and collection errors.
    """
    result = sandbox.run_pytest(project_dir, timeout_s=timeout_s)
    if result.timed_out:
        return Verdict(False, "tests timed out", result.exit_code)
    if result.exit_code != 0:
        tail = (result.stdout + result.stderr).strip().splitlines()
        last = tail[-1] if tail else "no output"
        return Verdict(False, f"tests failed (exit {result.exit_code}): {last}", result.exit_code)
    return Verdict(True, "all tests passed", 0)
