"""Deterministic mock model — the policy seam, scripted for the offline smoke run.

A deterministic policy and a frontier model are interchangeable at the model seam
(M6): scripting the policy makes the run reproducible and proves the *governance*
was the interesting part, not the inference. A real model plugs into the same
``respond(messages)`` seam with no contract change — see ``client_llm.py`` for the
opt-in Anthropic path, guarded so this smoke path stays standard-library-only.

Each agent in the team drives this mock with its own scripted plan. The coder
node reuses the exact five-state plan from the M6 coding agent (survey, fix, run,
verify, done). The architect, reviewer, and tester drive shorter scripts. Cost is
a flat per-call charge the fleet budget meters.
"""

from __future__ import annotations

from dataclasses import dataclass

COST_PER_CALL_USD = 0.01  # flat per-call charge the fleet budget meters

# The corrected source the coder mock "writes". The fixture ships a broken add();
# the fix is the one-character bug repair — the same fixture the M6 coding agent
# fixes, reused here so the coder node is literally the M6 loop.
FIXED_SOURCE = '''\
"""A tiny calculator with one bug the coder node must fix."""


def add(a, b):
    return a + b
'''

BAD_SOURCE = '''\
"""A tiny calculator the coder node failed to fix."""


def add(a, b):
    return a - b  # still wrong
'''


@dataclass
class ModelResponse:
    """What every loop reads back from any model — mock or real."""

    text: str | None
    tool_name: str | None
    tool_args: dict
    cost_usd: float

    @property
    def is_final(self) -> bool:
        return self.tool_name is None


class CoderMockLLM:
    """The M6 coding-agent policy, reused unchanged as the coder node's brain.

    Walks the fixed five-state plan against the fixture's known bug:
        SURVEY    -> read the broken file
        FIX       -> write the corrected file
        RUN_TESTS -> run the suite
        VERIFY    -> read the observation; finish
    Determinism comes from counting tool calls already in the buffer.
    """

    name = "mock-coder-v1"

    def __init__(self, source: str = FIXED_SOURCE):
        self._source = source  # swap to BAD_SOURCE to drive the bad-patch test

    def respond(self, messages: list[dict]) -> ModelResponse:
        n = len([m for m in messages if m.get("role") == "tool_call"])
        if n == 0:  # SURVEY
            return ModelResponse(None, "read_file", {"path": "calculator.py"}, COST_PER_CALL_USD)
        if n == 1:  # FIX
            return ModelResponse(None, "write_file",
                                 {"path": "calculator.py", "content": self._source},
                                 COST_PER_CALL_USD)
        if n == 2:  # RUN_TESTS
            return ModelResponse(None, "run_tests", {}, COST_PER_CALL_USD)
        # DONE — the coder does not declare the work merged; the gate and the
        # human do. It just reports its diff is written and self-tested.
        return ModelResponse("Implemented the fix and ran the suite.", None, {}, COST_PER_CALL_USD)


class StuckCoderMockLLM:
    """A pathological coder that calls the same tool forever, never finishing.
    Used to prove the fleet budget stops a per-agent runaway."""

    name = "mock-coder-stuck-v1"

    def respond(self, messages: list[dict]) -> ModelResponse:
        return ModelResponse(None, "read_file", {"path": "calculator.py"}, COST_PER_CALL_USD)


class SinglePassMockLLM:
    """A one-call policy: the architect, reviewer, and tester each reason once
    and return. They do not loop over a sandbox; they make one decision."""

    name = "mock-single-pass-v1"

    def respond(self, messages: list[dict]) -> ModelResponse:
        return ModelResponse("decision", None, {}, COST_PER_CALL_USD)
