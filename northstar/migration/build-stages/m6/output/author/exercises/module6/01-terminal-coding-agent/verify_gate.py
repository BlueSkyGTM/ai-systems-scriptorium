"""Verification gate — the agent does not mark its own work done.

An agent that decides it is finished is not done; it is optimistic. The verify
gate is deterministic code — no model, no judgment — that runs the fixture's
tests in the sandbox and returns one verdict. The default is REJECT: the gate
accepts only on a clean test run. Anything else — failing tests, a timeout, an
import error — is a rejection.

This is the M3 workbench ``verify_agent.py`` idea, narrowed to "did the tests
pass after the edit". CI reads the same verdict; the operator reads the same
verdict; the loop reads the same verdict. One source of truth.
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
    """Run the fixture's tests and return ACCEPT only on a clean pass.

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
