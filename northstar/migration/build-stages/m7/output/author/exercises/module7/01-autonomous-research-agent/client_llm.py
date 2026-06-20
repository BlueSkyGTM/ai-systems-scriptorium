"""Real-model adapter — the opt-in Anthropic path behind the same three seams.

This file is NOT on the smoke path. Importing it does not require the
``anthropic`` package: the import is guarded so ``python smoke.py`` and
``python -m pytest tests/`` run on the standard library alone. You reach for this
only when you set ANTHROPIC_API_KEY and want a live model driving the team.

It implements the same three seams the mock does — ``plan(question)`` for the
supervisor's Planner, ``respond(messages)`` for a sub-agent's loop, and
``synthesize(question, findings)`` for the Solver — so ``supervisor.run_team``
does not change. That is the portable seam: the team topology, the sandbox, the
fleet budget, the kill switch, and the verify gate are all model-agnostic; only
this adapter knows about a vendor.
"""

from __future__ import annotations

import json
import os

from mock_llm import ModelResponse

# Opus 4.8 input/output price per million tokens, for budget metering.
# [verify: pricing — platform.claude.com/docs/en/about-claude/pricing — confirm
#  $/1M tokens for the chosen model at build time]
_PRICE_IN_PER_MTOK = 5.00
_PRICE_OUT_PER_MTOK = 25.00

# The one tool a research sub-agent has: search its no-egress sandbox.
SEARCH_TOOL = {
    "name": "search",
    "description": "Search the sandbox corpus for evidence. Returns sources with ids to cite.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
}


class AnthropicLLM:
    """Wraps the Anthropic Messages API as the three team seams.

    Construction fails loudly if the SDK or key is missing — by design, so the
    real path is explicit and the mock path stays the default.
    """

    name = "claude-opus-4-8"

    def __init__(self, model: str = "claude-opus-4-8"):
        try:
            import anthropic  # guarded: absent on the offline smoke path
        except ImportError as exc:  # pragma: no cover - only with the SDK installed
            raise RuntimeError(
                "anthropic SDK not installed. `pip install anthropic` and set "
                "ANTHROPIC_API_KEY to use the real-model path. The smoke run and "
                "tests do not need it."
            ) from exc
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY is not set.")
        self._anthropic = anthropic
        self._client = anthropic.Anthropic()
        self.name = model

    # --- Planner seam ---------------------------------------------------
    def plan(self, question: str) -> list:  # pragma: no cover
        """Ask the model to decompose the question into sub-questions + queries.

        [verify: structured-output / JSON mode — platform.claude.com/docs — the
        Planner should return a JSON list of {id, question, query}; validate it
        before dispatch, since LLM planners are not sound-by-construction (M3).]
        """
        resp = self._client.messages.create(
            model=self.name,
            max_tokens=1024,
            system=(
                "You are a research supervisor. Decompose the question into 2-4 "
                "independent sub-questions. Reply with JSON: a list of objects "
                '{"id","question","query"} where query is keywords for retrieval.'
            ),
            messages=[{"role": "user", "content": question}],
        )
        text = next((b.text for b in resp.content if b.type == "text"), "[]")
        return json.loads(text)

    # --- Sub-agent loop seam --------------------------------------------
    def respond(self, messages: list[dict]) -> ModelResponse:  # pragma: no cover
        """One step of a sub-agent's loop: a tool_use (search) or a final finding.

        [verify: Messages API tool-use loop — the model emits a tool_use block,
        the harness runs it and returns a tool_result; the loop ends when the
        model stops calling tools. platform.claude.com/docs/en/agents-and-tools/tool-use]
        Findings must cite retrieved source ids as [S1]; the verify gate rejects
        any citation not grounded in the sandbox evidence.
        """
        api_messages = _to_api_messages(messages)
        resp = self._client.messages.create(
            model=self.name,
            max_tokens=1024,
            system=(
                "You are a research sub-agent. Search your sandbox for evidence, "
                "then answer your sub-question. Cite every claim with a retrieved "
                "source id like [S1]. Do not cite a source you did not retrieve."
            ),
            tools=[SEARCH_TOOL],
            messages=api_messages,
        )
        cost = (
            resp.usage.input_tokens / 1_000_000 * _PRICE_IN_PER_MTOK
            + resp.usage.output_tokens / 1_000_000 * _PRICE_OUT_PER_MTOK
        )
        tool_use = next((b for b in resp.content if b.type == "tool_use"), None)
        if tool_use is None:
            text = next((b.text for b in resp.content if b.type == "text"), "")
            return ModelResponse(text=text, tool_name=None, tool_args={}, cost_usd=cost)
        return ModelResponse(
            text=None, tool_name=tool_use.name,
            tool_args=dict(tool_use.input), cost_usd=cost,
        )

    # --- Solver seam ----------------------------------------------------
    def synthesize(self, question: str, findings: list) -> str:  # pragma: no cover
        """Stitch the verified findings into one cited answer (ReWOO Solver)."""
        packet = "\n".join(f"- ({q}) {f}" for q, f in findings)
        resp = self._client.messages.create(
            model=self.name,
            max_tokens=1024,
            system=(
                "You are a research supervisor. Synthesize the verified findings "
                "into one answer. Preserve every [S#] citation."
            ),
            messages=[{"role": "user",
                       "content": f"Question: {question}\n\nVerified findings:\n{packet}"}],
        )
        return next((b.text for b in resp.content if b.type == "text"), "")


def _to_api_messages(messages: list[dict]) -> list[dict]:  # pragma: no cover
    """Fold a sub-agent's flat buffer into the API's user/assistant turn shape.

    The loop stores tool calls and results as flat records; the Messages API
    wants assistant tool_use blocks paired with user tool_result blocks. This
    translation lives in the adapter so the loop stays vendor-neutral.
    """
    out: list[dict] = []
    for m in messages:
        role = m.get("role")
        if role == "user":
            out.append({"role": "user", "content": m["content"]})
        elif role == "subquestion":
            continue  # internal routing record; not part of the API conversation
        elif role == "tool_call":
            out.append({
                "role": "assistant",
                "content": [{
                    "type": "tool_use",
                    "id": f"call_{len(out)}",
                    "name": m["name"],
                    "input": m["args"],
                }],
            })
        elif role == "tool_result":
            out.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": f"call_{len(out) - 1}",
                    "content": m["content"],
                }],
            })
    return out
