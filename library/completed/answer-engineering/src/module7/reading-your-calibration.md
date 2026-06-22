# Reading Your Calibration

The scorecard is a mirror. It does not flatter you, and it does not care how confident you felt
after your last rep. It counts.

Once you have reps in your deliberate-practice log, you run the scorer from the `exercises/prep/`
directory:

```
python calibrate.py
```

What comes back is not a grade. It is a diagnosis, section by section, ending in a single verdict
and a drill list. Here is a real scorecard, and here is what each section tells you.

## The Sample Scorecard

```
Answer Engineering Calibration Scorecard
========================================

Reps logged: 10 across 5 categories
  (1 malformed rep(s) skipped: check the field names and scores.)

Per-category reps (need >= 3 each):
  ownership        3  ok 
  conflict         3  ok 
  failure          1  GAP  need 2 more
  influence        0  GAP  need 3 more
  systems-design   3  ok 

Step calibration (across all reps):
  Decompose    strong 8   partial 2   weak 0
  Signal       strong 6   partial 3   weak 1
  Construct    strong 5   partial 5   weak 0
  Stress-test  strong 2   partial 4   weak 4    <- weakest step

Readiness by category (latest rep must have no weak step):
  ownership       READY
  conflict        NOT READY (latest rep has a weak step)
  failure         NOT READY (need 2 more rep(s))
  influence       NOT READY (need 3 more rep(s))
  systems-design  READY

VERDICT: NOT READY. Drill: conflict (clean rep); failure (reps); influence (reps); Stress-test step across the bank.
```

## Reading Each Section

**Reps logged.** Ten valid reps were parsed; one was skipped because a field name or score value did
not match the schema. If you see a skipped count, open your log and find the malformed entry. The
scorer tells you exactly what to check.

**Per-category reps.** The categories the book covers are ownership, conflict, failure, influence, and
systems-design. Each needs at least three reps before the scorer will consider it practiced. In this
scorecard, failure has one rep and influence has none: both show `GAP` with the shortfall printed. The
`ok` mark on ownership, conflict, and systems-design only means the count is satisfied; it says nothing
yet about quality.

**Step calibration.** This is the section most people underread. It shows, across all ten reps, how
often each of the four Algorithm steps scored strong, partial, or weak. In this scorecard, Decompose
is nearly clean. Stress-test has four weak marks out of ten, flagged as the weakest step. That number
means something specific: on four of ten reps, you reached the final step and the answer did not hold.
That is not a conflict problem or a failure problem. It is a method problem, and it shows up the same
way everywhere.

**Readiness by category.** This is where the count and the quality check combine. A category is READY
only when it has at least three reps and its most recent rep has no weak step. In this scorecard, conflict
has the count, but the latest conflict rep has a weak step: NOT READY. Failure and influence are NOT READY
because the reps are not there yet. The reason matters because the fix differs.

**Verdict.** The scorer names your drill list explicitly. Here it is three items: get a clean conflict
rep, log two more failure reps, log three more influence reps, and address the Stress-test step across
the whole bank. When every category clears both thresholds, the verdict flips to READY and the scorer
exits 0.

## Two Different Reasons a Category Is Not Ready

A category can fail readiness for two reasons, and the fix is not the same for both.

**Under-practiced** means the count is below three. The fix is volume: log more reps in that category,
on fresh questions, scored honestly. Do not log the same question twice.

**Not clean** means the count is fine but the most recent rep had a weak step. The fix is quality: do
one rep on a fresh question in that category and clear the weak step. Adding volume without fixing the
step will not move the verdict; the scorer checks the latest rep, not the average.

The distinction also matters for how you prioritize. If a category is both under-practiced and weak on
a step, fix the volume first; you cannot have a clean "latest rep" when there is only one.

## The Weakest-Step Signal

When a step is flagged as weakest across the whole bank, that is a different kind of problem from a
thin category. Four weak Stress-test marks spread across ownership, conflict, failure, and systems-design
means the step itself is not landing. You are not forgetting to do it; you are doing it and it is not
working.

The targeted fix is to run reps specifically to practice that step, across categories. Take a question
from any category where you have at least one rep, run the full Algorithm, and hold yourself to a clear
standard on Stress-test before you log the score. A category rep that clears the weakest step does
double work: it counts toward readiness and it tightens the step distribution.

## The Practice Loop

The loop is not complicated. Read the scorecard, identify the single biggest gap, drill it, and re-run
the scorer.

Pick one gap at a time. If influence is empty, that outweighs a weak Stress-test mark in conflict; fill
the empty category first. If every category has the count but one has a dirty latest rep, fix that rep
before you log volume elsewhere. The verdict tells you what the scorer sees as the bloat; the drill list
orders it.

After each set of reps, run the scorer again:

```
python calibrate.py
```

Watch the numbers. A weak mark that drops from four to two is movement. A category that clears from
`GAP` to `ok` is movement. The loop ends when the verdict reads READY and the process exits 0. Until
then, the scorecard is telling you exactly where to spend the next session.

Readiness is not a feeling you arrive at. It is an exit code the scorer awards when the evidence supports it.

## Core Concepts

- A category can be NOT READY for two reasons, under-practiced or latest rep not clean, and the fix
  differs: volume closes the count gap, a targeted rep closes the quality gap.
- A step that is weak across many categories signals a method gap, not a category gap; drill the step
  itself across the whole bank.
- The practice loop is score, identify the single biggest gap, drill it, re-run; the scorer exits 0
  only when every category is both practiced and clean.
- Readiness is an exit code, not a confidence level.

<div class="claude-handoff" data-exercise="exercises/module7/reading-your-calibration/">

**Try It in Claude Code:** run the calibration scorer on your log, identify your single biggest gap (weakest step or thinnest category), run three targeted reps to close it, and re-run the scorer to confirm the numbers moved.

</div>
