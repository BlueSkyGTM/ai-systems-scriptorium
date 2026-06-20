"""Real-model adapter — the opt-in Anthropic path behind the same seam.

This file is NOT on the smoke path. Importing the package does not require the
``anthropic`` SDK: the import below is guarded, so ``python smoke.py`` and
``python -m pytest tests/`` run on the standard library alone. You reach for this
only when you set ANTHROPIC_API_KEY and want a live model driving the nodes.

It implements the same ``respond(messages) -> ModelResponse`` interface the mock
does, so no node changes. Point any node at a real model by passing it in the
``models`` dict to ``Fleet.ship_feature`` — e.g. give the coders a live model and
leave the architect/reviewer/tester on cheap deterministic policies. That is the
portable seam (M6): the loop, the governance, the A2A wire are all model-agnostic;
only this adapter knows about a vendor.
"""

from __future__ import annotations

import os

import tools
from mock_llm import ModelResponse

# Opus 4.8 input/output price per million tokens, for budget metering.
# [verify: pricing — platform.claude.com/docs/en/about-claude/pricing — Opus 4.8]
_PRICE_IN_PER_MTOK = 5.00
_PRICE_OUT_PER_MTOK = 25.00


class AnthropicLLM:
    """Wraps the Anthropic Messages API tool-use loop as one ``respond`` step.

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
        self._client = anthropic.Anthropic()
        self.name = model

    def respond(self, messages: list[dict]) -> ModelResponse:  # pragma: no cover
        """Translate the loop's message buffer into one Messages API call.

        [verify: Messages API tool-use loop — model emits a tool_use block, the
        harness executes it and returns a tool_result; stop_reason 'end_turn'
        ends the loop. platform.claude.com/docs/en/agents-and-tools/tool-use]
        """
        api_messages = _to_api_messages(messages)
        tool_defs = [
            {"name": s["name"], "description": s["description"], "input_schema": s["parameters"]}
            for s in tools.TOOL_SCHEMAS.values()
        ]
        resp = self._client.messages.create(
            model=self.name, max_tokens=2048,
            system=_system_text(messages), tools=tool_defs, messages=api_messages,
        )
        cost = (resp.usage.input_tokens / 1_000_000 * _PRICE_IN_PER_MTOK
                + resp.usage.output_tokens / 1_000_000 * _PRICE_OUT_PER_MTOK)
        tool_use = next((b for b in resp.content if b.type == "tool_use"), None)
        if tool_use is None:
            text = next((b.text for b in resp.content if b.type == "text"), "")
            return ModelResponse(text=text, tool_name=None, tool_args={}, cost_usd=cost)
        return ModelResponse(text=None, tool_name=tool_use.name,
                             tool_args=dict(tool_use.input), cost_usd=cost)


def _system_text(messages: list[dict]) -> str:
    for m in messages:
        if m.get("role") == "system":
            return m["content"]
    return ""


def _to_api_messages(messages: list[dict]) -> list[dict]:  # pragma: no cover
    """Fold the loop's flat buffer into the API's user/assistant turn shape."""
    out: list[dict] = []
    for m in messages:
        role = m.get("role")
        if role == "user":
            out.append({"role": "user", "content": m["content"]})
        elif role == "tool_call":
            out.append({"role": "assistant", "content": [{
                "type": "tool_use", "id": f"call_{len(out)}",
                "name": m["name"], "input": m["args"]}]})
        elif role == "tool_result":
            out.append({"role": "user", "content": [{
                "type": "tool_result", "tool_use_id": f"call_{len(out) - 1}",
                "content": m["content"]}]})
    return out
