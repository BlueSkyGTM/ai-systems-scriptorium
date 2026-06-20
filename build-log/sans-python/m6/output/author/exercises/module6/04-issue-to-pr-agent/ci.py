"""Mock CI = run the repo's real tests locally. The verifier must reproduce the gate.

The lesson from M4 lesson 11 is exact: a verifier that does not run *what CI runs*
issues false approvals. So this "mock" CI is not a stub that returns APPROVE — it
shells out to the fixture repo's own test command and reads the exit code. Green
exit -> APPROVE. Anything else -> REJECT. The default, on any doubt, is REJECT.

In production this stage waits on the real GitHub Actions run for the head SHA.
The seam is the same: an independent check, keyed to the commit, that the agent
cannot fake. Here the check is `python -m pytest` (or a configured command) run
in the repo directory; there it is the Actions workflow conclusion. The verdict
contract — APPROVE / REJECT / ESCALATE — does not change.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Verdict(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"


@dataclass
class CIResult:
    verdict: Verdict
    exit_code: int
    output: str
    command: list[str]

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.APPROVE


def default_ci_command() -> list[str]:
    """The command CI runs, resolved to stay stdlib-only on the smoke path.

    Prefer pytest if it is installed (the real CI gate). If it is not, fall back
    to running the repo's test file directly with this interpreter — so the
    BUILD->TEST gate never depends on a third-party package being present.
    """
    py = sys.executable or "python"
    if importlib.util.find_spec("pytest") is not None:
        return [py, "-m", "pytest", "-q"]
    return [py, "test_calculator.py"]


def run_ci(
    repo: Path,
    *,
    command: list[str] | None = None,
    timeout_s: int = 120,
) -> CIResult:
    """Run the repo's tests as CI. Default verdict is REJECT.

    The function only returns APPROVE when the command exits 0. A timeout, a
    crash, a non-zero exit, or an OS error all land on REJECT — the verifier
    never approves on the absence of a failure signal, only on the presence of
    a pass signal.
    """
    cmd = command or default_ci_command()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return CIResult(Verdict.REJECT, -1, f"CI timed out after {timeout_s}s", cmd)
    except OSError as exc:
        return CIResult(Verdict.REJECT, -1, f"CI failed to start: {exc}", cmd)

    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode == 0:
        return CIResult(Verdict.APPROVE, 0, output, cmd)
    return CIResult(Verdict.REJECT, proc.returncode, output, cmd)
