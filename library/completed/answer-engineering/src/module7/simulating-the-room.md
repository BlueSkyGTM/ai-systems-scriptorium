# Simulating the Room

The room does not give you ownership questions in a block, then conflict questions in a block, then a
systems-design prompt with a polite warning that the systems-design section is starting. It mixes
categories, imposes a clock, and follows up on whatever you just said. Practice that does not do the
same thing is rehearsal in a mirror: it shows you your reflection, not the room.

## Mixed Practice Is the Real Signal

Block practice, ten ownership reps in a row, inflates your scores because the first two reps warm you
up. By rep four you are calibrated on ownership framing. You feel ready, and you are ready, but only for
the tenth ownership question in a sequence. That is not a situation you will encounter.

The signal you actually need is this: a random category, a clock, and no warmup. Pick a question from
the bank without looking at the label first. Run the full Algorithm. Score it. Then pick another
question from a different category and do it again. The category jump is the real test, because the
room will jump categories without announcement and watch whether your framing holds.

Mixed practice also surfaces the transition cost, the mental shift between "what did I own and deliver?"
and "how would you design a retrieval-augmented generation pipeline at scale?" That cost is real. You
want to find it in practice, not in the room.

After you run a rep, add one follow-up you did not prepare. Not a question from your bank; a probe that
your answer invited. If you said "I drove the rollout decision," the follow-up is: "what did you do when
someone senior disagreed?" If you described a three-tier memory architecture, the follow-up is: "what
breaks first at ten times the load?" The follow-up exposes the seam between your rehearsed answer and
your actual reasoning.

## Timed Practice Is Compression, Not Speed

A behavioral answer has a two-minute budget in most interview loops. Two minutes is enough for a
complete answer; it is not enough for a complete answer plus hedging, plus restating the question, plus
asking whether the interviewer wants more detail at each phase transition. The clock forces compression.
Compression forces you to decide what the answer's center of gravity is, which is a reasoning act, not a
speaking act.

Time yourself. Start the clock when you hear the question. Stop it when you stop talking. If you land
past the two-minute mark, the problem is not that you spoke too fast; it is that you included content
that the answer did not need. Find it and cut it before the next rep.

A systems-design prompt gets more time, roughly 40 to 45 minutes in a real loop. The constraint there is
not total time but phase allocation: you have five minutes for scope, three for prioritization, ten for
initial architecture, 15 for the deep dive, five for evaluation, and five for reliability. Run a
complete SPIDER motion under a timer and look at where you overran. Most candidates overrun the initial
architecture phase because they want to finish drawing before moving on. The room will pull you into the
deep dive before you are satisfied with the drawing. Practice leaving the drawing incomplete on purpose.

## The Readiness Verdict

When you believe you are prepared, you run the calibration scorer.

```
python calibrate.py
```

The scorer reads your practice log and checks two conditions for every category in the bank:
ownership, conflict, failure, influence, and systems-design. First, you have logged at least the
minimum number of reps. Second, your most recent rep in that category has no weak step. Both conditions
must hold for every category before the verdict is READY.

Exit code 0 means READY. Exit code 1 means NOT READY, and the verdict line names exactly what to drill.
It reads like this:

```
VERDICT: NOT READY. Drill: conflict (clean rep); failure (reps); Stress-test step across the bank.
```

Read the drill list as a to-do, in order. The scorer is not editorializing; it is reporting facts from
your log. "Conflict (clean rep)" means your most recent conflict rep had a weak step: go run one clean
conflict rep and log it. "Failure (reps)" means you have not reached the minimum rep count in that
category: log more failure reps. "Stress-test step across the bank" means that step is your weakest
across all reps: drill it explicitly across categories until the distribution shifts.

After each drill, re-run the scorer. The verdict updates when the log updates. You are not trying to
satisfy the scorer; you are moving the numbers by doing the work, and the scorer reads the result.

What READY does not claim is that you will answer every question cleanly in the room. It claims that
you have covered every category recently enough, and that your most recent rep in each category was
clean. That is a stronger claim than "I feel prepared," but it is not a guarantee. A question you have
not seen can still surprise you. What the verdict removes is the possibility that you walked in
under-practiced on a whole category and did not know it.

## The Honest Close

Calibration replaces a feeling with evidence. By the time the scorer exits 0, you have run every
category under a clock, you know which step is your weakest across the bank, and you have logged at
least one recent clean rep in each category. That is what you carry into the room: not a sense of
readiness but a record of it.

The final module takes that record and the whole dossier and grades them together, the way an interview
loop grades a candidate. You have built what it will read.

## Core Concepts

- Mixed practice, randomizing category each rep, is a closer signal than block practice because it
  imposes the category jump and the transition cost the room actually produces; block practice inflates
  scores by warming you up inside a single category.
- Timed compression is a reasoning act: running a behavioral answer inside two minutes forces you to
  identify the answer's center of gravity, and overrunning tells you what to cut, not that you spoke
  too fast.
- Exit code 0 from the scorer means every category meets the minimum rep count and its most recent rep
  has no weak step; it does not mean you will answer every question cleanly, only that no category is
  uncovered.
- The NOT READY drill list is a to-do in order of what to fix: log the missing reps, run a clean rep
  in the category with a weak latest result, drill the weakest step; re-run the scorer after each.

<div class="claude-handoff" data-exercise="exercises/module7/simulating-the-room/">

**Try It in Claude Code:** run a mixed, timed practice session across all five categories, log and score each rep, then run the calibration scorer and drill whatever the verdict names until it reports READY.

</div>
