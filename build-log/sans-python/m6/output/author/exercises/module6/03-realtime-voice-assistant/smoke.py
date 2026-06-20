"""Smoke entry point — run a full text-driven turn through the voice pipeline.

`python smoke.py` (stdlib only):
  1. Wires the default VAD -> STT -> LLM -> TTS -> transport cascade.
  2. Drives one text-driven turn through it, printing the per-stage latency
     budget and the end-to-end total, and asserts it is within a configured
     sim budget (the enforced gate).
  3. Proves the gate bites: re-runs with one stage's budget deliberately blown
     and confirms `enforce` raises.
  4. Fires a barge-in mid-turn and confirms the in-flight turn cancels.

No audio hardware, no cloud, no network. Latency is simulated.
"""

from __future__ import annotations

import sys

from barge_in import BargeInController, run_turn_with_barge_in
from latency import BudgetExceeded, DEFAULT_BUDGET_MS, enforce, measure
from pipeline import build_default_pipeline


def run_good_turn(budget_ms: float = DEFAULT_BUDGET_MS) -> bool:
    print("=" * 50)
    print("1) Full turn through VAD -> STT -> LLM -> TTS -> transport")
    print("=" * 50)
    pipeline = build_default_pipeline()
    result = pipeline.run_turn("What are your hours?")
    report = measure(result, budget_ms=budget_ms)
    print(report.render())
    reply_audio = result.final_audio
    print(f"\n  reply audio: {reply_audio}")
    assert result.final_audio is not None, "turn did not produce audio out"
    enforce(report)  # raises if over budget
    print("  GATE: within budget -> turn ships.\n")
    return True


def run_blown_budget() -> bool:
    print("=" * 50)
    print("2) Gate must catch a deliberately blown budget")
    print("=" * 50)
    # LLM stalls at 900 ms — total ~1280 ms, well over the 600 ms budget.
    pipeline = build_default_pipeline(llm_ms=900.0)
    result = pipeline.run_turn("What are your hours?")
    report = measure(result, budget_ms=DEFAULT_BUDGET_MS)
    print(report.render())
    try:
        enforce(report)
    except BudgetExceeded as exc:
        print(f"  GATE: blocked as expected -> {exc}\n")
        return True
    raise AssertionError("blown budget was NOT caught by the gate")


def run_barge_in() -> bool:
    print("=" * 50)
    print("3) Barge-in mid-turn must cancel the in-flight turn")
    print("=" * 50)
    pipeline = build_default_pipeline()
    # User starts talking again just as the agent reaches TTS — cancel it.
    controller = BargeInController(fire_before_stage="tts")
    result, cancelled, where = run_turn_with_barge_in(
        pipeline, "Tell me a long story", controller
    )
    print(f"  cancelled: {cancelled}  (interrupted before stage: {where})")
    assert cancelled, "barge-in did NOT cancel the in-flight turn"
    assert result is None, "cancelled turn still produced a result"
    assert where == "tts", f"expected interrupt before tts, got {where}"
    print("  Agent stopped talking the instant the user did.\n")
    return True


def main() -> int:
    run_good_turn()
    run_blown_budget()
    run_barge_in()
    print("=" * 50)
    print("SMOKE PASS: turn completes, gate bites, barge-in cancels.")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
