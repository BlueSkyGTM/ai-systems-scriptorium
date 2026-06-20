"""Deterministic mock model — the policy seam, scripted for the smoke run.

The end-to-end coding agent (M5 capstone component 29) proves a point by using
a deterministic policy instead of a live model: it makes the run reproducible
and shows that the *harness* was the interesting part. A real model plugs into
the same seam with no contract change — see ``client_llm.py`` for the opt-in
Anthropic path.

This mock implements one model interface method: ``respond(messages)`` returns
either a tool call or a final answer, plus a token cost the budget charges. It
walks a fixed five-state plan against the fixture's known bug:

  SURVEY    → read the broken file
  FIX       → write the corrected file
  RUN_TESTS → run the suite
  VERIFY    → read the test observation; if green, finish
  DONE      → final answer, no tool call

Determinism comes from counting how many tool calls have already happened in
the message buffer, not from anything stochastic.
"""

from __future__ import annotations

from dataclasses import dataclass

# The corrected source the mock "writes". The fixture ships a broken add(); the
# fix is the one-character bug repair. The mock knows the answer because it is a
# fixture-scale stand-in for a model that would derive it.
FIXED_SOURCE = '''\
"""A tiny calculator with one bug the agent must fix."""


def add(a, b):
    return a + b
'''

COST_PER_CALL_USD = 0.01  # flat per-call charge the budget meters


@dataclass
class ModelResponse:
    """What the loop reads back from any model — mock or real."""

    text: str | None  # final answer when no tool call
    tool_name: str | None
    tool_args: dict
    cost_usd: float

    @property
    def is_final(self) -> bool:
        return self.tool_name is None


class MockLLM:
    """A scripted policy. Same ``respond`` signature a real client wraps."""

    name = "mock-deterministic-v1"

    def respond(self, messages: list[dict]) -> ModelResponse:
        tool_calls = [m for m in messages if m.get("role") == "tool_call"]
        n = len(tool_calls)

        if n == 0:  # SURVEY
            return ModelResponse(
                text=None,
                tool_name="read_file",
                tool_args={"path": "calculator.py"},
                cost_usd=COST_PER_CALL_USD,
            )
        if n == 1:  # FIX
            return ModelResponse(
                text=None,
                tool_name="write_file",
                tool_args={"path": "calculator.py", "content": FIXED_SOURCE},
                cost_usd=COST_PER_CALL_USD,
            )
        if n == 2:  # RUN_TESTS
            return ModelResponse(
                text=None,
                tool_name="run_tests",
                tool_args={},
                cost_usd=COST_PER_CALL_USD,
            )
        # VERIFY / DONE — read the last observation; finish either way and let
        # the verify gate be the authority on pass/fail.
        return ModelResponse(
            text="Fixed the bug in calculator.add and the tests pass.",
            tool_name=None,
            tool_args={},
            cost_usd=COST_PER_CALL_USD,
        )


class StuckMockLLM:
    """A pathological policy: calls the same tool forever, never finishing.

    Used by the tests to prove the budget's iteration cap stops a runaway loop.
    """

    name = "mock-stuck-v1"

    def respond(self, messages: list[dict]) -> ModelResponse:
        return ModelResponse(
            text=None,
            tool_name="read_file",
            tool_args={"path": "calculator.py"},
            cost_usd=COST_PER_CALL_USD,
        )


class BadPatchMockLLM:
    """A policy that writes a patch that does NOT fix the bug, then finishes.

    Used by the tests to prove the verify gate REJECTS a bad patch even when the
    model declares success.
    """

    name = "mock-badpatch-v1"

    BAD_SOURCE = '''\
"""A tiny calculator the agent failed to fix."""


def add(a, b):
    return a - b  # still wrong
'''

    def respond(self, messages: list[dict]) -> ModelResponse:
        tool_calls = [m for m in messages if m.get("role") == "tool_call"]
        n = len(tool_calls)
        if n == 0:
            return ModelResponse(None, "write_file",
                                 {"path": "calculator.py", "content": self.BAD_SOURCE},
                                 COST_PER_CALL_USD)
        return ModelResponse("I fixed it.", None, {}, COST_PER_CALL_USD)
