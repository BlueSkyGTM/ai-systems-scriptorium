"""Subprocess sandbox — the execution layer, with a timeout. No Docker.

A tool call can run a test suite, which means running arbitrary code. The
sandbox runs it in a child process under a wall-clock deadline and captures the
result as structured data, so the agent reads a verdict instead of a hang.

Framed honestly: this is a dev-time guardrail, not an OS security boundary. It
bounds runaway *time*, captures output, and isolates a crash from the loop. It
does not contain a hostile process — for that you reach for containers or a
VM, which the M6 plan keeps off the local gate on purpose. The seam is the same
either way: the loop calls ``run()`` and reads a ``SandboxResult``; swapping the
subprocess for a container changes this file and nothing else.
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
    """Run ``argv`` in ``cwd`` under a wall-clock deadline.

    Returns a structured result. A timeout is a result, not an exception —
    the agent decides whether to retry or abandon, the same way it would on a
    non-zero exit.
    """
    try:
        proc = subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        return SandboxResult(
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        return SandboxResult(
            exit_code=TIMED_OUT,
            stdout=exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
            stderr=(exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
            + "\n[sandbox] wall-clock timeout exceeded",
            timed_out=True,
        )


def run_pytest(cwd: str, timeout_s: float = 30.0) -> SandboxResult:
    """Run the project's test suite as a child process under the sandbox.

    Uses the same interpreter that launched the agent (``sys.executable``) so the
    smoke path needs nothing on PATH and no virtualenv juggling.
    """
    return run([sys.executable, "-m", "pytest", "-q"], cwd=cwd, timeout_s=timeout_s)
