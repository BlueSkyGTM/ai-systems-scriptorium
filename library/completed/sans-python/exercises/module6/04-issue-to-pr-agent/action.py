"""The action step: read an issue, draft a code fix. This is artifact 01 in miniature.

In production this slot is the terminal coding agent from artifact 01 — a real
plan/act/observe loop on a frontier model inside a sandbox. Here it is the
smallest self-contained coder that exercises the SAME contract: take an issue
and a repo, propose a concrete file edit, and report the tokens it spent so the
budget stage can charge it.

The smoke path uses a DETERMINISTIC mock "LLM" so the test is reproducible with
the standard library alone. A real model is opt-in and guarded behind a runtime
import, so a missing `anthropic` package never breaks the smoke gate.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Issue:
    """The trigger payload. Parsed from the fixture's ISSUE.md."""

    title: str
    body: str
    # The file the issue points at and the failing symbol, parsed from the body.
    target_file: str | None = None


@dataclass
class FixProposal:
    """What the action stage hands to the verifier. A concrete, applied edit."""

    file: str
    summary: str
    tokens_used: int
    rationale: str


def parse_issue(text: str) -> Issue:
    """Pull a title, body, and a `file:` hint out of an ISSUE.md."""
    lines = text.splitlines()
    title = "Untitled issue"
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    target = None
    m = re.search(r"(?im)^\s*file:\s*(\S+)", text)
    if m:
        target = m.group(1)
    return Issue(title=title, body=text, target_file=target)


# --------------------------------------------------------------------------- #
# The mock coder (smoke path). Deterministic: same issue + repo -> same edit.
# --------------------------------------------------------------------------- #

def _mock_fix(repo: Path, issue: Issue) -> FixProposal:
    """Apply the known fix for the fixture's seeded bug.

    The fixture ships an off-by-one in `add()` (it returns `a + b + 1`). A real
    coding agent would localize this from the failing test; the mock encodes the
    minimal repair directly so the loop's plumbing — not the model — is what the
    smoke test exercises. This mirrors capstone lesson 29: a deterministic policy
    makes the harness, not the model, the thing under test.
    """
    target = issue.target_file or "calculator.py"
    path = repo / target
    src = path.read_text(encoding="utf-8")

    fixed = src.replace("return a + b + 1", "return a + b")
    if fixed == src:
        # No known repair: report a no-op edit so the verifier (real CI) decides.
        return FixProposal(
            file=target,
            summary="no change proposed (no known repair for this issue)",
            tokens_used=900,
            rationale="Mock coder found no matching defect pattern; CI will gate.",
        )
    path.write_text(fixed, encoding="utf-8")
    return FixProposal(
        file=target,
        summary="fix off-by-one in add(): `a + b + 1` -> `a + b`",
        tokens_used=1200,
        rationale=(
            "The failing test expects add(2, 3) == 5 but the implementation adds an "
            "extra 1. Removed the `+ 1` so the function matches its contract."
        ),
    )


# --------------------------------------------------------------------------- #
# The real coder (opt-in). Guarded so a missing SDK never breaks the smoke gate.
# --------------------------------------------------------------------------- #

def _real_fix(repo: Path, issue: Issue) -> FixProposal:  # pragma: no cover - opt-in
    """Draft a fix with a real model. Reached only when use_real_llm=True.

    This is where artifact 01 plugs in. Kept behind a runtime import so the
    smoke path never depends on `anthropic` being installed.
    """
    try:
        import anthropic  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "real LLM requested but `anthropic` is not installed; "
            "the smoke path uses the deterministic mock — see README.md"
        ) from exc
    raise NotImplementedError(
        "Wire artifact 01 (the terminal coding agent) in here. The mock path "
        "is what the BUILD->TEST gate runs."
    )


def draft_fix(repo: Path, issue: Issue, *, use_real_llm: bool = False) -> FixProposal:
    """Produce a fix proposal. Mock by default; real model only when asked."""
    if use_real_llm and os.environ.get("ANTHROPIC_API_KEY"):
        return _real_fix(repo, issue)
    return _mock_fix(repo, issue)
