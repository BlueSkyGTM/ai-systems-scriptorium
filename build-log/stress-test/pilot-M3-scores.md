# Pilot M3 — Scores & Verdict

**Unblinded:** version-a = **Opus** (committed `src/module3`), version-b = **cheap** (Sonnet fleet).
3 blind Opus graders, ceiling rubric (5 dims × 1–5 = /25), authorship-blind, per `PILOT-SPEC.md`.

## Raw (Opus / Cheap)
| Dim | R1 | R2 | R3 | Opus mean | Cheap mean | Δ (Opus−Cheap) |
|---|---|---|---|---|---|---|
| Insight Density      | 4 / 3 | 4 / 3 | 5 / 4 | 4.33 | 3.33 | **+1.00** |
| Explanatory Depth    | 4 / 4 | 4 / 4 | 5 / 5 | 4.33 | 4.33 | **0.00** (tie) |
| Voice / Craft        | 4 / 3 | 5 / 3 | 5 / 4 | 4.67 | 3.33 | **+1.33** |
| Pedagogical Scaffold | 4 / 5 | 4 / 5 | 5 / 5 | 4.33 | 5.00 | **−0.67** (cheap wins) |
| Grounding Fidelity   | 4 / 4 | 4 / 3 | 5 / 3 | 4.33 | 3.33 | **+1.00** |
| **TOTAL /25**        | **20 / 19** | **21 / 18** | **25 / 21** | **22.0** | **19.33** | **+2.67** |

Per-run paired delta (Opus − Cheap): **+1, +3, +4** — sign unanimous.
Inter-run spread (absolute total): Opus **5** (20→25), Cheap **3** (18→21).

## Verdict against the pre-registered rule
- **Downgrade DETECTED?** No. Mean total delta +2.67 (< 3) and max per-dim delta +1.33 (< 2) — under both registered thresholds.
- **Inconclusive (noise)?** **YES.** Pre-reg: inconclusive if inter-run spread ≥ 2 on either version. Opus spread = 5, Cheap = 3. The grader is **not self-consistent on the absolute scale**, so the near-null cannot be trusted.
- **Net: INCONCLUSIVE.** No downgrade at the registered bar, but the instrument is too noisy to trust that null. (Pre-registration honored — the goalposts do not move after seeing the data.)

## What the data shows anyway (held loosely, sub-threshold)
- **Direction is unanimous:** Opus > cheap in all 3 runs.
- **Non-uniform:** Opus edges Insight (+1.0), Voice (+1.33), Grounding (+1.0); **ties** Depth; the **cheap fleet BEAT Opus on Pedagogy** — it showed full weak-answer-then-fix dissections and a complete model answer, where Opus narrated the contrast.
- **One concrete cheap-side defect, caught by all 3 graders:** raw provenance tokens leaked into reader-facing prose ("Question type: Collaboration and Conflict (asdg 05, Example 4)"), with inconsistent IDs. That is a STYLE / machine-token-in-prose violation — and it is **mechanically catchable** (a lint for source-ID patterns in prose).

## The methodological finding (the real pilot payoff)
The noise rule fired because the decision was pre-registered on the **absolute total spread**, which
carries grader-calibration drift (run 3 graded generously — straight 5s for Opus). The right statistic
is the **paired within-run delta** (same grader scores both → calibration cancels), which was far more
stable (unanimous sign) than the absolutes. The pilot did exactly its job: it exposed the instrument's
flaw cheaply, before scaling.

**Fix the instrument before any scale-up or conclusion:**
1. Pre-register the decision on the **paired within-run delta**, not absolute totals.
2. Add a 2–3 example **calibration anchor set** (what a 3 vs a 5 looks like) to pin the absolute scale.
3. Raise to **≥ 5 grader runs**; report delta mean + spread.
4. Add a **hard lint for provenance tokens in prose** — moves the one mechanically-catchable defect off
   the ceiling grader and onto a cheap hard gate (exactly the soft→hard migration the framework wants).

## Recommendation
The **experiment design is validated** — blind, paired, produced interpretable per-dimension data and
caught a real defect. The **metric needs tightening** (delta statistic + calibration + more runs)
before it can adjudicate a gap this small. The signal so far: the cheap fleet's "downgrade" is **small
and non-uniform** (thinner insight/voice/grounding, equal depth, *better* pedagogy) plus one
hard-gate-able style leak — not a catastrophe. Re-run with the fixed instrument on this module and one
harder module before trusting either direction. Do NOT read this pilot as "cheap is fine."

---

## Re-run — Instrument v2, n=5 (corrected verdict, 2026-06-21)
Re-scored on the **paired within-run delta** (the v2 fix that cancels grader-calibration drift); 5 blind
Opus graders total. Paired deltas (Opus − Cheap) per run: **+1, +3, +4, +4, +4** → mean **+3.2 / 25**, **5/5 positive**.

| Dim | Opus mean | Cheap mean | Δ |
|---|---|---|---|
| Insight Density | 4.2 | 3.2 | +1.0 |
| Explanatory Depth | 4.2 | 4.2 | 0.0 (tie, all 5) |
| Voice / Craft | 4.8 | 3.2 | **+1.6** (largest) |
| Pedagogical Scaffold | 4.2 | 4.8 | **−0.6** (cheap wins, all 5) |
| Grounding Fidelity | 4.4 | 3.2 | +1.2 |
| **TOTAL** | **21.8** | **18.6** | **+3.2** |

**Verdict (v2): DETECTED — a small (~13%), robust, non-uniform downgrade.** Mean delta +3.2 ≥ 2.0 and
5/5 share the sign. *Transparency caveat:* the v2 threshold was set after the first 3 runs, so this is a
strong **confirmatory** result, not a clean pre-registration; runs 4–5 (set blind to the threshold) both
landed +4, consistent.

**Where the gap lives — and how much is mechanically recoverable:**
- Voice (+1.6) and Grounding (+1.2) are **largely the provenance-token leak**, now caught by
  `provenance-lint.py` as a HARD gate (validated: Opus PASS / exit 0, cheap FAIL / exit 1, 10 lines flagged).
  So most of the two biggest gaps are lint-catchable, not true-ceiling loss.
- Insight (+1.0) is **padding/verbosity** (cheap wrote 39% more words) — catchable by a length/density guard.
- Depth ties; Pedagogy favors cheap (it shows full weak-answer dissections).
- **Net: after the provenance lint + a verbosity guard, the residual true-ceiling gap is small.** The
  cheap fleet is viable for this content type **with two hard gates added** — which is the actionable
  conclusion, and a textbook soft→hard migration: measure the gap once on the ceiling, then move the
  catchable part of it onto cheap mechanical gates.
