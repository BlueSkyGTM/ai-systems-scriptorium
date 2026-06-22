# Downgrade Pilot — Pre-Registered Spec

**Pre-registered:** 2026-06-21, before any cheap-fleet output is graded. Written first on purpose: the
decision rule below is fixed *now* so the result cannot be rationalized later.

## The question
Does authoring with a cheaper fleet (Sonnet/Haiku) measurably degrade book quality on the dimensions
the committed hard gate is blind to? The gate (`check_prep.py` and friends) checks structure and
completeness — the floor. The downgrade, if any, lives in the ceiling: insight, depth, voice,
pedagogy. This pilot measures the ceiling, on one module, before spending a fleet on the rest.

## Why a pilot, not the full study
`n = 1` module. This is a **detectability probe**, not a population estimate. It answers one yes/no:
*is the downgrade even visible with this instrument?* If yes → we have a working metric and scale it
to AE M6–8. If no → either the cheap fleet is sufficient for this content type, or the instrument is
too blunt; re-test on a harder content type before concluding. We do not generalize from one module.

## Design: paired, same-module, blind
- **Module:** Answer Engineering **M3 "Behavioral Interviews"** (already shipped by Opus). Reason:
  meaty, insight-heavy content (worked STAR-L examples, signal reasoning) — lots of ceiling to lose;
  and the Opus version already exists, so we spend **one** cheap-fleet run, not two.
  - *Alternative if you want both-fresh:* author an unstarted module (M6) with both tiers from the
    same brief. Cleaner (neither has an in-sequence context advantage) but costs an Opus run too.
- **Paired:** both versions are the *same module* — same ore, same contracts, same brief. The only
  variable that changes is the authoring model tier.
- **Confound control:** give the cheap-fleet re-author the **same context the Opus run had** (M1–M2
  established, the ingredient, the voice exemplar) so the only difference is model tier, not context.
- **Blind:** strip all attribution from both texts. Label them **Version A / Version B** in randomized
  order. The grader is never told which tier wrote which, or even that model tier is the variable.
  The A/B→tier mapping is recorded separately by the operator and not revealed until after scoring.

## Protocol
1. Pull the committed Opus M3 (the shipped lessons) = one version.
2. Re-author M3 with the cheap fleet from the **same brief + same context**. Hold it to the same
   `GATE-LOCK-PLAN` → author → VERIFY → reference-run flow. It must pass the **same hard gate**
   (`check_prep.py --module 3`) — confirm it does (expected: both pass; that is the point — the floor
   ties, so the floor tells us nothing).
3. Strip attribution from both; randomize to A/B; record the mapping offline.
4. Score both with `grader-prompt.md` against `ceiling-rubric.md`. Run the grader **3 times** (fresh
   instance each), average per dimension, and report the spread (inter-run variance).
5. Unblind. Compute the deltas. Apply the decision rule.

## The metric
Five ceiling dimensions, 1–5 each (see `ceiling-rubric.md`): Insight Density, Explanatory Depth,
Voice/Craft, Pedagogical Scaffolding, Grounding Fidelity. Total out of 25, averaged over 3 grader runs.

## Pre-registered decision rule (fixed before grading)
- **Downgrade DETECTED** if the cheap version scores **≥ 3 points lower in total** OR **≥ 2 points
  lower on any single dimension**, on the 3-run average.
- **No detectable downgrade** if both gaps are smaller than that (total < 3 and every dimension < 2).
- **Instrument too noisy (inconclusive)** if the inter-run spread on either version is ≥ 2 total
  points — the grader is not self-consistent, so the metric is noise; pin it harder (lower temp,
  sharper anchors) and re-run before trusting any delta.

## What each outcome triggers
- **Detected:** the metric works. Scale it to AE M6–8 (instrument every module), and use it as the
  ceiling gate for all future cheap-fleet deploys.
- **Not detected:** the cheap fleet is sufficient for this content type. Finish the remaining books
  cheap, but re-run the pilot once on a harder content type (a systems-design or math-heavy module)
  before declaring it sufficient everywhere.
- **Inconclusive:** fix the grader, do not ship a conclusion.

## Outputs (written here)
- `pilot-M3-scores.md` — the 3-run scores per version, deltas, the unblinded mapping, the verdict.
- A one-line entry appended to `FINDINGS.md` with the verdict.

## Instrument v2 (post-pilot fix, 2026-06-21)
The pre-registered rule above is kept as-written (pilot v1 was formally INCONCLUSIVE under it). The
pilot exposed *why*: the decision was scored on **absolute totals**, which carry grader-calibration
drift (a 5-point inter-run spread on the same version). Corrected instrument for all future runs:
- **Decision statistic = the paired within-run delta.** Each grader scores BOTH versions in the same
  run; take Opus − Cheap per run. Calibration cancels (a generous grader inflates both equally). Report
  the mean delta and the spread across runs, not absolute totals.
- **Detected** if the mean paired-delta is ≥ 2.0 / 25 AND ≥ 80% of runs share the sign.
- **Runs ≥ 5.** Optionally add a 2–3 passage calibration anchor set (a known-3 and a known-5) to pin
  the absolute scale; secondary, since the paired delta already cancels calibration.
- **Provenance-token lint** (`provenance-lint.py`) moves the one mechanically-catchable defect — source
  IDs leaking into reader-facing prose — off the ceiling grader onto a hard gate. Run it first; the
  ceiling grader judges only what a lint cannot.

## Honest limits (stated up front)
One module, one judge family, no human cross-check. A single LLM-judge can share blind spots with the
authors. If the pilot says "detected," it is trustworthy (a real, blind, paired gap). If it says "not
detected," that is weaker — it may mean the instrument can't see the loss, not that there isn't one.
Treat a null result as "not yet shown," never as "proven equivalent."
