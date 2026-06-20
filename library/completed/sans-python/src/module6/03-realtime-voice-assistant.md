# Real-Time Voice Assistant

A chatbot can think for two seconds and nobody minds. A voice agent that thinks for two seconds sounds broken; the caller talks over it, repeats the question, hangs up. Voice is the one interface where the model is the easy part and the clock is the problem, and this artifact is about building to the clock.

You read the architecture in Module 4: the VAD → STT → LLM → TTS → transport cascade, ruled by a mouth-to-ear budget of roughly 450–600 ms. Now you build it; a streaming pipeline you can measure stage by stage, a budget you enforce instead of hope for, and barge-in handling that stops the agent the instant the user speaks.

## The Business Problem

A voice agent answers the phone, books the appointment, takes the order, handles the support call, and the bar it has to clear is not intelligence. It is latency. Conversation has a rhythm, and past a certain delay that rhythm breaks: the human starts talking into the silence, the agent starts replying into the human, and you get two voices at once. The working target is roughly **450–600 ms end to end**, mouth to ear, through every stage; the budget Module 4 named, and the one the cascade is built to defend.

That budget is the spec everything bends to, and it forces two design choices before you write a line. First, **stream in fragments**: wait for a complete utterance and you have spent your budget before the model starts, so the pipeline processes speech as it arrives. Second, **handle barge-in**: when the user talks over the agent, the agent must stop synthesizing *now*. Keep going and the worst failure in voice UX plays out; the agent monologues over a person trying to interrupt it.

Strip the romance off and the job is narrow. You are not building a smarter model. You are building a clock you cannot miss, with a pipeline whose every hop is a withdrawal from a budget of half a second.

## Capability and One Stack

The capability is **streaming under a hard latency budget**: VAD → STT → LLM → TTS, wired through a transport, with barge-in. The reference stack, one concrete choice, is **Pipecat**; an open-source Python framework for real-time voice agents. It models the system as a `Pipeline` of `FrameProcessor` stages that pass `Frame`s between them, driven by a `PipelineTask` and a `PipelineRunner`. The scaffold reproduces that shape in the standard library so you can run it offline; real Pipecat swaps in behind the same seam.

That shape is the one you want to reason about: audio and text flow through the stages as **frames** with an explicit direction; DOWNSTREAM toward the speaker, UPSTREAM for control like an interrupt. Each `FrameProcessor` consumes a frame and emits the next. The reference cascade maps one provider per stage:

- **VAD**; Voice Activity Detection decides when the user is speaking versus pausing (Silero via `SileroVADAnalyzer`, from `pipecat.audio.vad.silero`).
- **STT**; Speech-to-Text turns audio into text (Deepgram via `DeepgramSTTService`, from `pipecat.services.deepgram.stt`).
- **LLM**; the model generates the reply, streaming (Anthropic via `AnthropicLLMService`, from `pipecat.services.anthropic.llm`). Pick the model for latency, not raw capability, a fast Sonnet over the flagship, and read the current model id from the environment rather than pinning one in code, so the choice doesn't go stale.
- **TTS**; Text-to-Speech turns the reply back into audio (Cartesia via `CartesiaTTSService`, from `pipecat.services.cartesia.tts`).
- **transport**; streams the audio to the user, over WebRTC for low latency (Pipecat's `DailyTransport`).

One stack, named, so the choices are honest. But the stack is not the lesson. The seam is.

## The Portable Seam

One interface carries this whole system: the **pipeline stage**. Every stage is a `FrameProcessor` with a single method, `process(frame) -> frame`, and a declared per-stage latency. Bind to that, and every provider becomes a drop-in swap.

```python
class FrameProcessor:
    name: str
    sim_latency_ms: float
    def process(self, frame: Frame) -> Frame | None: ...
```

The STT stage doesn't know whether the next stage is a real model or a mock; the LLM stage doesn't know whether its output goes to Cartesia or a stand-in. Swap Deepgram for Whisper, or Cartesia for ElevenLabs, and the cascade above and below the swapped stage does not move. That is the trade Module 4 named, and it is the choice LiveKit puts in front of you directly: its `MultimodalAgent` sends audio straight to one multimodal model and cuts two hops, while its `VoicePipelineAgent` is the explicit STT → LLM → TTS cascade. The cascade costs you milliseconds against the direct path, but it buys you a stage you can replace and a stage you can measure. This artifact is the cascade because the cascade is the one you can instrument.

The same seam is where real Pipecat plugs in. Every provider import sits behind a guarded `try_real_*` helper that returns the real service or `None` if it isn't installed. The mock stage and the real stage satisfy the same `process` contract, so the swap is config; install the package, set the key, hand the pipeline the real stage. The pipeline never learns the difference.

## The Build Sequence

Build it in the order the dependencies force, each step runnable before the next:

1. **The frame model**; `Frame` (type, direction, payload, a latency ledger in `meta`) and the `FrameProcessor` base class. This is the contract every stage speaks.
2. **The stages**; `mock_vad`, `mock_stt`, `mock_llm`, `mock_tts`, and a transport hop. Each is deterministic and adds a configurable *simulated* latency. The mock LLM returns a canned reply keyed off the transcript, so a turn is reproducible.
3. **The pipeline**; `VoicePipeline` chains the stages and drives one turn DOWNSTREAM, accumulating each stage's latency into a ledger on the finished turn.
4. **Latency measurement**; `measure(turn)` reads the ledger, sums it, and reports per-stage plus end-to-end against the budget.
5. **The gate**; `enforce(report)` raises on a blown budget instead of shipping a laggy turn. The budget is a parameter, surfaced as `VOICE_BUDGET_MS` in `.env.example`, not a constant baked into the code.
6. **Barge-in**; a controller the pipeline polls before each stage; a new user frame cancels the in-flight turn before it reaches the speaker.

The simulated latency is doing real work, not papering over a gap. A real STT call blocks on a network round trip you can't make on the smoke path; a configurable per-stage millisecond budget is what makes the *interesting* part, the measurement, the gate, the interrupt, testable in CI without audio hardware or a cloud account. Latency is the thing you are engineering, so latency is the thing the scaffold models directly.

## The Operator Surfaces

Module 8 hands the student the operator's chair: set the budget, watch the clock, hold the kill-switch. So this artifact exposes the surfaces the student will drive, and they are real, not decorative.

**The latency budget is an enforced gate.** This is the surface that defines the artifact. `latency.py` sums the per-stage cost off the finished turn and renders a budget table; every hop, the total, the verdict, the headroom. `enforce()` then *raises* when the total exceeds the budget. In production you wire that to drop the turn, fall back to a cheaper stage, or alert; anything but silently ship a turn that took 1.2 seconds. The budget is config, so the operator tightens it for a snappy phone menu and loosens it for a tolerant back-office assistant. The smoke harness blows one stage on purpose and confirms the gate catches it; a gate you can't watch bite is a gate you don't trust.

**Barge-in is the turn's kill-switch.** When VAD detects the user talking mid-turn, the agent must stop. The barge-in controller is polled before each stage; on an interrupt the in-flight turn is abandoned, its TTS never reaches transport, so the agent goes quiet the instant the user speaks. This is the operator surface that maps to the M8 kill-switch: a signal that halts work in flight, owned by something other than the model generating it.

**The turn is observable.** Every stage writes its latency into a ledger the finished turn carries, the same data a production tracer (OpenTelemetry GenAI spans, from Module 5) would emit. You can't fix a budget you can't see broken down by hop, so the breakdown is a first-class output, not a debug print.

## The BUILD→TEST Gate

The whole artifact runs on the Python standard library alone; no audio hardware, no cloud, no network, no GPU. `python smoke.py` wires the default cascade, drives one text-driven turn through it, prints the per-stage latency budget and the total, and asserts the turn is within budget. Then it re-runs with one stage's budget deliberately blown and confirms `enforce` raises. Then it fires a barge-in mid-turn and confirms the in-flight turn cancels. `python -m pytest tests/` asserts the three promises hold: a turn completes end to end with audio out, the latency report sums correctly and the gate flags a blown budget, and barge-in cancels the in-flight turn. A stdlib `unittest` fallback ships too, so the gate runs even where pytest isn't installed.

Every third-party import, Pipecat and the Deepgram, Anthropic, and Cartesia provider SDKs, sits behind a guarded `try_real_*` helper that returns the real service or falls back to the stdlib mock on the smoke path. Real services are opt-in through `.env`. Latency is simulated, so the gate is deterministic regardless of how fast the machine is. The gate you can run on a plane is the gate that runs in CI.

## Strong-Project Done-When

This clears the hireability bar: a real entry point you run from a shell, not a notebook; a README that frames the business problem, the brutal latency budget, before the code; evaluation in the form of a measured budget with a pass/fail gate, and the cascade-vs-direct trade named as the design comparison; tests covering the smoke path and both operator surfaces; a clean, versioned layout; and a shipped `outputs/skill-realtime-voice-assistant.md`. Done means the smoke gate is green and a stranger can read the README, run two commands, and watch a turn pass the budget, a blown turn get blocked, and a barge-in cancel mid-sentence.

## What Module 7 Reuses

This artifact is the **human-interface channel**. In Module 7 the voice pipeline stops being a standalone agent and becomes the way a person talks to a governed fleet in real time: it takes the caller's turn, hands the transcript to the team, and streams the team's answer back through TTS; under the same budget gate. The latency gate and the barge-in kill-switch carry forward unchanged, because they are exactly the operator surfaces the M8 student drives when the human interface is live. You are not rebuilding the pipeline in M7; you are wiring this channel onto a larger machine. That is the compounding the course promised: the single agent you ship here is how a human reaches the team you ship next.

## What You Build

A streaming voice pipeline against a hard latency budget: a Pipecat-shaped frame model, deterministic mock VAD/STT/LLM/TTS stages each carrying a simulated per-stage latency, a `VoicePipeline` that drives a turn through the cascade, a latency layer that measures per-stage and end-to-end against the budget and enforces it as a gate, and barge-in handling that cancels an in-flight turn; all passing an offline, stdlib-only BUILD→TEST smoke gate, with real Pipecat provider services opt-in behind guarded imports.

## Core Concepts

- A voice agent is engineered to a clock, not to intelligence: a ~450–600 ms mouth-to-ear budget forces streaming fragments and barge-in, and every pipeline hop is a withdrawal from that half-second.
- The portable seam is the pipeline stage, a `FrameProcessor` with one `process(frame)` method and a declared latency, so every STT/TTS/LLM/transport provider is a drop-in swap and the rest of the cascade never moves.
- The latency budget is an operator surface you enforce, not observe: `measure` sums the per-stage ledger and `enforce` raises on a blown budget, so a laggy turn is blocked instead of shipped.
- Barge-in is the turn's kill-switch: a new user frame mid-turn cancels the in-flight TTS so the agent stops talking the instant the user does; the same halt-work-in-flight control the M8 operator holds.

<div class="claude-handoff" data-exercise="exercises/module6/03-realtime-voice-assistant/">

**Build It in Claude Code**: Assemble the real-time voice assistant: a Pipecat-shaped frame model, the mock VAD → STT → LLM → TTS → transport cascade with a simulated per-stage latency, a `VoicePipeline` that drives one turn, a latency layer that measures and enforces the ~450–600 ms budget, and barge-in that cancels an in-flight turn. Prove it: `python smoke.py` exits zero printing a within-budget turn, a blocked blown-budget turn, and a cancelled barge-in, and `python -m pytest tests/` is green. Then swap a mock stage for real Pipecat behind the guarded import.

</div>
