# VERIFY verdict — L14 Computer-Use & Coding Agents

**Lesson:** `build-stages/m4/output/author/14-computer-use-and-coding-agents.md`
**Verifier:** Sonnet VERIFY subagent (ch04 thin, M4)
**Date:** 2026-06-19
**Overall verdict: PASS (edited in place).** All 7 markers resolved, all benchmark/vendor numbers verified against the source file and the highest-risk ones independently corroborated via WebFetch/WebSearch. Two figures softened for accuracy and flagged below. No markers remain in student-facing text. STYLE clean.

## Claim ledger (every benchmark / vendor number)

| Claim | Source check | External corroboration | Verdict |
|---|---|---|---|
| Claude `computer` tool: screenshot in, keyboard/mouse out, no accessibility API | asdg Ch17 §04; aefs Ph14 §21 — exact | (Anthropic computer-use; well-documented) | **PASS** |
| OpenAI CUA / Operator = RL-trained, vision-based | aefs Ph14 §21 ("RL-trained GPT-4o variant") | OpenAI CUA system card 403'd; Wikipedia confirms Operator, vision/browser automation | **PASS** |
| OpenAI CUA / Operator **OSWorld 38.1%** | aefs Ph14 §21 — exact "OSWorld 38.1%" | Wikipedia (OpenAI Operator): "38.1% on OSWorld benchmarks" — exact match | **PASS** |
| Gemini 2.5 Computer Use **~70% Online-Mind2Web** | aefs Ph14 §21 — "~70% Online-Mind2Web" | Google/DeepMind blog: "over 70%" headline; Browserbase harness measured **65.7%** on Online-Mind2Web specifically, 79.9% WebVoyager | **PASS — softened** ("roughly 70% … as of 2025"). See FLAG 1. |
| Gemini 2.5 Computer Use: per-step / inference-time safety service | aefs Ph14 §21 — "per-step safety service" | Google blog confirms verbatim: "out-of-model, inference-time safety service that assesses each action … before it's executed" | **PASS** |
| Gemini 2.5 Computer Use: browser scope | aefs Ph14 §21 — "browser-only" | Google blog: "primarily optimized for web browsers, but also demonstrates strong promise for mobile UI" — *not* strictly browser-only | **FIXED** — "browser-only" → "browser-focused". See FLAG 2. |
| OSWorld / OSWorld-G / OSWorld-Human **1.4–2.7× trajectory-efficiency gap** | aefs Ph14 §20 — exact "1.4–2.7× trajectory-efficiency gap" | OSWorld-Human paper (arXiv 2506.16042): agents take "1.4× more steps" (lower bound); range across agents extends to ~2.7× | **PASS** |
| GUI grounding vs operational knowledge failure split; OSWorld-G/-Human decompose grounding from planning | aefs Ph14 §20 — exact | OSWorld-Human paper confirms the human-trajectory split | **PASS** |
| Claude Sonnet 4.5 **43.2% SWE-agent v1 vs 59.8% Cline** (SWE-bench Verified) | aefs Ph15 §09 — exact "43.2% on SWE-agent v1 and 59.8% on Cline autonomous" | (Epoch AI leaderboard class; source-confirmed) | **PASS** |
| OpenHands (formerly OpenDevin) = most active open platform, **CodeAct** loop, executes Python in sandbox instead of JSON tool calls | aefs Ph15 §09 + asdg Ch17 §05 — exact | (OpenHands docs; well-documented) | **PASS** |
| Aider = git-backed local pairing agent | asdg Ch17 (Aider named); standard | (Aider docs; well-documented) | **PASS** |
| Cline = editor-integrated autonomous agent (the 59.8% harness) | aefs Ph15 §09 — Cline named as the 59.8% harness | (consistent w/ above) | **PASS** |

## Markers resolved
7 `[verify:]` markers removed → clean prose:
1. Claude `computer` tool · 2. OpenAI CUA/Operator OSWorld 38.1% · 3. Gemini ~70%/per-step safety · 4. OSWorld 1.4–2.7× gap · 5. Sonnet 4.5 43.2%/59.8% · 6. OpenHands CodeAct · 7. Aider + Cline.
Verified count remaining in file: **0**.

## Defects found + fixed
- **Gemini "browser-only" → "browser-focused"** — DeepMind's own blog says browser-primary with mobile-UI promise; "browser-only" overstated. Fixed.
- **Gemini "roughly 70%" kept but anchored "as of 2025"** — precise Online-Mind2Web Browserbase figure is ~65.7%; "70%+" is the headline/cross-bench number. "Roughly … as of 2025" is now defensible and time-stamped.
- **CUA acronym expansion** — "OpenAI CUA / Operator" → "OpenAI Computer-Using Agent (CUA) / Operator" (STYLE: expand acronym on first use).

## FLAGGED (age-sensitive, both softened — not blockers)
- **FLAG 1 — Gemini ~70% Online-Mind2Web.** Headline "70%+" is real (Google blog, cross-benchmark); the Online-Mind2Web-specific Browserbase number is ~65.7%. Lesson now says "roughly 70% … as of 2025." Monitor; replace with a single sourced figure if this lesson ever cites a precise number.
- **FLAG 2 — Gemini "browser-focused."** Model is browser-primary, not strictly browser-only (mobile-UI promise per DeepMind). Softened; accurate.

## STYLE result — PASS
- H1 present (`# Computer-Use & Coding Agents`). ✓
- Seam lead: first paragraph frames "the contract that governs both" — carries the untrusted-input thread forward; no throat-clearing. ✓
- One `## Core concepts` block (4 propositions, in voice). ✓
- Handoff div present, inspection-only ("no build here; the coding agent is a Module 6 artifact"). ✓ Correct — exercise did not become a full build.
- No template ending; ending lands on a reframe ("Here you only need the shape and the contract; there you make it run"). ✓
- Acronyms: DOM expanded ("The Document Object Model — the DOM"); CUA now expanded on first use. ✓
- Untrusted-input contract intact and emphasized. THIN framing + "build is the M6 artifact" framing preserved. ✓
- Voice unchanged. ✓
