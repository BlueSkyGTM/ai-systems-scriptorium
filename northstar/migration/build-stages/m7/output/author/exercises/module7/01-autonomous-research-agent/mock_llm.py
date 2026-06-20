"""Deterministic mock model — the policy seam, scripted for the offline smoke run.

The M6 coding agent proved a point by driving its loop with a deterministic
policy instead of a live model: the run becomes reproducible and shows the
*harness* was the interesting part. The same move here, raised to a team — one
mock plays three roles behind one ``respond``-style interface:

  - **plan(question)**  → the supervisor's Planner: decompose into sub-questions
                          (the M3 ReWOO Planner — describe the work, call no tools).
  - sub-agent loop      → ``respond(messages)`` returns a search tool call, then a
                          final cited finding (the M6 worker loop, scripted).
  - **synthesize(...)** → the supervisor's Solver: stitch verified findings into
                          one cited answer (the ReWOO Solver).

A real model plugs into the same three seams with no contract change — see
``client_llm.py`` for the opt-in Anthropic path. Determinism comes from counting
tool calls in the buffer and from a fixed question→sub-question map, not from
anything stochastic.
"""

from __future__ import annotations

from dataclasses import dataclass

COST_PER_CALL_USD = 0.01  # flat per-call charge the fleet budget meters


@dataclass
class ModelResponse:
    """What a sub-agent loop reads back from any model — mock or real."""

    text: str | None          # final finding when no tool call
    tool_name: str | None
    tool_args: dict
    cost_usd: float

    @property
    def is_final(self) -> bool:
        return self.tool_name is None


# The fixed decomposition the supervisor's Planner returns for the smoke
# question. A real planner derives this; the mock knows it because it is a
# fixture-scale stand-in. Each entry is a sub-question plus the search query the
# sub-agent will run in its sandbox.
PLAN = {
    "What makes a multi-agent system reliable in production?": [
        {"id": "sq1", "question": "What is the dominant multi-agent failure family?",
         "query": "multi-agent failure specification coordination verification mast"},
        {"id": "sq2", "question": "How does a verification gate improve reliability?",
         "query": "verification gate external check critic grounding reliability"},
        {"id": "sq3", "question": "What operator controls bound a fleet's cost and risk?",
         "query": "budget kill-switch operator control fleet cost governance"},
    ],
}


class MockLLM:
    """A scripted policy covering all three team roles. Same seams a real client wraps."""

    name = "mock-deterministic-v1"

    # --- Supervisor role: Planner ---------------------------------------
    def plan(self, question: str) -> list:
        """Decompose a research question into typed sub-questions (ReWOO Planner)."""
        return [dict(sq) for sq in PLAN.get(question, [])]

    # --- Sub-agent role: the worker loop --------------------------------
    def respond(self, messages: list[dict]) -> ModelResponse:
        """One step of a sub-agent's loop: search once, then answer with citations.

        Step 0 (no tool calls yet): issue the search tool call for this
        sub-question. Step 1+ (evidence in buffer): emit a final finding that
        cites the evidence ids the sandbox returned — so the verify gate can
        ground every citation.
        """
        tool_calls = [m for m in messages if m.get("role") == "tool_call"]
        if not tool_calls:
            sub = _current_subquestion(messages)
            return ModelResponse(
                text=None,
                tool_name="search",
                tool_args={"query": sub["query"]},
                cost_usd=COST_PER_CALL_USD,
            )
        # Compose a finding that cites every evidence id the sandbox handed back.
        ids = _evidence_ids(messages)
        sub = _current_subquestion(messages)
        if ids:
            citations = " ".join(f"[{i}]" for i in ids)
            finding = f"On '{sub['question']}': the evidence supports a clear answer. {citations}"
        else:
            finding = f"On '{sub['question']}': no evidence found."
        return ModelResponse(text=finding, tool_name=None, tool_args={}, cost_usd=COST_PER_CALL_USD)

    # --- Supervisor role: Solver ----------------------------------------
    def synthesize(self, question: str, findings: list) -> str:
        """Stitch verified findings into one cited answer (ReWOO Solver).

        ``findings`` is a list of (sub_question, finding_text) for findings that
        passed the gate. The solver concatenates them and carries every citation
        through, so the final answer is traceable end to end.
        """
        lines = [f"Answer to: {question}", ""]
        for sub_q, text in findings:
            lines.append(f"- {text}")
        return "\n".join(lines)


def _current_subquestion(messages: list[dict]) -> dict:
    """Pull the sub-question record the sub-agent was dispatched with."""
    for m in messages:
        if m.get("role") == "subquestion":
            return m["sub"]
    return {"id": "?", "question": "?", "query": ""}


def _evidence_ids(messages: list[dict]) -> list:
    """Collect evidence ids the sandbox returned in tool results."""
    ids: list = []
    for m in messages:
        if m.get("role") == "tool_result":
            ids.extend(m.get("evidence_ids", []))
    # stable, de-duplicated
    seen, out = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


# ---------------------------------------------------------------------------
# Pathological policies the tests use to prove the operator surfaces fire.
# ---------------------------------------------------------------------------

class FabricatingMockLLM(MockLLM):
    """A sub-agent that cites a source it never retrieved.

    Used by the tests to prove the verify gate REJECTS an ungrounded finding —
    the fabricated citation that would otherwise seed a cascading error — even
    though the sub-agent declares an answer.
    """

    name = "mock-fabricating-v1"

    def respond(self, messages: list[dict]) -> ModelResponse:
        tool_calls = [m for m in messages if m.get("role") == "tool_call"]
        if not tool_calls:
            sub = _current_subquestion(messages)
            return ModelResponse(None, "search", {"query": sub["query"]}, COST_PER_CALL_USD)
        sub = _current_subquestion(messages)
        # Cite [S99] — a source id no sandbox ever returns.
        finding = f"On '{sub['question']}': fabricated certainty. [S99]"
        return ModelResponse(finding, None, {}, COST_PER_CALL_USD)


class LoopingMockLLM(MockLLM):
    """A sub-agent that searches forever, never producing a finding.

    Used to prove the shared fleet budget's call cap stops a runaway team — the
    runaway is now N loops, not one.
    """

    name = "mock-looping-v1"

    def respond(self, messages: list[dict]) -> ModelResponse:
        sub = _current_subquestion(messages)
        return ModelResponse(None, "search", {"query": sub["query"]}, COST_PER_CALL_USD)
