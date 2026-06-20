# VERIFY verdict — 03 Real-Time Voice Assistant

Artifact: `build-stages/m6/output/author/03-realtime-voice-assistant.md`
Scaffold: `build-stages/m6/output/author/exercises/module6/03-realtime-voice-assistant/`
Gate: guide-prose correctness (claims + STYLE + guide-matches-scaffold). Code already passed BUILD→TEST.
Verdict: **PASS (fixes applied in place)**

## Markers resolved

| Marker (location) | Resolution | Source |
|---|---|---|
| `[verify: 450–600 ms working-budget figure …]` (business problem) | Resolved to clean prose: "the budget Module 4 named, and the one the cascade is built to defend." Kept as the working target; LiveKit corroborates the regime (direct path 320–800 ms; cascade adds hops). No precise external source pinned. | carried from M4 ch15; LiveKit voice-agent docs/blog. |
| `[verify: Pipecat is a Python frame-pipeline framework with Frame/FrameProcessor/Pipeline/PipelineTask/PipelineRunner]` (capability) | VERIFIED + rewritten naming all five classes. | reference-server.pipecat.ai (pipecat.pipeline.pipeline.Pipeline, .runner.PipelineRunner, .task.PipelineTask, pipecat.processors.frame_processor.FrameProcessor); FrameDirection DOWNSTREAM/UPSTREAM confirmed. |
| `[verify: SileroVADAnalyzer import path]` | VERIFIED → `pipecat.audio.vad.silero` folded into prose. | WebSearch pipecat reference + examples. |
| `[verify: DeepgramSTTService import path + constructor]` | VERIFIED → `pipecat.services.deepgram.stt`. | reference-server.pipecat.ai/.../services/deepgram/stt.html. |
| `[verify: AnthropicLLMService import path + model id]` | VERIFIED path `pipecat.services.anthropic.llm` (matches `pipecat.services.openai.llm` pattern + scaffold). Model id NOT hardcoded — guide now says read current id from env, pick a fast Sonnet for latency. | pipecat services pattern; build-progress model-id gotcha. |
| `[verify: CartesiaTTSService import path]` | VERIFIED → `pipecat.services.cartesia.tts`. | pipecat reference + scaffold. |
| `[verify: Pipecat WebRTC/Daily transport import path]` | VERIFIED → `DailyTransport` (scaffold uses `pipecat.transports.services.daily`). | scaffold `stages/transport.py`; pipecat docs. |

Zero markers remain in the guide (grep clean).

## Claim ledger

- **Pipecat core: `Frame`, `FrameProcessor`, `Pipeline`, `PipelineTask`, `PipelineRunner`, frame direction DOWNSTREAM/UPSTREAM** — VERIFIED (pipecat reference server). Matches scaffold `pipeline.py` (`FrameDirection`, `FrameProcessor.process -> Optional[Frame]`, `try_real_pipecat()` importing all four from the real paths).
- **Service import paths** (VAD/STT/LLM/TTS/transport) — all VERIFIED (above), all match the scaffold `try_real_*` helpers.
- **Seam = pipeline stage; `FrameProcessor` with `process(frame) -> Frame | None` + declared latency** — VERIFIED. Guide code block matches scaffold base class (`name: str`, `sim_latency_ms: float`, `process(frame) -> Optional[Frame]`).
- **~450–600 ms mouth-to-ear budget** — accepted as the established voice-UX working budget (carried from M4); scaffold `latency.py` defaults sum to 500 ms inside a 600 ms `DEFAULT_BUDGET_MS`. Consistent.
- **LiveKit alternative (`MultimodalAgent` direct vs `VoicePipelineAgent` cascade)** — VERIFIED these are real LiveKit Agents abstractions (LiveKit docs). Now named in the guide's seam section, matching the scaffold README/skill. See FLAGGED for a currency nuance.
- **BUILD→TEST: `smoke.py` exit 0 (within-budget turn, blown-budget block, barge-in cancel); `pytest tests/` green (9 tests); stdlib `unittest` fallback** — VERIFIED. `smoke.py` runs the three scenarios; `tests/test_smoke.py` has exactly 9 tests (TurnCompletes 2 + LatencyGate 4 + BargeIn 3) and is unittest-based so `unittest discover` works. Matches README "9 tests".

## Guide-matches-scaffold — drift found and FIXED

1. **LiveKit/numpy mislabeled as guarded imports.** Guide BUILD→TEST said "Every third-party import — Pipecat, LiveKit, the STT/TTS/LLM providers, numpy, audio libraries — is guarded… with a stdlib mock." Scaffold has **no LiveKit import and no numpy** anywhere in code; only Pipecat + Deepgram/Anthropic/Cartesia SDKs sit behind `try_real_*`. **FIXED**: rewrote to "Pipecat and the Deepgram, Anthropic, and Cartesia provider SDKs… behind a guarded `try_real_*` helper." Also fixed "What you build" ("real Pipecat/LiveKit providers" → "real Pipecat provider services").
2. **`VOICE_BUDGET_MS` overstated as code-read config.** Guide said "The budget is config (`VOICE_BUDGET_MS`), not a constant." `latency.py` parameterizes the budget (`budget_ms` arg, `DEFAULT_BUDGET_MS=600`) but does not `os.environ`-read `VOICE_BUDGET_MS`; that name lives only in `.env.example`. **FIXED**: "The budget is a parameter, surfaced as `VOICE_BUDGET_MS` in `.env.example`, not a constant baked into the code."
3. **LiveKit comparison promised but not named in prose.** Done-when promises "the cascade-vs-direct trade named as the design comparison"; the guide named the trade but not LiveKit's two shapes. **FIXED**: added `MultimodalAgent` (direct) vs `VoicePipelineAgent` (cascade) to the seam section, matching scaffold README/skill.

Otherwise confirmed: pipeline stages (`mock_vad/stt/llm/tts` + transport), `VoicePipeline`, `measure`/`enforce` latency layer, `BargeInController` polled before each stage, file names, and the offline stdlib-only gate all match.

## STYLE (full read)

- H1 present; seam-style two-paragraph lead (latency is the problem; build to the clock); `## What you build` + `## Core concepts` precede the handoff; `<div class="claude-handoff">` present with correct `data-exercise` path.
- Second person, present tense, one blunt confident voice. No banned template ending; endings vary (reframe, cost, consequence). Genuine voice present ("a clock you cannot miss," "the agent monologues over a person").
- Fix applied: expanded acronym-as-jargon **IVR** → "phone menu" (it was unexpanded; cheaper to gloss than expand for one passing use). VAD/STT/LLM/TTS are expanded on first use in the cascade bullets. WebRTC left (standard).
- Tightened a "models the pipeline / models the system" echo introduced when resolving the Pipecat marker.

## FLAGGED (non-blocking)

- **LiveKit 1.0 currency nuance.** `VoicePipelineAgent` and `MultimodalAgent` were the pre-1.0 named abstractions; LiveKit Agents 1.0 unified both under `AgentSession`. The guide presents them as the conceptual cascade-vs-direct trade (which still holds and is how the scaffold README/skill teach it), not as the current top-level API. Acceptable as a teaching framing; if a future pass wants strict-current API names, update guide + scaffold README + skill together. Low priority.
- **`ANTHROPIC_MODEL` asymmetry across the two M6 artifacts.** Artifact 02's `chatbot.py` reads `ANTHROPIC_MODEL` from env; artifact 03's `stages/mock_llm.py` `try_real_llm()` constructs `AnthropicLLMService(api_key=...)` without a model id and `.env.example` documents only `ANTHROPIC_API_KEY` (not `ANTHROPIC_MODEL`). The guide prose was corrected to avoid asserting the scaffold reads `ANTHROPIC_MODEL` (it says "read the current model id from the environment" as guidance, not a scaffold claim). A consistency tidy — add `ANTHROPIC_MODEL` to 03's `.env.example` and `try_real_llm()` — is a code change, out of scope for this prose-VERIFY gate.
