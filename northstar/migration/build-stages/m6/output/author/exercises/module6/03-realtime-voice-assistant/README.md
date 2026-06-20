# Real-Time Voice Assistant

A streaming voice pipeline built against the one constraint that defines voice
agents: a hard latency budget. Mouth to ear, you have roughly **450-600 ms** —
through Voice Activity Detection, Speech-to-Text, the LLM, Text-to-Speech, and
transport — before the conversation starts to feel broken. This scaffold is the
pipeline, the measurement, and the operator surfaces that keep it honest.

## The business problem

Voice is the highest-bar interface a model ever sits behind. A chatbot can take
two seconds to answer and nobody minds. A voice agent that takes two seconds
sounds broken — people start talking over it, repeat themselves, hang up. The
budget is the spec everything else bends to, and it forces two design choices
the moment you start: process speech in **streaming fragments** (waiting for a
full utterance blows the budget before the model starts), and handle **barge-in**
(when the user talks over the agent, the agent must stop *now*, or you get two
voices at once). Build a voice agent and you are not building a smarter model —
you are building a clock you cannot miss.

## What this is

A composable, **Pipecat-shaped** frame pipeline that runs standalone on the
Python standard library. Frames flow through stages with an explicit direction
(DOWNSTREAM toward the speaker, UPSTREAM for control like an interrupt), exactly
as Pipecat moves audio and text. Each stage is a `FrameProcessor` you can swap
without touching the rest of the pipeline — that is the **portable seam**.

```
user text -> VAD -> STT -> LLM -> TTS -> transport -> reply audio
             (the cascade; swap any STT/TTS provider behind the stage interface)
```

| File | Role |
|------|------|
| `pipeline.py` | The frame model + `VoicePipeline` (the Pipecat-shaped chain) |
| `stages/mock_vad.py` | Voice Activity Detection (mock; Silero opt-in) |
| `stages/mock_stt.py` | Speech-to-Text (mock; Deepgram opt-in) |
| `stages/mock_llm.py` | The reply (mock deterministic; Anthropic/OpenAI opt-in) |
| `stages/mock_tts.py` | Text-to-Speech (mock; Cartesia opt-in) |
| `stages/transport.py` | The final hop (mock; WebRTC/Daily opt-in) |
| `latency.py` | Per-stage + end-to-end measurement and the **enforced budget gate** |
| `barge_in.py` | Interrupt handling — a new user frame cancels the in-flight turn |
| `smoke.py` | Runs a full turn, prints the budget, proves the gate bites + barge-in cancels |
| `tests/test_smoke.py` | Asserts: turn completes, report sums + gate flags a blown budget, barge-in cancels |

## Run it (no audio, no cloud, no keys)

```bash
python smoke.py            # full turn + latency budget + gate + barge-in demo
python -m pytest tests/    # the BUILD->TEST gate (9 tests)
# stdlib fallback if pytest is not installed:
python -m unittest discover -s tests
```

Latency is **simulated** (configurable per-stage milliseconds), so the gate is
deterministic regardless of how fast your machine is. There is no audio
hardware, no network, and no provider key on this path.

## The operator surfaces (what you drive in M8)

- **The latency budget is an enforced gate.** `latency.py` sums the per-stage
  cost and `enforce()` *raises* on a blown budget instead of shipping a laggy
  turn. The budget is config (`VOICE_BUDGET_MS`), not a constant baked in code.
- **Barge-in is a kill-switch for the turn.** `barge_in.py` polls a controller
  before each stage; a new user frame cancels the in-flight TTS turn so the
  agent stops talking the instant the user does.
- **The turn is observable.** Every stage records its latency into a ledger you
  can read off the finished turn — the same data a production tracer would emit.

## Extend to real Pipecat / LiveKit

Every real provider is behind a **guarded import** (`try_real_*` in each stage)
so nothing breaks if it is missing:

1. `pip install pipecat-ai` (and the provider extras you need).
2. Copy `.env.example` to `.env` and fill in `DEEPGRAM_API_KEY`,
   `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`), `CARTESIA_API_KEY`.
3. Swap a mock stage for the real service the stage's `try_real_*` returns —
   the `VoicePipeline` chain does not change. That is the portable seam paying
   off: provider choice is a stage swap, not a rewrite.

The direct-vs-cascade trade (LiveKit's `MultimodalAgent` sends audio straight
to a multimodal model and cuts two hops; `VoicePipelineAgent` is the explicit
STT -> LLM -> TTS cascade you can instrument and swap) is the recurring decision
of voice engineering. This scaffold is the cascade, because the cascade is the
one you can measure stage by stage.

## Done when

`python smoke.py` exits 0 and prints a within-budget turn, a blocked
blown-budget turn, and a cancelled barge-in; `python -m pytest tests/` is green.
The artifact ships `outputs/skill-realtime-voice-assistant.md`.
