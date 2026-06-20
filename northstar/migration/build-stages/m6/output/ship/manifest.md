# M6 SHIP manifest — Module 6, Agent Artifacts

Shipped 2026-06-19. AUTHOR → VERIFY → **BUILD→TEST** → SHIP complete (the code gate's first module).
`mdbook build` PASS (M1–M6 live). 4 portfolio artifacts, each guide + a runnable, gate-passing scaffold.

## What shipped
- 4 build-guide chapters → `src/module6/` (01 terminal-coding-agent, 02 production-rag-chatbot, 03 realtime-voice-assistant, 04 issue-to-pr-agent).
- 4 runnable scaffolds → `exercises/module6/<artifact>/` (each: smoke.py + tests + README + `.env.example` + `outputs/skill-*.md`), all passing the offline BUILD→TEST gate (4/4 smoke, 24/24 tests).
- `exercises/module6/_prereqs/CLOUD-SETUP.md` — the dry-run-first prereqs (local default, cloud opt-in, scoped-creds/budget/teardown guardrails).
- `src/SUMMARY.md` M6 section: Overview + 4 artifacts. `src/module6/README.md` rewritten to the 01–04 order + the runs-not-renders framing.
- `.gitignore`: `__pycache__/`, `.pytest_cache/`, `.env` (scaffold caches + secrets never committed; `.env.example` is).

## Pipeline records
- BUILD→TEST gate: `build-stages/m6/output/build-test/SUMMARY.md` (Opus re-ran all 4; 24/24 tests).
- VERIFY: `build-stages/m6/output/verify/SUMMARY.md` (4 guides PASS; guide-matches-scaffold confirmed; 4 defects fixed).

## Compounding forward (what M7 imports)
- 01 → the **coder node** of the SWE team · 02 → the **knowledge/retrieval service** · 03 → the **human-interface channel** · 04 → the **autonomous-execution pattern**.
- Every artifact exposes the **operator surfaces** (budget, kill-switch, audit/verify gate, acceptance eval) the M8 student operates.

## Carried / antilibrary
- GPT-from-scratch + distributed-training stay cut (antilibrary M6–M8 line, confirmed).
- **Next: M7 (Multi-Agent Artifacts)** — compose the M6 agents into governed teams (05 research, 06 K8s, 10★ governed fleet FINALE), wrapping them in the M4 fleet layer; **elevate, don't author** (DRY). Same AUTHOR→VERIFY→BUILD→TEST→SHIP. Write `build-stages/m7/PLAN.md` first.
