# Voice Agents & Benchmark Literacy

Two skills round out this chapter, and neither is a build. The first is reading a voice agent's architecture against a latency budget so brutal it shapes every design choice. The second is reading a benchmark number well enough not to be fooled by it — including the ones you've been quoting all chapter. Both are thin here; the voice agent itself is a Module 6 artifact.

## Voice: a pipeline ruled by a latency budget

A voice agent is its own production category, and what makes it hard is not the language model — it's the clock. Conversation feels broken past a certain delay; the working target is **roughly 450–600ms end-to-end**, mouth to ear, through every stage. [verify: Pipecat / LiveKit — voice agent latency budget ~450–600ms end-to-end] That budget is the spec everything else bends to, and it forces **partial audio as the default**: the agent processes speech in streaming fragments rather than waiting for a complete utterance, because waiting blows the budget before the model has even started.

The standard architecture is a cascade of stages, each spending milliseconds you don't have to spare:

```
mic → VAD → STT → LLM → TTS → transport → speaker
```

- **VAD** — Voice Activity Detection, deciding when the user is actually speaking versus pausing.
- **STT** — Speech-to-Text, turning audio into tokens.
- **LLM** — the model, generating the reply.
- **TTS** — Text-to-Speech, turning the reply back into audio.
- **transport** — streaming the audio to the user, typically over WebRTC for low-latency delivery.

Two frameworks anchor the space:

**Pipecat** gives you this as a frame-based Python pipeline. Audio and text flow through the stages as frames with explicit DOWNSTREAM and UPSTREAM direction, so you can reason about and instrument each hop. [verify: Pipecat — frame-based pipeline, VAD → STT → LLM → TTS → transport, DOWNSTREAM/UPSTREAM]

**LiveKit Agents** bridges models to users over WebRTC and offers two shapes you choose between: `MultimodalAgent`, which sends audio **directly** to a multimodal model and skips the STT/TTS hops, versus `VoicePipelineAgent`, the explicit STT → LLM → TTS **cascade**. It adds semantic turn detection — a model that decides whether the user has finished a thought, not whether they merely paused for breath. [verify: LiveKit Agents — WebRTC, MultimodalAgent (direct audio) vs VoicePipelineAgent (cascade), semantic turn detection]

The direct-vs-cascade choice is the one to hold onto. Direct audio cuts two hops and saves latency but hands control to one model; the cascade costs milliseconds but lets you swap a better STT or TTS independently and instrument each stage. That trade — fewer milliseconds against more control — is the recurring decision of voice engineering, and it's the heart of **Module 6 artifact 03**, where you build a voice assistant against this budget. Here you only need to read the pipeline and see where the time goes.

## Benchmark literacy: read the number before you quote it

This chapter has thrown benchmark numbers at you — 38.1% on OSWorld, 59.8% on SWE-bench, 70% on Online-Mind2Web. A score is a compressed claim, and decompressing it before you repeat it is a core engineering skill. Three questions unpack any benchmark: what's in it (**composition**), did the model already see the answers (**contamination**), and what does it **not** measure.

**SWE-bench** runs real GitHub issues and gates a fix by whether the repo's tests flip from failing to passing — FAIL_TO_PASS. **SWE-bench Verified** is a human-curated 500-task subset, and it is **saturated**: top scores cluster near the ceiling, so a high number there says little about hard work. The reasons are two, and both are composition facts. First, contamination: SWE-bench+ analysis found **32.67% of patches leaked their solutions** into the model's reach. [verify: SWE-bench / SWE-bench Verified (500 tasks) / SWE-bench+ — 32.67% solution leakage] Second, triviality: **161 of the 500 Verified tasks need only a 1–2 line change**. The harder signal lives in **SWE-bench Pro**, which requires 10+ line changes and sits at **23–59%** — a wide gap that real-world quality hides in, behind the saturated headline. [verify: SWE-bench Pro — 10+ line changes, 23–59%; 161/500 Verified tasks are 1–2 line changes] When someone quotes a SWE-bench score, ask which one.

Three more benchmarks, each measuring a different slice and each silent on the rest:

- **GAIA** — general assistant tasks calibrated so humans score ~92% and AI ~15%, across three difficulty levels. It measures whether an agent can chain tools and reasoning on tasks easy for people; it says nothing about coding or GUI control. [verify: GAIA — humans ~92%, AI ~15%, three difficulty levels]
- **WebArena** — 812 long-horizon tasks across four self-hosted web apps, scored by execution (did the task get done), not by string match. It measures web navigation; it doesn't touch desktop apps or code. [verify: WebArena — 812 tasks, four self-hosted web apps, execution-based eval]
- **OSWorld** — 369 real tasks across Ubuntu, Windows, and macOS, driven by free-form keyboard and mouse on 1920×1080 screenshots. It measures full-desktop computer use — and it is where the grounding-vs-knowledge split from the last lesson was named. [verify: OSWorld — 369 tasks, Ubuntu/Windows/macOS, 1920×1080 free-form keyboard/mouse]

The discipline is the same for all of them: a benchmark measures one slice of one capability under one set of conditions, and the headline number tells you nothing about the slices it left out. Saturation means the test got easy, not that the problem got solved. Quote a number, and you've made a claim about composition and contamination whether you meant to or not — so know them before the number leaves your mouth.

## Core concepts

- A voice agent is governed by a ~450–600ms end-to-end latency budget that forces partial-audio streaming and shapes the whole architecture; the standard pipeline is VAD → STT → LLM → TTS → transport (over WebRTC).
- The recurring voice design choice is direct audio (MultimodalAgent — fewer hops, less latency, one model) versus the STT→LLM→TTS cascade (VoicePipelineAgent — more latency, but swappable stages and per-stage instrumentation).
- A benchmark score is a compressed claim; decompress it by composition (what's in it), contamination (did the model see the answers), and what it does not measure — SWE-bench Verified is saturated and partly contaminated (32.67% leakage), so the harder signal is SWE-bench Pro at 23–59%.
- GAIA, WebArena, and OSWorld each measure a different slice — tool-chaining, web navigation, full-desktop control — and a headline number says nothing about the slices a benchmark leaves out.

<div class="claude-handoff" data-exercise="exercises/module4/15-voice-and-benchmarks/">

**Inspect it in Claude Code** — no build here; the voice assistant is a Module 6 artifact. Sketch a voice pipeline's latency budget: lay out VAD → STT → LLM → TTS → transport, assign a plausible millisecond cost to each hop, and find where the ~450–600ms budget breaks. Then read one benchmark card from this lesson and write down its composition, its contamination story, and three things it does not measure. Open the repo and run the exercise for this lesson.

</div>
