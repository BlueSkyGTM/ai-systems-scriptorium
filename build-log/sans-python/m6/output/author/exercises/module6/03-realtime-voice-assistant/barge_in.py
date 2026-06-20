"""Barge-in — a new user frame cancels the in-flight turn.

In a real call the user talks over the agent. VAD fires SPEECH_STARTED mid-turn
and the agent must stop talking *now* — keep synthesizing and you get two voices
at once, the most jarring failure in voice UX. Barge-in is an UPSTREAM signal:
it travels back toward the source and cancels the downstream turn.

This module models the interrupt with a controller the pipeline polls before
each stage. When `request_interrupt()` fires, the next poll returns True and the
pipeline raises `CancelledTurn`. The controller can be armed to fire at a chosen
stage, which is how the smoke + tests inject a deterministic mid-turn barge-in.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BargeInController:
    """Polled by the pipeline before each stage; fires once when triggered.

    `fire_before_stage` arms a deterministic interrupt: the controller returns
    True the first time the pipeline asks about that stage. `request_interrupt`
    arms an immediate one-shot interrupt (the live-call path: VAD fired).
    """

    fire_before_stage: Optional[str] = None
    _armed_immediate: bool = field(default=False, init=False)
    _fired: bool = field(default=False, init=False)
    interrupted_at: Optional[str] = field(default=None, init=False)

    def request_interrupt(self) -> None:
        """Live-call entry point: a new user frame arrived — cancel the turn."""
        self._armed_immediate = True

    def should_interrupt(self, stage_name: str) -> bool:
        """The poll the pipeline calls before running `stage_name`."""
        if self._fired:
            return False
        trigger = self._armed_immediate or (stage_name == self.fire_before_stage)
        if trigger:
            self._fired = True
            self.interrupted_at = stage_name
            return True
        return False

    def reset(self) -> None:
        self._armed_immediate = False
        self._fired = False
        self.interrupted_at = None


def run_turn_with_barge_in(pipeline, user_text: str, controller: BargeInController):
    """Run a turn under a barge-in controller.

    Returns `(result, cancelled, interrupted_at)`. On barge-in the in-flight
    turn is abandoned (its TTS never reaches transport) — exactly the behavior a
    real agent needs so it stops talking the instant the user does.
    """
    from pipeline import CancelledTurn

    try:
        result = pipeline.run_turn(
            user_text,
            interrupt_check=controller.should_interrupt,
        )
        return result, False, None
    except CancelledTurn:
        return None, True, controller.interrupted_at
