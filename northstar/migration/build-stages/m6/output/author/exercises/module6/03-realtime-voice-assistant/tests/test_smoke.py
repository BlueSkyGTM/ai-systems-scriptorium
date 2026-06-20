"""Tests for the real-time voice assistant scaffold.

Run with: python -m pytest tests/   (pytest)
       or: python -m unittest discover -s tests   (stdlib fallback)

Both paths are stdlib-only: no audio, no cloud, no third-party providers. The
tests assert the three things the artifact promises:
  - a turn completes end to end (audio out);
  - the latency report sums correctly AND the gate flags a blown budget;
  - barge-in cancels the in-flight turn.
"""

from __future__ import annotations

import os
import sys
import unittest

# Make the package root importable whether run via pytest or unittest.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from barge_in import BargeInController, run_turn_with_barge_in  # noqa: E402
from latency import (  # noqa: E402
    BudgetExceeded,
    LatencyReport,
    enforce,
    measure,
)
from pipeline import FrameType, build_default_pipeline  # noqa: E402


class TestTurnCompletes(unittest.TestCase):
    def test_turn_produces_audio_out(self):
        pipeline = build_default_pipeline()
        result = pipeline.run_turn("hello there")
        self.assertIsNotNone(result.final_audio)
        # Every stage ran in order and is in the ledger.
        self.assertEqual(
            list(result.stage_latencies_ms.keys()),
            ["vad", "stt", "llm", "tts", "transport"],
        )

    def test_turn_is_deterministic(self):
        p1 = build_default_pipeline()
        p2 = build_default_pipeline()
        r1 = p1.run_turn("what are your hours")
        r2 = p2.run_turn("what are your hours")
        self.assertEqual(r1.final_audio.text, r2.final_audio.text)


class TestLatencyGate(unittest.TestCase):
    def test_report_sums_correctly(self):
        pipeline = build_default_pipeline(
            vad_ms=30, stt_ms=120, llm_ms=220, tts_ms=90, transport_ms=40
        )
        result = pipeline.run_turn("hello")
        report = measure(result, budget_ms=600)
        # 30 + 120 + 220 + 90 + 40 == 500.
        self.assertAlmostEqual(report.total_ms, 500.0, places=3)
        self.assertTrue(report.within_budget)
        self.assertAlmostEqual(report.headroom_ms, 100.0, places=3)

    def test_gate_passes_within_budget(self):
        pipeline = build_default_pipeline()
        result = pipeline.run_turn("hello")
        report = measure(result, budget_ms=600)
        # enforce returns the report unchanged when within budget.
        self.assertIs(enforce(report), report)

    def test_gate_flags_blown_budget(self):
        pipeline = build_default_pipeline(llm_ms=900.0)  # stall the model
        result = pipeline.run_turn("hello")
        report = measure(result, budget_ms=600)
        self.assertFalse(report.within_budget)
        self.assertLess(report.headroom_ms, 0)
        with self.assertRaises(BudgetExceeded):
            enforce(report)

    def test_report_render_contains_total(self):
        report = LatencyReport(
            stage_latencies_ms={"vad": 30, "stt": 120}, budget_ms=600
        )
        text = report.render()
        self.assertIn("TOTAL", text)
        self.assertIn("PASS", text)


class TestBargeIn(unittest.TestCase):
    def test_barge_in_cancels_in_flight_turn(self):
        pipeline = build_default_pipeline()
        controller = BargeInController(fire_before_stage="tts")
        result, cancelled, where = run_turn_with_barge_in(
            pipeline, "tell me a long story", controller
        )
        self.assertTrue(cancelled)
        self.assertIsNone(result)
        self.assertEqual(where, "tts")

    def test_no_barge_in_completes_normally(self):
        pipeline = build_default_pipeline()
        controller = BargeInController()  # never fires
        result, cancelled, where = run_turn_with_barge_in(
            pipeline, "hello", controller
        )
        self.assertFalse(cancelled)
        self.assertIsNotNone(result)
        self.assertIsNone(where)
        self.assertEqual(result.frames[-1].type, FrameType.AUDIO_OUT)

    def test_immediate_interrupt_cancels_before_first_stage(self):
        pipeline = build_default_pipeline()
        controller = BargeInController()
        controller.request_interrupt()  # VAD fired: user is talking again
        result, cancelled, where = run_turn_with_barge_in(
            pipeline, "hello", controller
        )
        self.assertTrue(cancelled)
        self.assertEqual(where, "vad")  # cancelled before the very first stage


if __name__ == "__main__":
    unittest.main()
