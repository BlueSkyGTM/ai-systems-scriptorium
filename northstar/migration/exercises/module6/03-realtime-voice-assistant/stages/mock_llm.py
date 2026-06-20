"""Mock LLM stage.

Real deployment streams tokens from a frontier model (Pipecat's
`AnthropicLLMService` / `OpenAILLMService`). The mock returns a deterministic
canned reply keyed off the transcript, adding a simulated latency. No network,
no API key — the smoke path never calls a real model.
"""

from __future__ import annotations

import os

from pipeline import Frame, FrameProcessor, FrameType

# A tiny deterministic "model": canned replies by keyword, with a default.
_CANNED = {
    "hours": "We are open from nine to five, Monday through Friday.",
    "refund": "I can start a refund for you. May I have your order number?",
    "hello": "Hi there. How can I help you today?",
}
_DEFAULT_REPLY = "Got it. Let me help you with that."


class MockLLM(FrameProcessor):
    name = "llm"

    def __init__(self, sim_latency_ms: float = 220.0):
        self.sim_latency_ms = sim_latency_ms

    def process(self, frame: Frame):
        spent = self._sleep_sim()
        frame.meta["_last_stage_ms"] = spent
        transcript = str(frame.payload or "").lower()
        reply = _DEFAULT_REPLY
        for key, value in _CANNED.items():
            if key in transcript:
                reply = value
                break
        return Frame(
            type=FrameType.LLM_TEXT,
            direction=frame.direction,
            payload=reply,
            meta={"llm_reply": reply},
        )


def try_real_llm():  # pragma: no cover - opt-in only
    """Return a configured Anthropic LLM service, or None if unavailable.

    Reads ANTHROPIC_API_KEY from `.env` in a real deployment.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        # [verify:] AnthropicLLMService import path + model id (current model is
        # claude-opus-4-8 / a Sonnet for latency) against pipecat + claude-api.
        from pipecat.services.anthropic.llm import AnthropicLLMService

        return AnthropicLLMService(api_key=api_key)
    except ImportError:
        return None
