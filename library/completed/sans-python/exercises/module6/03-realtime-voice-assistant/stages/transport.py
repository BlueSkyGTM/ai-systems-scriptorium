"""Mock transport stage — the final hop, mouth to ear.

Real transport streams the synthesized audio to the user, typically over WebRTC
(Pipecat's `DailyTransport` / a WebRTC transport) for low-latency delivery. The
mock just passes the AUDIO_OUT frame through and charges a simulated network
latency. This is where the turn's audio "reaches the speaker"; the latency
budget is measured mouth-to-ear, so transport counts.
"""

from __future__ import annotations

from pipeline import Frame, FrameProcessor, FrameType


class MockTransport(FrameProcessor):
    name = "transport"

    def __init__(self, sim_latency_ms: float = 40.0):
        self.sim_latency_ms = sim_latency_ms

    def process(self, frame: Frame):
        spent = self._sleep_sim()
        frame.meta["_last_stage_ms"] = spent
        # Transport is the terminal stage: forward the audio frame unchanged so
        # the pipeline records final audio out.
        return Frame(
            type=FrameType.AUDIO_OUT,
            direction=frame.direction,
            payload=frame.payload,
            meta=dict(frame.meta),
        )


def try_real_transport():  # pragma: no cover - opt-in only
    """Return a Pipecat WebRTC transport class, or None if not installed."""
    try:
        # [verify:] the current Pipecat WebRTC/Daily transport import path.
        from pipecat.transports.services.daily import DailyTransport

        return DailyTransport
    except ImportError:
        return None
