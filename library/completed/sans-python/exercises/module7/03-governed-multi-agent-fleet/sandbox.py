"""Subprocess sandbox — the coder node's execution layer, with a timeout. No Docker.

Imported unchanged from the M6 coding agent (artifact 01). A tool call can run a
test suite, which means running arbitrary code; the sandbox runs it in a child
process under a wall-clock deadline and captures the result as structured data,
so the agent reads a verdict instead of a hang.

Framed honestly: a dev-time guardrail, not an OS security boundary. It bounds
runaway *time* and isolates a crash from the loop. Swapping the subprocess for a
container changes this file and nothing else — the loop reads a ``SandboxResult``
either way. The M7 fleet does not rebuild this; it reuses it under governance.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass

TIMED_OUT = -101  # sentinel exit code


@dataclass
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


def run(argv: list[str], cwd: str, timeout_s: float = 30.0) -> SandboxResult:
    """Run ``argv`` in ``cwd`` under a wall-clock deadline. A timeout is a result,
    not an exception — the agent decides whether to retry or abandon."""
    try:
        proc = subprocess.run(
            argv, cwd=cwd, capture_output=True, text=True, timeout=timeout_s,
        )
        return SandboxResult(proc.returncode, proc.stdout, proc.stderr, False)
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return SandboxResult(TIMED_OUT, out, err + "\n[sandbox] wall-clock timeout exceeded", True)


def run_pytest(cwd: str, timeout_s: float = 30.0) -> SandboxResult:
    """Run the project's suite as a child process under the sandbox, using the
    same interpreter that launched the fleet so the smoke path needs nothing on
    PATH and no virtualenv juggling."""
    return run([sys.executable, "-m", "pytest", "-q"], cwd=cwd, timeout_s=timeout_s)
