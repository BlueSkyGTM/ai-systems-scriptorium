"""Deterministic mock model — the reasoning seam, scripted for the smoke run.

The specialists and supervisor would, in production, call a frontier model to
turn raw cluster data into a hypothesis and a remediation. On the smoke path that
call is this deterministic stand-in, so the run is reproducible on the standard
library alone and the thing under test is the TEAM (read-only fan-out, supervisor
synthesis, HITL gate), not the model's mood. This is the M5-capstone discipline:
a deterministic policy makes the harness the interesting part.

A real model is opt-in behind a guarded import, so a missing `anthropic` package
never breaks the gate.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Remediation:
    """A concrete, reversible change the supervisor proposes for a human."""

    deployment: str
    namespace: str
    change: dict           # e.g. {"memory_limit_mib": 192}
    rationale: str
    rollback: str          # how to undo it — required for the HITL case


def synthesize_remediation(findings: list, evidence: dict) -> Remediation:
    """Turn the assembled findings into one proposed change.

    Deterministic rule for the fixture: if the team's evidence points at an
    OOMKilled container with a too-low memory limit, propose raising the limit to
    the metrics reader's suggested value. The rollback is the prior limit, so the
    proposal carries its own undo (HITL move 2: surface the rollback plan).
    """
    suggested = evidence.get("suggested_limit_mib")
    prior = evidence.get("memory_limit_mib")
    deployment = evidence.get("owner_deployment", "unknown")
    namespace = evidence.get("namespace", "default")

    if suggested is not None and prior is not None:
        return Remediation(
            deployment=deployment,
            namespace=namespace,
            change={"memory_limit_mib": suggested},
            rationale=(
                f"Container OOMKilled: working set exceeds the {prior}Mi memory "
                f"limit. Raise the limit to {suggested}Mi to give headroom and "
                f"stop the crash loop."
            ),
            rollback=f"set deployment/{deployment} memory limit back to {prior}Mi",
        )
    # No confident remediation: propose nothing actionable (the supervisor will
    # escalate rather than invent a change).
    return Remediation(
        deployment=deployment,
        namespace=namespace,
        change={},
        rationale="No confident remediation derived from the evidence.",
        rollback="n/a",
    )


# --- real model (opt-in) ---------------------------------------------------- #

def real_synthesize(findings: list, evidence: dict) -> Remediation:  # pragma: no cover
    """Reached only when USE_REAL_LLM and a key are set. Guarded import."""
    try:
        import anthropic  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "real LLM requested but `anthropic` is not installed; "
            "the smoke path uses the deterministic mock — see README.md"
        ) from exc
    raise NotImplementedError(
        "Wire a real model here to reason over findings. The mock path is what "
        "the BUILD->TEST gate runs."
    )


def use_real_llm() -> bool:
    return bool(os.environ.get("USE_REAL_LLM")) and bool(os.environ.get("ANTHROPIC_API_KEY"))
