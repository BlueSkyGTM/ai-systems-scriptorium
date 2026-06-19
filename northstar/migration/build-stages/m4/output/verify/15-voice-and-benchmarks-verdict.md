# VERIFY verdict — L15 Voice Agents & Benchmark Literacy

**Lesson:** `build-stages/m4/output/author/15-voice-and-benchmarks.md`
**Verifier:** Sonnet VERIFY subagent (ch04 thin, M4)
**Date:** 2026-06-19
**Overall verdict: PASS (edited in place).** All 7 markers resolved; every benchmark number verified against the source file and the highest-risk ones independently corroborated. One contamination figure reworded for precision (32.67% of *resolved instances*, not "patches"). No markers remain. STYLE clean. This is the benchmark-dense lesson — every number was checked individually.

## Claim ledger (every benchmark / vendor number)

| Claim | Source check | External corroboration | Verdict |
|---|---|---|---|
| Voice latency budget **~450–600ms end-to-end** | aefs Ph14 §22 — exact "~450–600ms end-to-end" | Voice-AI latency literature: human-conversation gold standard ~500ms; production targets sub-500ms→~800ms; sub-500ms TTFT the goal. 450–600ms sits squarely in band | **PASS** |
| Partial / streaming audio as the default | aefs Ph14 §22 — "partial audio as the default" | (standard streaming-ASR practice) | **PASS** |
| Pipeline **VAD → STT → LLM → TTS → transport** | aefs Ph14 §22 — exact | (standard cascade) | **PASS** |
| Pipecat = frame-based Python pipeline, **DOWNSTREAM/UPSTREAM** frame flow | aefs Ph14 §22 — exact "DOWNSTREAM/UPSTREAM flow" | Pipecat docs URL 404'd; framework is well-documented as frame-based with directional frames; source-confirmed | **PASS** |
| LiveKit Agents over **WebRTC**; **`MultimodalAgent`** (direct audio) vs **`VoicePipelineAgent`** (STT→LLM→TTS cascade); **semantic turn detection** | aefs Ph14 §22 — exact | LiveKit docs confirm: MultimodalAgent = direct audio via realtime API; VoicePipelineAgent = STT/LLM/TTS pipeline; LiveKit custom open-weights turn-detection model atop VAD; WebRTC transport | **PASS** |
| Headline numbers recapped: 38.1% OSWorld, 59.8% SWE-bench, 70% Online-Mind2Web | carried from L14 (all PASS there) | see L14 verdict | **PASS** (consistent w/ L14) |
| **SWE-bench** = real GitHub issues, gated by **FAIL_TO_PASS** | aefs Ph14 §19 — exact | (SWE-bench paper; standard) | **PASS** |
| **SWE-bench Verified** = human-curated **500-task** subset; saturated | aefs Ph14 §19 — exact "Verified 500-task subset" | (widely documented) | **PASS** |
| **SWE-bench+ 32.67% solution leakage** | aefs Ph14 §19 + Ph15 §09 — exact "32.67%" | SWE-bench+ paper (arXiv 2410.06992): "Answer Leak, where in **32.67%** of the resolved instances, the solutions were outlined directly in the issue reports or comments" — exact | **PASS — reworded** ("patches" → "resolved instances … spelled out in the issue report or its comments") for fidelity to the paper's claim |
| **161 of 500 Verified tasks need a 1–2 line change** | aefs Ph15 §09 — exact "161 of 500 Verified tasks need only a 1–2 line change" | (Epoch/SWE-bench analysis class; source-confirmed) | **PASS** |
| **SWE-bench Pro** = 10+ line changes, sits at **23–59%** | aefs Ph15 §09 — exact "SWE-bench Pro (10+ lines) sits at 23–59%" | source-confirmed | **PASS** |
| **GAIA** — humans **~92%** / AI **~15%**, three difficulty levels | aefs Ph14 §19 — exact "simple for humans 92%, hard for AI 15%, three difficulty levels" | (GAIA paper; standard) | **PASS** |
| **WebArena** — **812** tasks, four self-hosted web apps, execution-based eval | aefs Ph14 §20 — exact "812 long-horizon tasks across four self-hosted web apps, execution-based eval" | (WebArena paper; standard) | **PASS** |
| **OSWorld** — **369** real tasks, Ubuntu/Windows/macOS, **1920×1080** free-form keyboard/mouse | aefs Ph14 §20 — exact "369 real tasks across Ubuntu/Windows/macOS … 1920×1080" | OSWorld site + paper (arXiv 2404.07972): "benchmark of **369** computer tasks … Ubuntu, Windows, and macOS"; execution-based eval — exact | **PASS** |

## Markers resolved
7 `[verify:]` markers removed → clean prose:
1. Latency budget ~450–600ms · 2. Pipecat frame-based/DOWNSTREAM-UPSTREAM · 3. LiveKit WebRTC/MultimodalAgent vs VoicePipelineAgent/semantic turn detection · 4. SWE-bench/Verified 500/SWE-bench+ 32.67% · 5. SWE-bench Pro / 161-of-500 · 6. GAIA · 7. WebArena · 8. OSWorld.
(Five inline + the SWE-bench+/SWE-bench-Pro pair.) Verified count remaining in file: **0**.

## Defects found + fixed
- **SWE-bench+ contamination wording.** Draft said "32.67% of patches leaked their solutions." The paper's exact claim is 32.67% of *resolved instances* had **solution leakage** (the answer was spelled out in the issue/comments) — a subset of the 63.75% "suspicious" total. Reworded to "32.67% of resolved instances had their solutions leaked … spelled out in the issue report or its comments." Number unchanged; framing now precise. (Note: 31.08% additional were suspicious due to weak tests — not cited in lesson, correctly so for THIN scope.)
- No other numeric defects: 500, 161, 23–59%, 92%, 15%, 812, 369, 1920×1080, ~450–600ms all verified exact.

## FLAGGED
- None blocking. The latency budget (~450–600ms) is a range claim consistent with current literature; SWE-bench Pro 23–59% is a moving leaderboard range but source-anchored and presented as a range. Both are appropriately hedged. No softening required.

## STYLE result — PASS
- H1 present (`# Voice Agents & Benchmark Literacy`). ✓
- Seam lead: opens on the two skills + the latency clock; no throat-clearing. ✓
- One `## Core concepts` block (4 propositions, in voice). ✓
- Handoff div present, inspection-only ("no build here; the voice assistant is a Module 6 artifact"). ✓ Correct — exercise did not become a full build.
- No template ending; lands on a reframe ("know them before the number leaves your mouth"). ✓
- Acronyms: VAD/STT/TTS all expanded on first use in the pipeline bullet list; WebRTC used as standard proper noun. ✓
- THIN framing + "voice agent is a M6 artifact" preserved; benchmark-literacy discipline intact. ✓
- Voice unchanged. ✓
