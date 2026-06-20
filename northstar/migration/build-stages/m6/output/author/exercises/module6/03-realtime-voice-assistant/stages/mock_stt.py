"""Mock Speech-to-Text stage.

Real STT (Deepgram Nova-3 via Pipecat's `DeepgramSTTService`) turns streaming
audio into text. The mock treats the inbound payload as already-transcribed
text and emits a TRANSCRIPT frame, adding a simulated latency. Deterministic:
the same input always yields the same transcript.
"""

from __future__ import annotations

from pipeline import Frame, FrameProcessor, FrameType


class MockSTT(FrameProcessor):
    name = "stt"

    def __init__(self, sim_latency_ms: float = 120.0):
        self.sim_latency_ms = sim_latency_ms

    def process(self, frame: Frame):
        spent = self._sleep_sim()
        frame.meta["_last_stage_ms"] = spent
        # The "transcript" is the user text, normalized — deterministic.
        transcript = str(frame.payload or "").strip()
        return Frame(
            type=FrameType.TRANSCRIPT,
            direction=frame.direction,
            payload=transcript,
            meta={"transcript": transcript},
        )


def try_real_stt(api_key: str | None = None):  # pragma: no cover - opt-in only
    """Return a configured Deepgram STT service, or None if unavailable.

    Reads the key from `.env` (DEEPGRAM_API_KEY) in a real deployment.
    """
    if not api_key:
        return None
    try:
        # [verify:] DeepgramSTTService import path + constructor signature
        # against the installed pipecat version.
        from pipecat.services.deepgram.stt import DeepgramSTTService

        return DeepgramSTTService(api_key=api_key)
    except ImportError:
        return None
