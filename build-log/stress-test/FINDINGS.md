# Stress-Test Findings — Does the Method (Not Built-Ins) Complete the Books?

**Written:** 2026-06-21, from the per-book ledgers (`build-log/<book>/build-progress.md`) + git, after
the parallel-host sessions ran. The HANDOFF asked for this verdict; the sessions shipped books instead
of writing it, so it is reconstructed here from what they left behind.

**Standing frame (Ray):** the repo is both a **working pipeline** and an **observatory.** This file is
the observatory log. Keep it honest; a negative result is a real result.

**The question:** not "did the books get made" — they did. It is **which part did the work: the
structure (routing + contracts + gates + conductor-verifier + isolation) or Claude's raw capability?**

---

## What got built (cold parallel hosts, one branch, one working tree)

- **Just Python — content-complete 8/8.** Capstone `pipeline.py` imports `wrangle.py` (M6) + `eval_engine.py`
  (M7) off disk under a code-graded `rubric.py`; all exercise gates pass; `mdbook build` clean.
- **Local Metal — content-complete 7/7** (M3–M7 shipped; M1–M2 authored/verified/built, awaiting
  `GATE-APPROVE-SHIP`, a human gate). Runnable spine `ollama_client.py` (M3) → `route.py` (M5) →
  `mcp_server.py` (M6) reads end to end; seven `check_*.py` validators.
- **Answer Engineering — 4 of 8 shipped** (M1–M3, M5), **M4 correctly deferred** (see finding 3),
  M6–M8 not started. `check_prep.py` grew v1→v4 in place across modules, staying backward-compatible
  (40/40 tests).

Three books advanced concurrently, committed sequentially to `main`, **zero collisions** — no merge
conflicts, no cross-book contamination. `git worktree list` shows one tree: the isolation was purely
**filesystem boundaries** (each book its own `library/` lane + `build-log/` ledger), not separate
worktrees and not separate context.

---

## Verdict: HOLDS for the mill + governance + isolation. The abstraction front-end is PARTIAL. The inverted/co-discovery layer is UNTESTED.

### What the structure demonstrably did (attributable delta over a cold-Claude baseline)

1. **Grounding + VERIFY caught fabrication, repeatedly — a built-in failure the structure corrected.**
   Cold workers fabricated MS-Learn citations in Just Python M2/M3 and would have in every book. The
   grounding rule (author against the live connector, cite real verified URLs) + the VERIFY gate caught
   and removed them; after M4 the rule was standing and fabrications went to zero across all three books.
   A baseline prompt does not self-catch its own fabrications.

2. **The conductor reference-run caught cold-worker drift the workers' self-reports missed.**
   On multi-file shared artifacts (Just Python M6/M8, Local Metal M1–M4 schema/naming divergences), four
   cold workers drifted on cross-file seams (wrong `composed_modules` value, a missing dataclass field,
   `default_config` scoped wrong, an adapter path off by one + missing `sys.modules` registration, 3-way
   BOM-column divergence, function-name mismatches). The conductor **assembling and running the full
   reference harness end to end** is the gate that caught all of them. This is the "parent verifier" the
   autoplan review said a blind-leaf cascade requires — validated in production.

3. **No-fabrication governance produced a correct module-level DEFER, not fabricated content.**
   Answer Engineering M4 (technical screens) was **deferred** because the vault has no live-coding-screen
   ore and the no-fabrication rule forbids inventing coding problems. The system refused to fabricate and
   stopped — the "declare-and-halt / insufficient-input" behavior the review demanded for blind leaves,
   firing at the module level. This is the single strongest safety result: the governance chose a true
   gap over a plausible fake.

4. **The artifact-chaining contract held across all three books.** Compounding artifacts, not just
   stacked lessons: Just Python's `measure.py` chain → `vectorization_report.py` → `wrangle.py`/`eval_engine.py`/`pipeline.py`;
   Local Metal's `ollama_client.py` → `route.py` → `mcp_server.py` spine; Answer Engineering's `check_prep.py`
   grown v1→v4 in place with byte-identical backward compatibility. A baseline run produces lessons; the
   contract produces a portfolio that composes.

5. **Isolation let parallelism be real.** Three books, one branch, no collisions — the filesystem-boundary
   model carried concurrent cold hosts without a coordination layer.

### What built-ins did, honestly

The model's raw capability wrote the prose and the code. A cold Claude with one good prompt can author a
strong lesson. What it cannot do alone: keep three books consistent to one standard, catch its own
fabrications, refuse to fabricate a missing module, and chain artifacts across eight modules. That gap —
consistency, self-verification, principled refusal, composition — **is** the structure's contribution.
The structure is governance, not authorship.

### What was NOT tested (the honest gaps)

- **The inverted / co-discovery layer never fired.** Every book arrived with its goal already frozen —
  the Sans Python gap-report rows, the Cthulhu SPEC, the `asdg` ore's known shape. There was never a "we
  don't know what this book is" moment requiring a goal co-discovered bottom-up with the operator. The
  deepest part of the abstraction thesis is untested here, because books are concretization with known
  targets. It needs a domain where the goal is unknown at the start (an open problem, a fresh ops system).
- **The distillation front-end is PARTIAL, not absent (correcting an earlier claim).** It **did** fire in
  Answer Engineering: raw `asdg` ore → distilled ingredients (signal taxonomy, frameworks catalog,
  behavioral bank, systems-design ore) across M1–M5. It was **bypassed** in Just Python (M1–M3 used
  reference-grade vault docs; the dossier machinery stayed idle). So distillation works when raw ore
  exists and is skipped when it doesn't — the engine pulls it only when load-bearing. Proven, not
  unproven; just not always needed.

---

## Orchestration observations

- **The handler tier is usually unnecessary.** Just Python M3 ran conductor-direct and matched the
  handler-tier M2 on quality; `ORCHESTRATION.md` was relaxed (handler only for concurrent gates or
  multiple clusters, not by worker count). Orchestration is throughput tuning, not a quality lever.
- **The useful division that emerged: Haiku fetchers feeding Sonnet authors.** Local Metal M3–M7 and
  Answer Engineering M5 ran 2–3 Haiku source-fetchers (grounding URLs) into 4 Sonnet lesson-authors, with
  the Opus conductor owning + testing every code artifact. Speed + grounding without a quality cost.
- **Pre-locking structure narrows divergence but never eliminates it.** Even with contracts pre-locked
  (M8), four cold workers still drifted on the seams. The conductor reference-run remains the gate.

---

## The DCG read

The thing that did the work and the thing that held is **governance** — verify, grounding, the
reference-run, the no-fabrication defer. Deferred context was the tool (the agents stayed lean, hydrated
per task); governance was the goal. That is exactly **Deferred Context Governance**, and the evidence
names it: the mill plus the governance is the proven core; the abstraction front-end is the frontier,
proven in part (distillation) and untested in part (co-discovery). The books could not test the
abstraction thesis because they never posed the question abstraction answers.

---

## Open / pending (operator-coordinated)

- Just Python and Local Metal are content-complete but still under `library/in-progress/`. Graduation
  (move → `completed/`, update `CATALOG.md`, `route-lint`) is pending and should run only when the
  parallel hosts are quiet.
- Local Metal M1–M2 await `GATE-APPROVE-SHIP` (human gate).
- Answer Engineering M4 stays deferred until live-coding-screen ore is sourced (likely the real Sans
  Python portfolio code); M6–M8 not started.
- The abstraction thesis (inverted/co-discovery) remains the one thing the book domain cannot test. It
  is the question for the engine's eventual non-book casting.

---

## Pilot M3 — downgrade detectability probe (paired, blind, 3 Opus graders) — 2026-06-21
**INCONCLUSIVE** per the pre-registered rule: grader absolute-score spread (Opus 20→25) exceeded the
noise bar, so the near-null can't be trusted. No downgrade at threshold (mean delta +2.67/25 favoring
Opus, < 3), BUT direction unanimous (Opus > cheap-Sonnet 3/3). Non-uniform: Opus edged
insight/voice/grounding, TIED depth, and the cheap fleet BEAT Opus on pedagogy (full weak-answer
dissections). One mechanically-catchable cheap-side defect: provenance tokens ("asdg 05, Example 4")
leaked into prose. **Instrument fix before scaling:** score the paired within-run delta (not absolute
totals), add calibration anchors, raise to ≥5 runs, add a provenance-token lint. Experiment design
validated; metric needs tightening. Full data: `pilot-M3-scores.md`. Do not read as "cheap is fine."

### Pilot M3 — re-run, Instrument v2, n=5 (corrected) — 2026-06-21
Re-scored on the paired within-run delta (cancels the calibration drift that made v1 inconclusive).
5 blind Opus graders: deltas +1,+3,+4,+4,+4 → mean **+3.2/25, 5/5 positive = DETECTED** (small ~13%,
non-uniform). Gap is Voice +1.6, Grounding +1.2, Insight +1.0, Depth tie, Pedagogy −0.6 (cheap wins).
KEY: Voice+Grounding losses are largely the provenance-token leak, now caught by `provenance-lint.py`
(HARD gate, validated Opus-PASS/cheap-FAIL); Insight loss is verbosity (cheap +39% words). After the
lint + a length guard, residual true-ceiling gap is small → cheap fleet viable for this content type
WITH two added hard gates. The catchable part of the ceiling moved to mechanical gates = the soft→hard
migration, demonstrated. (Confirmatory, not clean pre-reg — v2 threshold set after run 3.)
