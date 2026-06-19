# Authoring Progress

Live status of the lesson-authoring run (Handoff-2). Editor-in-chief = Opus; drafters = Sonnet subagents.
Resume from the first PENDING module. Each module: read `_dossier/moduleN.md` (keep/cut), the `src/moduleN/`
ingredients + `synthesis/source/moduleN/` depth, author finished lessons one-idea-each, self-Zinsser,
editor reviews against `STYLE.md`, update `src/SUMMARY.md`, remove superseded ingredient files.

## Status

| Module | Status | Lessons |
|--------|--------|---------|
| M1 Foundations | ✅ DONE | 01-dev-environment, 02-your-first-llm-call, 03-attention, 04-transformer-era-nlp, 05-retrieval-and-eval-foundations |
| M2 LLM Engineering | ✅ DONE | 01-prompt-engineering, 02-context-engineering, 03-rag-system, 04-advanced-rag, 05-evaluation, 06-structured-output-and-tools, 07-the-complexity-ladder |
| M3 Agent Foundations | ⬜ PENDING | reasoning-loops, tools-mcp, memory-state, frameworks-patterns, agent-workbench, typescript-entry |
| M4 Multi-Agent Systems | ⬜ PENDING | multi-agent-swarms, autonomous-safety, fleet-loop, computer-use-coding-voice |
| M5 Deploy & Perf | ⬜ PENDING | serving-inference, metrics-observability, ops-security-finops, perf-eng-depth, rust-entry |
| M6 Agent Artifacts | ⬜ PENDING | 4 artifacts (coding agent, RAG chatbot, voice, issue-to-PR) — apply M3, ship skill-*.md |
| M7 Multi-Agent Artifacts | ⬜ PENDING | 3 artifacts (research, K8s, governed fleet) — compose M6 agents |
| M8 Final Exam | ⬜ PENDING | M7 fleet builds the exam system; asdg Ch16 case studies as reference |

## Gotchas learned (save the next drafter time)

- **Model IDs:** the current Anthropic model is `claude-opus-4-8` (NOT 4-5). Verify any model ID / API shape
  via the `claude-api` skill, never from memory. First-call curl uses `anthropic-version: 2023-06-01`.
- **Numbering crosswalk:** `synthesis/source/moduleN/` uses OLD 5-module numbering; `src/moduleN/` + SUMMARY use
  NEW 8-module numbering. M3 source feeds new M3+M4; M5 source (capstone) feeds new M6+M7+M8. See `build/`... (now `MANIFEST` folded; the crosswalk lives in the dossiers + this note).
- **Voice anchors:** every drafter must read `STYLE.md` + `src/preface.md` + `src/README.md`. Em dashes are house style.
- **Granularity:** one idea per lesson; a chapter ingredient → 2–4 lessons (not 1 mega, not 12 atomic). Update SUMMARY to match; delete the ingredient file once its lessons are authored.
- **Threads to carry:** eval-driven development (M2→M5), versioning (M2/M5), safety distributed (M2/M3/M4/M5), complexity ladder (M2→M3).
- **mdbook** is not installed here; verify by checking SUMMARY links resolve to real files.
- **MS-Learn markers:** drafters insert `[MS-Learn: ...]` where a production pattern needs validation; the editor resolves them before the lesson ships (don't leave them in student-facing text).

## Follow-up polish (non-blocking)

- **M2 got a lighter editorial pass than M1.** M1: all 5 lessons full-read + corrected. M2: 1 of 7 full-read (`01-prompt-engineering`, clean) + structural sweep (all 7 have Core-concepts + handoff, no stray markers). A future pass should full-read M2's other 6.
- **`02/01-prompt-engineering.md`:** mentions "an assistant prefill you can seed" — assistant prefills now 400 on current Anthropic models (Opus 4.6+/Fable). Fine as a generic-LLM hierarchy concept, but reword so it doesn't read as a recommended Anthropic technique.
- **Module READMEs (Overview pages)** for M1/M2 were not re-read; confirm they don't still describe the old chapter structure.
- The top-level `northstar/CONTEXT.md` "AI Systems Engineering" / "LearnHouse" strings remain (flagged earlier; CONTEXT.md is archival).
