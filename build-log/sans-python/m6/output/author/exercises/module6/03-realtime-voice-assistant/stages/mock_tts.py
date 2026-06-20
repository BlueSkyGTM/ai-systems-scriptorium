"""Mock Text-to-Speech stage.

Real TTS (Cartesia Sonic-2 via Pipecat's `CartesiaTTSService`) streams the
reply text back into audio. The mock wraps the reply text in a placeholder
"audio" payload and emits an AUDIO_OUT frame, adding a simulated latency. This
is the stage a barge-in cancels mid-flight.
"""

from __future__ import annotations

from pipeline import Frame, FrameProcessor, FrameType


class SynthAudio:
    """A stand-in for synthesized audio bytes (no real PCM on the smoke path)."""

    def __init__(self, text: str):
        self.text = text
        # A deterministic byte placeholder so downstream code can treat it as audio.
        self.data = text.encode("utf-8")

    def __repr__(self) -> str:
        return f"<SynthAudio {self.text!r}>"


class MockTTS(FrameProcessor):
    name = "tts"

    def __init__(self, sim_latency_ms: float = 90.0):
        self.sim_latency_ms = sim_latency_ms

    def process(self, frame: Frame):
        spent = self._sleep_sim()
        frame.meta["_last_stage_ms"] = spent
        text = str(frame.payload or "")
        return Frame(
            type=FrameType.AUDIO_OUT,
            direction=frame.direction,
            payload=SynthAudio(text),
            meta={"tts_text": text},
        )


def try_real_tts(api_key: str | None = None):  # pragma: no cover - opt-in only
    """Return a configured Cartesia TTS service, or None if unavailable."""
    if not api_key:
        return None
    try:
        # [verify:] CartesiaTTSService import path + constructor (voice_id, etc.)
        # against the installed pipecat version.
        from pipecat.services.cartesia.tts import CartesiaTTSService

        return CartesiaTTSService(api_key=api_key)
    except ImportError:
        return None
