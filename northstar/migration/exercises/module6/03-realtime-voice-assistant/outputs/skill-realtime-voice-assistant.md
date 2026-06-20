# Skill — Real-Time Voice Assistant

## What it proves

You can build a streaming voice pipeline against the constraint that defines the
category: a hard mouth-to-ear latency budget of roughly 450-600 ms. It
demonstrates that the load-bearing engineering in a voice agent is not the model
but the pipeline — a cascade of stages you can measure stage by stage, a budget
you enforce as a gate instead of hoping for, and barge-in handling that stops
the agent talking the instant the user does.

## What it does

Given a user turn, the pipeline:

1. **streams through the cascade** — VAD -> STT -> LLM -> TTS -> transport, each
   a `FrameProcessor` consuming one frame and emitting the next, frames carrying
   an explicit direction (DOWNSTREAM toward the speaker, UPSTREAM for control);
2. **measures every hop** — `latency.py` reads the per-stage cost off the
   finished turn, sums it, and reports it against the budget;
3. **enforces the budget** — `enforce()` *raises* on a blown budget instead of
   shipping a laggy turn; the budget is config, not a baked-in constant;
4. **handles barge-in** — a new user frame mid-turn cancels the in-flight TTS so
   two voices never overlap.

## How to invoke

```bash
python smoke.py            # full turn + latency budget + the gate + barge-in demo
python -m pytest tests/    # the BUILD->TEST gate: 9 tests
```

Offline, standard library only (pytest for the test runner; a stdlib `unittest`
fallback ships too). No audio hardware, no cloud, no provider key. Latency is
simulated so the gate is deterministic across machines.

## How to extend

- **Real STT/TTS/LLM:** every provider is behind a guarded import
  (`try_real_*` in each stage). `pip install pipecat-ai`, set the keys in `.env`
  (`DEEPGRAM_API_KEY`, `ANTHROPIC_API_KEY`, `CARTESIA_API_KEY`), and swap a mock
  stage for the real service — the `VoicePipeline` chain does not change.
- **Different provider:** write one `FrameProcessor` with a `process(frame)`
  method and the right `sim_latency_ms`. The pipeline is provider-agnostic.
- **Real transport:** swap `MockTransport` for a WebRTC/Daily transport; the
  pipeline reads an AUDIO_OUT frame, so the boundary swap is local to one stage.
- **Direct vs cascade:** this is the explicit cascade. To go direct (fewer hops,
  less latency, one multimodal model), collapse STT/LLM/TTS into one stage — the
  same trade LiveKit's `MultimodalAgent` vs `VoicePipelineAgent` exposes.

## The portable seam

The pipeline stages are the seam. Each is a `FrameProcessor` with one method:

- **the stage interface** — `process(frame) -> frame` plus a `sim_latency_ms` —
  makes every STT, TTS, LLM, and transport provider a drop-in swap;
- **the latency gate** — `measure(turn) -> report` and `enforce(report)` — makes
  "fast enough" a fact from a summed ledger, not a hope.

Swap a provider and the rest of the pipeline does not move. That is what lets
you trade a better STT or a cheaper TTS in and out as config.

## What M7 reuses

This is the **human-interface channel** of the Module 7 fleet — the way a person
talks to a team of agents in real time. M7 composes it: the voice pipeline takes
the user's turn, hands the transcript to the governed fleet, and streams the
fleet's answer back through TTS under the same budget gate. The latency gate and
the barge-in kill-switch carry forward unchanged — they are the operator
surfaces the M8 student drives when the human interface is live.
