"""Mock Voice Activity Detection stage.

Real VAD (Silero v5 via Pipecat's `SileroVADAnalyzer`) decides when the user is
actually speaking versus pausing. Here the input is text, so "speech detected"
is true whenever the utterance is non-empty. The stage emits a SPEECH_STARTED
signal then forwards the audio downstream, adding a small simulated latency.
"""

from __future__ import annotations

from pipeline import Frame, FrameProcessor, FrameType


class MockVAD(FrameProcessor):
    name = "vad"

    def __init__(self, sim_latency_ms: float = 30.0):
        self.sim_latency_ms = sim_latency_ms

    def process(self, frame: Frame):
        spent = self._sleep_sim()
        frame.meta["_last_stage_ms"] = spent
        text = frame.payload or ""
        speaking = bool(str(text).strip())
        frame.meta["vad_speaking"] = speaking
        # VAD forwards the (audio) frame downstream unchanged; STT reads it next.
        return Frame(
            type=FrameType.AUDIO_IN,
            direction=frame.direction,
            payload=text,
            meta={"vad_speaking": speaking},
        )


def try_real_vad():  # pragma: no cover - opt-in only
    """Return Pipecat's Silero VAD analyzer, or None if not installed."""
    try:
        # [verify:] exact import path for SileroVADAnalyzer in the installed
        # pipecat version — confirm against pipecat docs at build time.
        from pipecat.audio.vad.silero import SileroVADAnalyzer

        return SileroVADAnalyzer
    except ImportError:
        return None
