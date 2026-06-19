# /autoplan Review — Sans Python / Northstar curriculum spec

**Run:** 2026-06-18 · adapted (non-git, docs-as-plan) · phases: CEO + Eng + DX (Design skipped — no real UI scope)
**Reviewed:** `northstar/SPEC.md`, `SYLLABUS.md`, `HANDOFF.md`, `REFERENCE-LAYER.md`
**Dual voices:** Codex `gpt-5.5` (cross-model) + independent Claude subagent — both ran, `source=codex+subagent`
**Decisions:** 24 findings → 17 auto-decided (mechanical), 4 taste, 3 user challenges
**Filesystem-grounded:** yes — verified claims against the cloned `migration/synthesis/` tree (value-add beyond both models, which saw only the 4 docs)

---

## Filesystem ground truth (verified, not claimed)

| Claim in docs | Reality on disk | Verdict |
|---|---|---|
| Handoff-1 "9 `output/` folders" feed the audit | 9 sub-repos exist in `source/_repos/`, but **no `output/` folders**; extraction is consolidated per-module in `source/moduleN/` | **Contract is wrong** — Handoff-1 references a layout that doesn't exist |
| SPEC source table = 6 sub-repos | **9** on disk (adds `ai-performance-engineering`, `ai-system-design-guide`, `loop-engineering-orange-book`) | SPEC table stale |
| SYLLABUS: "Step-2 flow audit passed" | `output/snapshot/step2-flow-audit.md` **exists** | SYLLABUS grounded → it wins the staleness dispute |
| HANDOFF: renumber + flow-audit + antilibrary fold-in are TODO | `step2-flow-audit.md`, `step3-resolutions.md`, renumbered SYLLABUS all exist; snapshot `module1-5.md` still old numbering | HANDOFF **stale** on those; right that snapshot files aren't renumbered |
| HANDOFF: `build/CONTEXT.md` "does not exist yet" | No `build/` dir anywhere | **Correct** — Handoff-2 spec genuinely missing |
| "lesson-level audit not begun" | No `lesson-audit.md`, no `lessons/` anywhere | **Correct** — honest |

**Doc authority ruling (resolves the one model disagreement — Claude said HANDOFF wins, Codex said SYLLABUS wins):**
**SYLLABUS.md is the curriculum state-of-record. HANDOFF.md is archival** (end-of-session snapshot, now stale). HANDOFF retains value only as the list of genuinely-open work, of which exactly **three items remain real**: (1) reconcile `artifacts-plan.md`, (2) write `build/CONTEXT.md`, (3) renumber the snapshot `module1-5.md` files. Mark HANDOFF archival and move those three into a live TODO.

---

## Consensus tables (Claude subagent ⋂ Codex)

### CEO / Strategy
| Dimension | Claude | Codex | Consensus |
|---|---|---|---|
| 1. Premises stated & evidenced? | NO (1-day JD audit, confirmation bias) | NO (asserted, no falsification criteria) | **CONFIRMED concern** |
| 2. Right problem to solve? | YES (seam is real) | YES (capability framing strong) | **CONFIRMED — problem right, framing weak** |
| 3. Scope cut (perf>ML) calibrated? | concern (reads as rationalization) | concern (reframe to inference-platform) | **CONFIRMED concern → user challenge** |
| 4. Employability/market risk covered? | NO (Python hole, niche title) | NO (interview readiness, Python) | **CONFIRMED critical** |
| 5. Positioning/title stable? | NO (Platform vs Systems Engineer) | NO (title unstable) | **CONFIRMED** |
| 6. 12-month trajectory sound? | NO (hardcoded numbers date) | NO (anti-IDE rhetoric dates) | **CONFIRMED** |

### Eng / Build architecture
| Dimension | Claude | Codex | Consensus |
|---|---|---|---|
| 1. Pipeline architecture sound? | NO (no MANIFEST) | NO (breaks at authority control) | **CONFIRMED critical** |
| 2. Authoring fidelity gate exists? | NO (no lesson template/rubric) | NO (no lesson contract) | **CONFIRMED critical** |
| 3. Build scope bounded? | NO (60–300 lessons unknown) | — | **CONFIRMED (med)** |
| 4. Dedup / "one spine" owned? | partial | NO (no section ownership) | **CONFIRMED** |
| 5. Drift/error paths handled? | NO (drifts to ML defaults) | NO (needs authoring constitution) | **CONFIRMED critical** |
| 6. Readiness/staleness manageable? | NO (HANDOFF stale, LearnHouse) | NO (mdBook vs LearnHouse, artifacts) | **CONFIRMED** |

### DX (student + build-AI)
| Dimension | Claude | Codex | Consensus |
|---|---|---|---|
| 1. Time-to-first-win fast? | NO (setup wall day one) | NO (NLP before any win) | **CONFIRMED critical** |
| 2. Copy-button UX specified? | NO (mechanism hand-waved) | NO (fragile surface) | **CONFIRMED** |
| 3. Failure/recovery paths? | partial | NO ("what if Claude Code fails") | **CONFIRMED** |
| 4. Prereq bar honest? | NO (beginner overloaded) | NO (dishonest bar) | **CONFIRMED critical** |
| 5. Runtime story coherent? | NO (no-IDE vs VS Code) | NO (contradiction) | **CONFIRMED** |
| 6. Build reproducibility? | — | NO (uncached MS Learn fetch) | **CONFIRMED (med)** |

**Convergence is unusually high — almost no model disagreement.** The only split (doc authority) is resolved above with filesystem evidence.

---

## Cross-phase themes (flagged independently in 2+ lenses → high-confidence)

1. **There is no build contract.** Shows up as CEO "no falsification criteria," Eng "no MANIFEST / no lesson template," DX "build-AI will drift." One missing artifact drives the top finding in all three lenses. **This is the headline.**
2. **The spec contradicts its own delivery.** "No IDE / IDEs near extinction" (SPEC) vs "Claude Code via VS Code" (SYLLABUS M8); "LearnHouse block format" (Handoff-2) vs "LearnHouse dropped, mdBook" (M8). Internal contradictions an authoring AI will resolve unpredictably.
3. **The prerequisite wall the thesis kills is relocated to setup.** M1-00 stacks three toolchains + agent + git + mdBook before any win — the exact gate SPEC claims to remove.

---

## Findings catalog (merged, deduped) + auto-decisions

Severity = max(both). Source: B=both, X=codex, C=claude, FS=filesystem-verified. Principle = the autoplan decision principle applied.

### Auto-decided — MECHANICAL (clearly right; the required next work)
| # | Lens | Finding | Sev | Src | Decision (P) |
|---|---|---|---|---|---|
| E1 | Eng | No canonical build MANIFEST (source IDs, versions, module map, keep/cut, authoring status) | crit | B,FS | **Create `northstar/build/MANIFEST.md`** before any handoff (P1) |
| E2 | Eng | No lesson contract/template (objective, source IDs, prereq edges, artifact, exercise cmd, eval rubric, anti-drift, mdBook path, copy payload) | crit | B | **Write a lesson template** (P1) |
| E3 | Eng | mdBook adopted but Handoff-2 still says "LearnHouse block format" | crit | B,FS | **Delete LearnHouse refs; define mdBook-native authoring** (SUMMARY.md, admonitions, code/asset conventions) (P5) |
| D5/E? | DX | Build-AI drifts to generic ML defaults | crit | B | **Add a per-lesson "authoring constitution"** (no generic ML history, no Python-first exercises, every lesson ties to a production task/artifact) (P1) |
| E4 | Eng | "One spine" (RAG/MCP/evals/memory/safety/observability/versioning) lacks section ownership | high | B | **Per-thread: canonical home + allowed/prohibited repeats + required cross-links** (P1) |
| E5 | Eng | Compounding artifacts have no interface contracts (M6→M7 compose) | high | B | **Define artifact APIs** (tool schemas, state, auth, logging, eval output, budgets, failure modes) — *strengthen the PROTECT item* (P1) |
| E6 | Eng | Handoff-1 "9 output/ folders" contract ≠ disk (per-module `source/moduleN/`) | high | FS | **Fix the Handoff-1 contract to the real layout** (P5) |
| E7 | Eng | SPEC source table lists 6 repos; 9 on disk | med | FS | **Reconcile SPEC table to the 9** (P3) |
| E8 | Eng | HANDOFF vs SYLLABUS staleness | high | B,FS | **SYLLABUS wins; mark HANDOFF archival; carry 3 open items forward** (P3) |
| E9 | Eng | `artifacts-plan.md` genuinely unreconciled to 8-module + compounding | high | B | **Reconcile before authoring** (it is the build spine) (P1) |
| E10 | Eng | Reference policy self-contradiction (MS Learn "only" vs Anthropic foundational) | med | X | **Reword: "only fetch-required reference; Anthropic = fixed conceptual appendix"** (P5) |
| E11 | Eng | Lesson count unbounded (60–300) | med | C | **Produce kept-lesson count per module from the audit before authoring** (P1) |
| C5 | CEO | Interview-readiness blind spot (Python, system design, k8s, SQL, incidents) | crit | X | **Add a per-module "hiring-surface" mapping** (P1) |
| C7 | CEO | Hardcoded salaries + perf deltas (EAGLE-3/NVFP4/4.16×) will date fastest | med | C | **Move named numbers to swappable reference entries; teach invariants (TTFT/TPOT/goodput/KV-cache)** (P5) |
| D1 | DX | TTFW too slow; setup wall | high | B | **Add a "first agentic win < 60 min" lesson in a hosted sandbox (toolchains pre-installed); defer Rust→M5, Python→point-of-read** (P1) |
| D2 | DX | Prereq bar dishonest | crit | B | **Publish explicit prereqs + a zero-module bootcamp (env, git, shell, agent loop, API keys, recovery)** (P1) |
| D3 | DX | Copy-button payload + progress schema hand-waved | high | B | **Spec the payload (goal, files-allowed, expected output, verify cmd, rollback, progress update, failure recovery) + progress-file schema; prototype on ONE lesson first** (P1) |
| D6 | DX | MS Learn fetch not reproducible | med | B | **Cache fetched refs (title/URL/date/summary/decision)** (P1) |

### Surfaced at gate — TASTE (auto-decided with recommendation, your call)
| # | Lens | Decision | Recommendation |
|---|---|---|---|
| C4 | CEO | Title string: "AI Platform Engineer" vs "AI Systems Engineer" (spec uses both) | **Lock "AI Platform Engineer"** (matches roadmap + SYLLABUS); lead with the *capability* ("owns the full AI system, first API call to dashboard"), map to adjacent titles. Grep-replace "AI Systems Engineer." |
| DA | Eng | Doc authority | **SYLLABUS state-of-record; HANDOFF archival + 3 open items** (evidence-resolved above) |

### Surfaced at gate — USER CHALLENGES (both models push on a locked decision; your direction is the default)
See the gate section below — C2 (perf>ML framing), C3 (Sans Python / Python track), C6 (anti-IDE rhetoric).

---

## Build-readiness gate — "Build-ready when ALL true"

The single checklist both models asked for (readiness is currently scattered across 3 docs and self-contradictory):

- [ ] `build/MANIFEST.md` exists (9 repos, module map, keep/cut, version, authoring status)
- [ ] Lesson template + per-lesson authoring constitution defined (mdBook-native)
- [ ] All LearnHouse references removed; mdBook authoring rules written
- [ ] `artifacts-plan.md` reconciled to 8-module + compounding + artifact interface contracts
- [ ] Copy-button payload + progress-file schema specified and prototyped on one lesson
- [ ] Handoff-1 contract matches the real `source/moduleN/` layout
- [ ] Lesson-level audit complete → kept-lesson count per module known
- [ ] Title string locked; SPEC source table = 9; HANDOFF marked archival
- [ ] (Gate decisions C2/C3/C6 resolved by Ray)

Only after all true does Handoff-1 → Handoff-2 → mdBook authoring begin.

---

## PROTECT (unanimous — do not dilute during the build)

**The compounding-artifact spine:** single agents (M6) → governed teams (M7) → the team builds the exam system (M8), each solving a real business problem. Both models named this independently as the one thing that makes the course read as *AI Platform Engineering* instead of another stitched-together AI survey. Strengthen it with interface contracts (E5); never flatten it into a topic checklist.

---

## Decision audit trail (auto-decisions)
All 17 mechanical decisions above were taken under principles P1 (completeness), P3 (pragmatic), P5 (explicit over clever) per the /autoplan 6-principle set. None reduce scope; all are additive build-contract work. The 4 taste + 3 user-challenge items were NOT auto-decided and went to Ray at the gate.

---

## Gate outcomes (Ray, 2026-06-18)

| # | Decision | Ray's ruling |
|---|---|---|
| C2 | perf>ML framing | **Reframe to "inference-platform engineering > model training" + define minimum ML-literacy floor** |
| C3 | Python demotion | **Add the narrow "Python you WILL write" track** (read/debug, pytest, packaging, FastAPI glue, eval scripts, notebook→service) |
| C6 | anti-IDE rhetoric | **Reframe to "agent-first environment"** (CLI + VS Code + hosted sandbox); drop IDE-extinction absolutism |
| C4 | title string | **"AI Platform Engineer"** — grep-replace "AI Systems Engineer"; lead with capability |

**Open strategic thread (raised by Ray at C3):** the SPEC "English is the most important programming language" pillar is a lossy proxy for the **orchestration layer**. Pending decision: demote "English" to a supporting line and make **orchestration-first + platform-seam** the explicit thesis — and whether that forces a course rename or just a thesis rewrite (recommendation: keep the "Sans Python" name as the positioning hook, fix the thesis, no rename). Resolve before applying edits to SPEC.md.

**STATUS: DONE_WITH_CONCERNS.** Gate passed. Primary concern at review time: no build contract — the unanimous #1 finding.

---

## Post-review reconciliation (2026-06-18)

The "#1 finding" was resolved by discovery, not new work: **the build contract already existed in the
`migration/` layer** and the top-level docs were simply a stale generation pointing elsewhere.

- `migration/AUTHORING.md` = the build contract (three-source rule, per-lesson How-To, Zinsser pass, execution model).
- `migration/_dossier/module1-5 + 6-7-8.md` = the lesson audit (Handoff-1 output), all modules.
- `migration/src/` = ~21 lessons already drafted; `theme/copy-to-claude.js` = the copy button; `book.toml` = mdBook.
- `snapshot/artifacts-plan.md` = already reconciled to 8-module + compounding (2026-06-18).

Action taken: the from-scratch `build/` folder created during this review was **removed as redundant**; all
references repointed to `migration/`. `northstar/CONTEXT.md` (LearnHouse-era) and `HANDOFF.md` marked archival.
Thesis gate rulings (inversion/orchestration-first, inference-platform>model-training, agent-first,
Python-write-track, title) ported into `SPEC.md`, `SYLLABUS.md`, and the canonical voice (`migration/src/README.md`).

**Real frontier:** finish authoring `migration/src/` — modules 6–8 are stubs; 1–5 are partial.
