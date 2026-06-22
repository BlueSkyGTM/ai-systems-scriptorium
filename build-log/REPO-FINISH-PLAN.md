# Finish-the-Repo-Right Plan — the structured close of the Scriptorium

**Status:** for review (`/autoplan`). The pivot after the stress test: stop trusting rationale, make
quality *measurable*, and finish the repo with structured deploys. ECP frame — **the gate is king**;
from here, quality is read off mechanical gates, not persuasion, and the operator is present at every
irreversible move.

## Goal
Maximize the value of this repo by making three things true: (1) every book's production claim is
**re-runnable** (committed hard gates), (2) we can **measure** which gate actually deters a quality
drop (a gate-testing environment), and (3) the remaining books are finished by **structured,
instrumented deploys** that read the Sonnet/Haiku downgrade off the mechanical axis. Then graduate
what is content-complete.

## Why now (what the stress test surfaced)
- The method **HOLDS** (3 books advanced in parallel, zero collisions; governance + isolation +
  composition is the attributable delta).
- But gate integrity is uneven: **Sans Python + Answer Engineering ship committed, re-runnable gates;
  Just Python + Local Metal commit none** — their "all gates pass" was a one-time conductor
  reference-run, not persisted. That is a soft gate where a hard one belongs.
- In the run, gate passage was approved on **rationale**, which is bluffable; rationale degrades slower
  than correctness, so it would hide a downgrade. The fix is mechanical, persisted gates.

## Workstreams

### 1. Persist the gates (hard-gate the repo)
Commit a runnable acceptance validator per book that lacks one (Answer-Engineering-style: a `check_*.py`
+ a pytest, exit-code-honest, with a negative case). Target first: Just Python, Local Metal. Result: the
production claim is re-runnable and any future fleet downgrade is **bounded, not invisible**. Without
this, the downgrade experiment has no mechanical axis to measure on.

### 2. Build the gate-testing environment (the instrument)
A harness that measures **which gate catches which failure**. Feed each gate known-good inputs and
deliberately-degraded ones (a fabricated citation, a broken artifact chain, missing provenance,
off-bar difficulty, a non-running reference). Record catch/miss per gate. Output: a per-gate
"catches / misses" table — the **map of where soft gates are needed** (the quality dimensions the hard
gates cannot see). This is the test bench for the checks themselves, not the books.

### 3. Codify the soft/hard gate framework
- **Hard gate** = committed, exit-code-honest validator → a production floor (mechanical, persistent,
  fleet-independent).
- **Soft gate** = judgment/rationale/rubric check → an exploration + measurement instrument.
- Standing rule: never let a rationale-gate stand alone where correctness must hold; measure quality on
  the mechanical axis. Where hard gates cannot reach (prose depth, insight, voice), define soft gates
  with explicit rubrics so the judgment is at least repeatable.

### 4. Finish the books with structured Sonnet/Haiku deploys
- **Control: Answer Engineering M6–M8** — within-book comparison against Opus M1–M3 (same ore,
  contracts, throughline) measured against the committed `check_prep.py` gate. The clean read.
- Then **Weights and Measures** and **Machine Math** (cheap fleet, each with a committed gate). These
  are confounded (no Opus twin) — supporting evidence, not the control.
- Reconcile the two stubs (**Show, Don't Tell** / **Simple Systems**) before starting either.
- Every deploy is structured: `GATE-LOCK-PLAN` → fleet authors → VERIFY (live grounding) → conductor
  reference-run → **commit the gate** → `GATE-APPROVE-SHIP`. No ad-hoc passes.

### 5. Graduate the content-complete books
Move Just Python + Local Metal to `library/completed/`, update `CATALOG.md`, `route-lint` green. Clear
Local Metal M1–M2's `GATE-APPROVE-SHIP`. Operator-coordinated: run only when the parallel hosts are
quiet, so a relocation does not yank a lane from a live host.

## Open decisions for review
- **Sequencing:** gates-first (build the instrument + persist gates before finishing books, so the
  downgrade is measurable) vs books-first (finish, then instrument). Recommendation: gates-first — an
  un-instrumented run produces vibes, not data.
- **Gate-testing environment scope:** a built harness vs a documented manual procedure.
- **Weights / Machine Math model:** Opus (your strongest portfolio pieces) vs Sonnet/Haiku (the
  experiment). Decide per book by which goal wins — clean measurement uses AE as the control regardless.
- **The two stubs:** merge, cut, or build.

## GSTACK REVIEW REPORT

**Run:** autoplan (CEO + Eng + DX, combined pass). **Voices:** Codex (gpt-5.5) + a blind Claude
subagent, parallel. Strong convergence — both independently flagged the same fatal measurement flaw.

### Consensus on the five decisions
| # | Decision | Codex | Claude | Consensus |
|---|---|---|---|---|
| 1 | Sequencing gates-first | SOUND | SOUND (only while gates stay cheap) | CONFIRMED sound |
| 2 | Gate-testing environment | SOUND at mutation-test scope only | RISKY (right frame, over-build risk) | CONFIRMED: build a minimal mutation-fixtures + catch/miss matrix (generalize `test_check_prep.py`), NOT a harness/platform |
| 3 | Mechanical-axis / soft-hard framework | RISKY | WRONG-as-written | CONFIRMED risk: the mechanical axis measures the FLOOR only; insight/voice/depth need a PINNED grader (fixed judge + prompt + pre-registered threshold) or it's "judgment with a label" |
| 4 | AE M6–8 within-book control | RISKY | RISKY (fatal as stated) | CONFIRMED: the gate measures the floor → both models pass → "passes gate" is a TIE that detects nothing; it's cross-sectional, not paired |
| 5 | Measurement rigor | WRONG-as-written | WRONG-as-written | CONFIRMED: no defined downgrade metric, no blinding, no paired design, no pre-registered threshold, n≈3 underpowered → "decorated anecdotes" / "vibes" |

### The killer finding (both, identical)
**"Passes the committed gate" will be read as "quality held" — but the gate is structurally blind to
the only thing the downgrade threatens.** `check_prep.py` checks structure/completeness, not
insight/voice/depth. The mechanical axis measures the FLOOR; the downgrade lives in the CEILING. The
plan validates itself on the one axis guaranteed not to move.

### Auto-decided revisions (mechanical, per the 6 principles)
1. **Gate-testing environment → minimal mutation-matrix, not a harness** (P5, P3). Generalize the
   existing `test_check_prep.py` (already a 2-point mutation test) into a fixtures dir + a catch/miss
   matrix runner. An afternoon, not a platform.
2. **Persist JP + LM floor gates with a positive + a deliberate-negative fixture each** (P1, P2) —
   prerequisite for graduation and for bounding a downgrade, but NOT a downgrade metric.
3. **Write the soft/hard framework FROM the matrix output, not before** (P5) — the matrix shows which
   dimensions fall outside the hard gates; the framework is downstream of that.
4. **Drop Weights/Machine Math from the experiment** (P4) — confounded, n=1, no inferential value;
   finish them for the portfolio, do not count them as evidence.

### Decision Audit Trail
| # | Decision | Class | Principle | Rationale |
|---|---|---|---|---|
| 1 | Minimal mutation-matrix (not a harness) | Mechanical | P5,P3 | Both: over-build risk; seed exists in `test_check_prep.py` |
| 2 | Persist JP+LM floor gates w/ pos+neg fixtures | Mechanical | P1,P2 | Prerequisite for graduation; both flagged |
| 3 | Framework doc deferred until matrix runs | Mechanical | P5 | Write from data, not before |
| 4 | Weights/MM out of the experiment | Mechanical | P4 | Confounded; no inferential value |
| 5 | Measurement design (floor-gate vs ceiling metric) | USER CHALLENGE | — | Both challenge "measure on the mechanical axis" → D1 |
| 6 | First action (pilot vs floor-gates) | TASTE | — | D2 |
| 7 | Weights/MM model choice | TASTE | — | D3 |
| 8 | The two stubs | TASTE | — | D4 |

### Open decisions for the operator
D1 measurement design; D2 first action; D3 Weights/MM model; D4 the two stubs — presented at the gate in chat.

### Gate outcomes (operator)
- **D1 = add a paired-blind ceiling metric.** The mechanical gate stays for the floor + graduation; the
  downgrade is measured on the CEILING via a **pinned grader** (fixed judge model + fixed prompt +
  pre-registered threshold) on blind, attribution-stripped output. Extends the thesis: mechanical for the
  floor, pinned-grader for the ceiling. (Resolves the killer finding — the committed gate is blind to the
  variable under test.)
- **D2 = single-module paired-blind pilot FIRST.** One AE module, authored by BOTH Opus and the cheap
  fleet from the same brief; strip attribution; score the ceiling against the pre-set threshold — before
  scaling to AE M6–8. Floor gates (JP/LM) proceed as a graduation prerequisite, NOT as the downgrade metric.
- **D3 = Opus for both Weights and Measures + Machine Math** (portfolio, not experiment). Dropped from the
  downgrade study (confounded, n=1).
- **D4 = cut both stubs** (Show, Don't Tell / Simple Systems): remove stub dirs + `CATALOG.md` rows +
  `route-manifest.yaml` entries, `route-lint` green. Operator-coordinated (run when parallel hosts are quiet).

**Revised study scope:** the downgrade study = the paired-blind pilot on one AE module + a defined ceiling
metric, THEN (only if the delta is detectable) scale to AE M6–8 with the ceiling metric instrumented.
Weights/Machine Math and the cut stubs are out of the study.
