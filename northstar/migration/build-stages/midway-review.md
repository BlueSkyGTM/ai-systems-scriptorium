# Sans Python — Midway Build Review (M3 → M4 checkpoint)

Purpose: gut-check the proven build PROCESS and the back-half PLAN before committing to M4–M8.
This is a process + remaining-work review, not a single-feature plan.

## State (done)
- M1 Foundations, M2 LLM Engineering — shipped. M2 retroactively VERIFIED (assistant-prefill defect fixed).
- M3 Agent Foundations — AUTHORED + VERIFIED. 15-lesson hybrid; drafts + 15 per-lesson verdicts in
  `build-stages/m3/`. M3 SHIP (relocate `output/author` → `src/module3`, rewrite SUMMARY, `mdbook build`,
  mark DONE) is the one mechanical step still pending.

## Proven pipeline (the engine — full detail in build-progress.md → "Build pipeline")
Module-as-stage ICM: **AUTHOR → VERIFY → SHIP**. Opus orchestrates + reviews (the type-checker); Sonnet
subagents do the work, treating `STYLE.md` as a spec ("writing as code"). VERIFY scales to a fleet because
**the Microsoft Learn connector is available inside Sonnet subagents** — each resolves its own `[MS-Learn]`
markers, source-verifies, applies STYLE §8, and writes a per-lesson verdict. M3 caught real correctness
defects this way (wrong SDK shapes, a renamed package, an unverifiable GA date, an unsupported vendor claim).
Commit each stage to GitHub as it lands.

## Remaining plan (back half), per `_dossier/module4.md … module6-7-8.md` + directives
- **M4 Multi-Agent Systems:** multi-agent & swarms; autonomous & operational safety (kill switches, HITL);
  fleet & loop engineering (the M3 source `fleet-*`/`loop-*` files feed this); computer-use, coding & voice.
  Apply the same hybrid one-idea split + the locked STYLE (incl. §8). M4 is denser and safety-critical.
- **M5 Deploy & Performance Engineering:** serving/inference optimization, metrics/observability/rollout,
  ops (security/compliance/FinOps), perf-eng depth, **Rust entry** (the serving-layer language, point-of-use).
- **M6 Agent Artifacts** (single-agent, builds on M3 + the `agent-workbench-pack/`), **M7 Multi-Agent
  Artifacts** (teams composing M6 agents), **M8 Final Systems Exam** (the M7 fleet builds it). Artifacts
  compound M6 → M7 → M8; each is a portfolio piece solving a real business problem.

## Open decisions (the gut-check)
1. **Pipeline scaling.** Is AUTHOR→VERIFY→SHIP + Sonnet-fleet + connector-per-agent sound for M4–M8 as-is?
   What hardens it for denser/safety-critical M4 and for the M6–M8 build-artifact modules (which produce
   code, not just lessons)?
2. **M4 granularity.** Same hybrid one-idea split? M4 carries the multi-agent safety load (kill switches,
   HITL, fleet governance) — does the split/threading need adjustment?
3. **Directive #2 — artifact → platform bindings (M6–M8), the key open decision.** Each artifact must bind to
   a real platform (Azure AI Search / Azure OpenAI / AKS, Databricks Vector Search / MLflow, GitHub/CI,
   Pipecat/LiveKit), NOT toy abstractions. Tool-per-artifact binding is UNSELECTED.
4. **Sequencing.** Ship M3 before M4 starts, or proceed to M4 authoring with M3 SHIP deferred?

---

# GSTACK REVIEW REPORT (midway /autoplan)

Phases: CEO + Eng + DX (Design skipped — no UI). Voices: Claude subagent ×3 + Codex ×2 (CEO, Eng;
DX subagent-only). Consensus was strong — most findings appeared independently in 3+ voices.

## Consensus (high-confidence — flagged by multiple independent voices)

| Finding | Voices | Call |
|---|---|---|
| **SHIP M3 first, before any M4 authoring** | CEO, Eng, DX, Codex×2 (unanimous) | AUTO — `src/module3/` still holds the 6 OLD ingredient stubs; SUMMARY points at old slugs; M4 voice-anchoring + cross-refs would read stubs, not finished lessons. Do it now. |
| **Pipeline doesn't scale to M6–M8 code artifacts as-is — needs a runnable gate** | all 5 | AUTO — extend to AUTHOR→VERIFY→**BUILD→TEST**→SHIP for M6–M8: `tsc --noEmit` / `cargo check` / smoke-test-with-mocks. `mdbook build` proves *renders*, not *runs*. Lock the code-gate before M6 (not needed for M4/M5 prose). |
| **Non-Microsoft grounding gap** (Pipecat/LiveKit/OpenHands/Databricks not in MS Learn) | Eng, Codex×2, CEO | AUTO — extend the claim-authority map: name a primary-doc source per non-MS platform; VERIFY subagents resolve via **WebFetch** (works inside subagents, like the connector). Codex's matrix: tag every platform claim `mslearn / vendor-doc / spec / repo-example / local-smoke / unverified-cut`. |
| **Cloud creds/cost/secrets for M6–M8 exercises** | Eng, DX, Codex×2 | AUTO — dry-run-first: mocks/emulators/fake creds/`.env.example`/`plan`-only + a local `done-when` fallback per artifact; live cloud is opt-in "bring your own account" + budget caps + teardown. Add `exercises/module6/_prereqs/CLOUD-SETUP.md`. |
| **M4 needs its own locked plan** (count + threading + Ch03 split + fleet inclusion) | CEO, Eng, DX | AUTO — M4 is 4 dense tracks; lock a lesson count, dedupe the kill-switch/HITL threading (it lands in both Ch02 and Ch03), split Ch03 (11 fleet-*/loop-* files) into Fleet + Loop drafter turns, and write a POSITIVE inclusion list (the M3 exclusion rule inverts — M4 NEEDS those files). |
| **M4 exercise substrate + M5 Rust on-ramp** | DX | AUTO — seed `exercises/module4/_harness/` (2 stub agents + orchestrator) so safety lessons have something to govern; add a one-lesson Rust bridge (rustup + hello + cargo) at M5 entry. |
| **M8 is structurally different** (agentic run, not prose authoring) | CEO, Eng, Codex CEO | SURFACE — "M7 fleet builds the exam" isn't AUTHOR→VERIFY→SHIP; define the student's active role (else it's a demo, not an exam) before M6 (it shapes M6/M7 artifact design). |

## CEO/Eng/DX consensus tables (abbrev)

- **CEO:** premises mostly sound; right problem CONFIRMED; the artifact-binding altitude is the live strategic risk; 6-month regret = unverified code artifacts + undefined M8.
- **Eng:** pipeline PASS for prose, **FAIL for code artifacts**; failure modes = unshipped-M3 drift, lesson-grade-gate-on-code, non-MS grounding, fleet/loop inclusion, cloud-cred hygiene, M8 mismatch.
- **DX:** keep the one-idea split; the learner risk is *substrate* (M4 harness), *second-language ramp* (M5 Rust), and *cloud setup cost* (M6) — all fixable with starters + prereqs + local fallbacks.

## Surfaced to the gate (NOT auto-decided)

- **USER CHALLENGE — build order ("pull, not push").** Codex CEO + the strategic lens argue: build the **M6 coding-agent skeleton (artifact 01) early**, then let M4/M5 teach the failures it exposes — the back half pulled by a working artifact, not pushed by more chapters. This contradicts Ray's stated "jump into M4 next." Your direction stands unless you change it.
- **KEY DECISION — artifact→platform binding altitude (directive #2).** Strong cross-voice recommendation: bind to the **capability** (retrieval index, model gateway, eval store, deploy target, tracing, secrets, CI, human gate) + show **one concrete stack** + name the **portable interface** — NOT vendor ceremony (screenshots, menu flows, SDK trivia that ages badly). Toy abstractions are rejected (directive #2 holds); pure vendor-lock is rejected (ages badly).

## Decision audit (auto-decided via the 6 principles)
1. Ship M3 first (P6). 2. Add code BUILD/TEST gate for M6–M8 (P1). 3. Claim-authority map + WebFetch for non-MS platforms (P1). 4. Dry-run-first cloud strategy + prereqs doc + local fallbacks (P1). 5. M4 gets its own PLAN.md: locked count, kill-switch/HITL threading, Ch03 Fleet/Loop split, fleet/loop positive inclusion list (P1/P5). 6. M4 `_harness/` starter (P1). 7. M5 Rust bridge lesson (P1). 8. Define M8 student-role before M6 (P1). 9. Run `mdbook build` at M3 SHIP (first real build — also validates M1/M2) (P1).
