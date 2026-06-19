# Computer-Use, Coding & Voice (Thin Teaching)

> **Migrated from** `aefs-module3-agent-engineering` (Ph14 19–22, Ph16 advanced) + `asdg-module3-tool-use-
> computer-agents` (Ch17). **Track-H ruling: teach light here, prove in the artifact.** The heavy realization
> lives in the artifacts these seed (coding → M6 artifact 01; voice → M6 artifact 03).

## Computer-use agents

Three production models, all vision-based: Claude (screenshot in, keyboard/mouse out, no accessibility API),
OpenAI CUA/Operator, Gemini Computer Use (browser-only, per-step safety). The shared contract: **screenshots,
DOM text, and tool outputs are untrusted input; only direct user instructions count as permission.** The two
failure modes: GUI grounding (pixel→element) and operational knowledge (the menu/shortcut tail).

## Coding agents

Scaffolding now matters as much as the model (same model: 43% → 60% across harnesses). OpenHands (CodeAct —
execute Python in a sandbox instead of JSON tool calls), Aider, Cline. Methodological caveat: SWE-bench
Verified is saturated; real-world difficulty hides in SWE-bench Pro (10+ line changes, 23–59%).

## Voice agents

A first-class production category with brutal latency budgets (~450–600ms end-to-end), partial audio as
default. Pipecat (frame-based Python pipeline: VAD → STT → LLM → TTS → transport); LiveKit Agents (WebRTC,
`MultimodalAgent` direct-audio vs `VoicePipelineAgent` cascade) with semantic turn detection.

## Benchmarks (know what they don't measure)

SWE-bench / SWE-bench Verified / Pro (contamination story), GAIA, WebArena, OSWorld — know composition,
contamination, and what each does *not* measure before quoting a number.

**Why thin:** these are advanced single-agent applications. You learn *how each works* here; you *build* one
in the artifacts (the coding agent and voice assistant are M6 artifacts).
