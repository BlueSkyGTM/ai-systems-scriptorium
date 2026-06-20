"""A composable, frame-based voice pipeline — Pipecat-shaped, stdlib-only.

The real Pipecat moves audio and text through a chain of `FrameProcessor`s as
`Frame`s with an explicit direction (DOWNSTREAM toward the user, UPSTREAM back
toward the mic). This module reproduces that *shape* with the Python standard
library so the smoke path runs with no audio hardware, no cloud, and no
third-party install. The seam is identical to Pipecat's: a list of stages, each
consuming a frame and emitting the next, wired VAD -> STT -> LLM -> TTS ->
transport. Swap a stage and the rest of the pipeline does not change.

Real Pipecat is opt-in behind a guarded import (see `try_real_pipecat`); the
mock stages in `stages/` are the default and carry a *simulated* per-stage
latency so the latency budget is measurable offline.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterable, Optional


class FrameDirection(Enum):
    """Frames flow two ways, exactly as in Pipecat."""

    DOWNSTREAM = "downstream"  # mic -> ... -> speaker (the forward path)
    UPSTREAM = "upstream"  # control signals back toward the source (e.g. interrupt)


class FrameType(Enum):
    """The minimal frame vocabulary this pipeline needs."""

    AUDIO_IN = "audio_in"  # raw user speech (a chunk, real or simulated)
    SPEECH_STARTED = "speech_started"  # VAD: the user began talking
    TRANSCRIPT = "transcript"  # STT output: text
    LLM_TEXT = "llm_text"  # LLM output: the reply text
    AUDIO_OUT = "audio_out"  # TTS output: synthesized audio ready for transport
    INTERRUPT = "interrupt"  # barge-in: cancel the in-flight turn (UPSTREAM)


@dataclass
class Frame:
    """One unit of data flowing through the pipeline.

    `payload` is whatever the stage produced (a string for text frames, a bytes
    placeholder for audio). `meta` carries the per-stage latency ledger so the
    measurement layer (`latency.py`) can read it off the finished frame.
    """

    type: FrameType
    direction: FrameDirection = FrameDirection.DOWNSTREAM
    payload: object = None
    meta: dict = field(default_factory=dict)


class CancelledTurn(Exception):
    """Raised when a barge-in cancels an in-flight downstream turn."""


class FrameProcessor:
    """Base class for a pipeline stage.

    A processor receives a frame, does its work, and returns the next frame (or
    `None` to swallow it). `name` and `sim_latency_ms` are read by the latency
    layer. Subclasses live in `stages/`.
    """

    name: str = "processor"
    sim_latency_ms: float = 0.0

    def process(self, frame: Frame) -> Optional[Frame]:  # pragma: no cover - overridden
        raise NotImplementedError

    def _sleep_sim(self) -> float:
        """Burn the configured simulated latency and return the ms spent.

        Latency is *simulated*: a real deployment would block on a network round
        trip to an STT/TTS provider. We sleep a tiny fraction of the configured
        budget so the smoke path stays fast, and record the *configured* budget
        (not the wall-clock sleep) as the stage's contribution. That keeps the
        gate deterministic regardless of how fast the test machine is.
        """
        # Sleep a small, capped real amount purely so wall-clock totals are
        # non-zero and ordering is observable; never the full simulated budget.
        real_sleep_s = min(self.sim_latency_ms, 5.0) / 1000.0
        if real_sleep_s > 0:
            time.sleep(real_sleep_s)
        return self.sim_latency_ms


@dataclass
class TurnResult:
    """What one downstream turn produced, plus its per-stage latency ledger."""

    frames: list = field(default_factory=list)
    stage_latencies_ms: dict = field(default_factory=dict)
    cancelled: bool = False
    final_audio: Optional[object] = None

    @property
    def total_latency_ms(self) -> float:
        return sum(self.stage_latencies_ms.values())


class VoicePipeline:
    """A linear chain of `FrameProcessor`s — the Pipecat `Pipeline` shape.

    `run_turn` drives one user utterance through every downstream stage and
    accumulates the simulated per-stage latency. `interrupt_check` is polled
    before each stage; if it returns True the turn raises `CancelledTurn`,
    modeling barge-in (a new user frame arriving mid-turn). The check is the
    seam `barge_in.py` drives.
    """

    def __init__(self, stages: Iterable[FrameProcessor]):
        self.stages = list(stages)

    def run_turn(
        self,
        user_text: str,
        interrupt_check: Optional[Callable[[str], bool]] = None,
    ) -> TurnResult:
        """Run one turn. `interrupt_check(stage_name) -> bool` polls for barge-in."""
        result = TurnResult()
        frame = Frame(
            type=FrameType.AUDIO_IN,
            direction=FrameDirection.DOWNSTREAM,
            payload=user_text,
            meta={"user_text": user_text},
        )
        for stage in self.stages:
            if interrupt_check is not None and interrupt_check(stage.name):
                result.cancelled = True
                raise CancelledTurn(f"barge-in before stage '{stage.name}'")
            next_frame = stage.process(frame)
            spent = frame.meta.get("_last_stage_ms", stage.sim_latency_ms)
            result.stage_latencies_ms[stage.name] = spent
            if next_frame is None:
                break
            # Carry the latency ledger forward on the new frame.
            next_frame.meta.update(frame.meta)
            frame = next_frame
            result.frames.append(frame)
        result.final_audio = frame.payload if frame.type == FrameType.AUDIO_OUT else None
        return result


def try_real_pipecat():
    """Opt-in: return the real Pipecat building blocks, or None if not installed.

    The smoke path NEVER calls this. It exists so a student who has run
    `pip install pipecat-ai` can swap the mock stages for real services without
    touching `pipeline.py`. Every import is guarded.
    """
    try:  # pragma: no cover - exercised only when pipecat is installed
        from pipecat.frames.frames import Frame as PCFrame  # noqa: F401
        from pipecat.pipeline.pipeline import Pipeline as PCPipeline  # noqa: F401
        from pipecat.pipeline.runner import PipelineRunner  # noqa: F401
        from pipecat.pipeline.task import PipelineTask  # noqa: F401

        return {
            "Frame": PCFrame,
            "Pipeline": PCPipeline,
            "PipelineRunner": PipelineRunner,
            "PipelineTask": PipelineTask,
        }
    except ImportError:
        return None


def build_default_pipeline(
    vad_ms: float = 30.0,
    stt_ms: float = 120.0,
    llm_ms: float = 220.0,
    tts_ms: float = 90.0,
    transport_ms: float = 40.0,
) -> VoicePipeline:
    """Wire the four mock stages plus a transport hop into the standard cascade.

    The default per-stage budgets sum to 500 ms — inside the ~450-600 ms voice
    budget. The smoke harness blows one stage on purpose to prove the gate bites.
    """
    from stages.mock_vad import MockVAD
    from stages.mock_stt import MockSTT
    from stages.mock_llm import MockLLM
    from stages.mock_tts import MockTTS
    from stages.transport import MockTransport

    return VoicePipeline(
        [
            MockVAD(sim_latency_ms=vad_ms),
            MockSTT(sim_latency_ms=stt_ms),
            MockLLM(sim_latency_ms=llm_ms),
            MockTTS(sim_latency_ms=tts_ms),
            MockTransport(sim_latency_ms=transport_ms),
        ]
    )
