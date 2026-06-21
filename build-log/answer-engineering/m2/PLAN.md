# Module 2 — The Algorithm in Detail — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared via Ray's "go for it").** Second authoring
stage for Answer Engineering (M1 "The Framework" shipped 2026-06-21). M2 takes the four-step Algorithm
M1 installed and goes deep on each step: the expert's internal monologue, the hard cases, the real-time
judgment. All three open decisions resolved at lock: the M1/M2 dedup split below is locked; cadence
locked at 4 lessons (one step each); `check_prep.py` extends in place to v2.

## The stage in one line

M1 taught you to run the loop once, on clean questions. M2 is the internal monologue of someone who has
run it fifty times: the ambiguous decomposition, the signal that shifts mid-conversation, the answer
delivered out loud under pressure, the self-audit that catches the weak sentence before the interviewer
does. Seam: a Production AI Engineer who can run the Algorithm slowly on paper still freezes in the
room; M2 is the depth that makes it automatic and survivable live.

## The M1/M2 dedup (THE decision to lock)

The risk is repetition: M1 already taught decompose and construct. M2 must deepen, not restate. The
split:

- **M1 owns the loop as two working halves** on clean questions: L1 decompose + identify-signal (the
  three-part parse, the four signal categories); L2 construct + stress-test (build backward, the named
  scaffolds, the one-line stress test).
- **M2 owns one step per lesson, at depth, on the hard cases**: ambiguous and level-dependent
  decomposition; reading signal in real time; delivering the answer out loud and recovering mid-answer;
  the systematic weak-answer audit. M2 assumes M1 cold and never re-teaches the basics; it opens each
  lesson by naming what M1 established, then goes past it.

If this split is wrong, say so at lock; it determines all four lessons.

## Locked-on-the-blueprint decisions

1. **Stage = module.** Same ICM shape; reads its sources, writes `build-log/answer-engineering/m2/`,
   hands the deepened voice forward to M3.
2. **Held to the three contracts** (AUTHORING, STANDARDS, STYLE) + the now-locked M1 voice exemplar
   (`src/README.md` + the two M1 lessons). Cold workers get all of it in-brief.
3. **Cadence steps up to the house shape:** overview + 4 lessons + 4 exercises (M1's 2+2 was the
   framework opener; "in detail" earns the full four-lesson module, matching Just Python's cadence).
4. **No fabrication; ground every example in the real `asdg` ore + the live MS-Learn connector where it
   fits** (the JP M2/M3 fix, already clean in AE M1).

## Proposed M2 split (overview + 4 lessons, one Algorithm step each, at depth)

| # | Lesson (slug) | One idea (the depth beyond M1) | Source slice |
|---|---------------|--------------------------------|--------------|
| 0 | `00-overview` | M1 gave you the loop; M2 is the expert's internal monologue at each step. | M1 recap + blueprint |
| 1 | `the-question-behind-the-question` | Decompose, deeper: the latent signal under the stated one, the follow-up that reveals the real probe, and how the primary hypothesis shifts with role level (senior vs staff) and a curveball framing. | taxonomy ingredient + leveling ore (asdg 05/06) |
| 2 | `reading-the-room` | Identify the signal in real time: the interviewer's follow-ups and reactions are data; calibrate the hypothesis to company, role, and level as the conversation moves; the clarifying-question as live signal. | pitfalls (communication) + asdg 06 trends |
| 3 | `thinking-out-loud` | Construct, live: the internal monologue made audible, narrating reasoning without losing the thread, the two-minute and thirty-second versions of one answer, and recovering when you realize mid-answer you have drifted. | frameworks ingredient (SPIDER transcript) + asdg 05 out-loud guide + MS-Learn (live eval/observability narration) |
| 4 | `the-weak-answer-audit` | Stress-test, systematic: run the full pitfalls catalog as a self-audit; the "could a weak candidate say this" failure modes by category; the senior-vs-staff bar. | pitfalls catalog ingredient (asdg 03) |

## Ore augmentation (the first move)

M1's ingredient (`ingredients/source/answer-engineering/asdg-{question-taxonomy,interview-frameworks}.md`)
covers most of M2. One gap: the **delivery and leveling** material is not yet distilled. A short
augmentation pass produces `ingredients/source/answer-engineering/asdg-delivery-and-leveling.md` from
the un-distilled ore (asdg `04-whiteboard-exercises` real-time motion, `05` out-loud/2-min/30-sec
practice guide, `05`/`06` leveling and senior-vs-staff bar). Author against the ingredient, not raw vault.

## The compounding throughline (STANDARDS Part 3) — real reuse, not restated

M2 EXTENDS the M1 prep dossier and the validator; it does not start a new one:

- `decomposition-log.md` gains a **hard-cases** section: re-decompose three questions at senior and at
  staff level, showing how the primary hypothesis shifts. (Ex1.)
- new `practice-log.md`: out-loud practice records, two answers each with a 2-minute and a 30-second
  version, self-scored. (Ex3.)
- new `audit-log.md`: take two of your own M1 `answers-log.md` answers and run the full pitfalls audit.
  (Ex4.)
- `reading-the-room` exercise adds a stated-vs-latent **signal map** for three questions across two
  company contexts. (Ex2.)
- **`check_prep.py` grows to v2**: it imports/extends the M1 checks and adds validation for the new logs
  (the validator-as-throughline compounding the STANDARDS contract reserves for later modules; M8 will
  compose the whole dossier and grade it).

## The fleet plan (orchestration)

**Conductor-direct, no handler tier** (one small cluster, per the JP A/B and AE M1). Round 1: one Sonnet
worker runs the delivery/leveling augmentation; the conductor authors `00-overview` and updates SUMMARY.
Round 2: four Sonnet lesson-writers (one each) + one exercises/validator worker, parallel, each briefed
with the three contracts + the M1 voice exemplars + the ingredient + the connector instruction. The
conductor runs the Zinsser + STYLE + STANDARDS review gate on every draft, fetches every MS-Learn
citation live to confirm it (no fabrications, no fourth-wall leaks like the "the ore"/"Example N" ones
caught in M1), and reconciles the shared `check_prep.py` v2 so it stays runnable.

## Open decisions for lock

1. **The M1/M2 dedup split** (above) — the load-bearing call.
2. **Cadence at 4 lessons** vs collapsing to 3 (e.g., merging decompose+identify depth). Recommend 4:
   one step per lesson is the cleanest one-idea-per-lesson fit and matches the house cadence.
3. **`check_prep.py` v2 extends in place** (one validator grows across modules) vs a per-module checker.
   Recommend extend-in-place: it is the real artifact-compounding the book is supposed to demonstrate.

On lock: the fleet augments the ore + authors M2, VERIFY gates it (voice + claims + grounding + the
extended validator runs), BUILD/TEST runs `mdbook build` + `check_prep.py` v2 + pytest, and the stage
stops at `GATE-APPROVE-SHIP` before folding into `src/` and `exercises/`.
