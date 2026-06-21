# Construct the Answer

You have decomposed the question. You know the primary signal. You have a hypothesis in your
head: what this interviewer needs to see demonstrated.

Now you have to demonstrate it.

This is where most preparation fails. Candidates who have done the decomposition work
correctly still answer poorly because they conflate "aimed at the right signal" with "good
enough." Signal identification is necessary; it is not sufficient. The construction step
decides whether your answer actually delivers the evidence the signal demands, or gestures
toward it.

## The Construction Principle

A strong answer has three properties. It is specific enough that a weak candidate could not
give it. It is structured enough that the interviewer can follow the reasoning. It is complete
enough to close the loop on the hypothesis.

Specificity is the most important of the three and the most commonly abandoned under pressure.
When you are nervous, you reach for the general case. "I used eval-driven development" instead
of "I built three binary judges: one for groundedness, one for answer relevance, one for
format compliance; calibrated each against fifty labeled examples from our support queue; and
set the groundedness judge as a hard gate in CI." The first sentence is a claim. The second is
evidence.

Structure matters because the interviewer is pattern-matching in real time. A behavioral
question answered with a coherent situation-action-result arc is easier to evaluate than a
narrative that covers the same ground in a different order. Structure is not about filling in
a template; it is about making the reasoning visible so the interviewer can follow it.

Completeness means you close the loop. If the hypothesis is "this candidate makes defensible
calls under uncertainty," your answer is not complete until the interviewer can see the
decision, the reasoning behind it, and the outcome. A story that ends with "we made the
decision" without saying what happened is not complete.

## The Construction Move

Build the answer in reverse. Start from the hypothesis, not from the beginning of the story.

**What does the hypothesis require as evidence?** The judgment-under-uncertainty hypothesis
requires: a real decision (not "I contributed to the discussion"), explicit uncertainty (what
you did not know and why), and a defensible reasoning process (not luck, not authority, but
logic you can trace). Those three things are your required outputs. Everything else is optional
context.

**What is the shortest path to the evidence?** Now find the story or explanation that delivers
those outputs in the fewest steps. The shortest path is not always the chronologically first
path. You do not have to start at the beginning. You can start with the decision, then unpack
the uncertainty, then describe the reasoning. Or start with the constraint, then the options
you saw, then the call you made. Choose the order that gets to the evidence fastest.

**What should you cut?** Everything that does not move you toward the evidence. Background
that sets context is valuable up to the point where the interviewer understands the stakes.
After that point, more background is overhead. The ratio to aim for: roughly 20% context, 60%
the actual evidence, 20% result and reflection.

## Worked Example: Behavioral

Question: "Tell me about a time you pushed back on a product decision."

Decomposition (already done): ownership + communication/influence. Primary hypothesis: "This
candidate can operate with authority in a real organization; they do not just implement
whatever they are handed."

Construction: What does that hypothesis require? A real pushback (not a suggestion, a
conversation where the candidate actually tried to change something). A specific reason for the
pushback (technical, quality, risk). An outcome (did it work? what happened?). Optional but
valuable: evidence of how they calibrated the pushback (tone, timing, who they brought in).

Now find the story. Select the example where the pushback was clearest and the reasoning was
most defensible. Lead with the decision being made and why you disagreed: "The feature we were
building sent evaluation requests synchronously during user sessions; I flagged that the
p99 latency would violate our SLA." That sentence delivers the evidence in two lines:
specific technical concern, connected to a real stake.

Then: what you did. Not "I raised concerns" but "I ran a quick load test, brought the numbers
to the PM, and proposed moving eval to an async queue with a daily dashboard instead of
real-time blocking." Specific action. Then: outcome. "The design changed. We shipped with the
async path; the p99 held."

Total answer: under two minutes. Delivers every piece of required evidence. No weak candidate
can give that answer because the technical specificity is real.

## Worked Example: Technical Depth

Question: "How do you evaluate an LLM feature before shipping?"

Decomposition (already done): technical depth, secondary ownership. Primary hypothesis: "This
candidate has a real evaluation framework, not a vague intention."

Construction: What does the hypothesis require? A named framework (not a category label, actual
techniques). Production grounding (the answer should reflect real constraints). Some evidence
of calibration or rigor (not just "I run tests").

Build from the framework outward. Do not narrate the history of eval; name your approach and
justify it. "I use a three-layer eval stack: deterministic checks for format and schema
validation; LLM-as-judge for semantic quality using binary criteria, one judge per criterion;
and calibration against a labeled set before I trust any judge score." That is the framework.
Three sentences, defensible, specific.

Then production grounding: "In practice the bottleneck is calibration — building the labeled
set takes time, and the judge is meaningless without it. I prioritize the RAG triad first:
context relevance, groundedness, answer relevance; those are the three independent failure
modes and they decompose the pipeline so you know which component broke." Now the interviewer
can see you have shipped this, not just read about it.

Optional specificity: name a tool or a number. "We target Spearman rho of 0.7 or better
between judge scores and human labels before we gate on the judge in CI." That is the kind of
detail that separates operational experience from study.

## The Stress Test

Before you finish, run one check: could a weak candidate give this answer?

If yes, add one specific thing. A number, a decision you made that had real stakes, a failure
mode you caught. Specificity is the only defense against the vague-positive answer that sounds
good and proves nothing.

The stress test is internal. You are not asking the interviewer "was that specific enough?" You
are asking yourself, in the final seconds before you stop talking, whether you actually
delivered the evidence or only pointed at it.

## What to Do When You Do Not Have a Good Example

This happens. The question lands in a category where your experience is thin, or your best
example from that category is confidential, or you genuinely cannot remember one in the moment.

The correct move is not to fabricate, not to pivot to a tangentially related story and hope the
interviewer does not notice, and not to apologize. The correct move is to be honest about the
constraint and demonstrate reasoning anyway.

"I haven't had a direct experience with that at production scale; but here is how I would
approach it:" followed by a technically grounded answer is better than a weak fabricated
example. It demonstrates judgment about what you know and what you do not, which is itself a
signal. Integrity about scope is a competency.

If the gap is real, note it; plan to fill it. The example bank in Module 7 exists so that this
gap narrows with practice.

## Core Concepts

- Construction starts from the hypothesis, not from the beginning of the story; identify what
  evidence the hypothesis requires before choosing an example or ordering a response.
- Specificity is the critical property: a strong answer names details no weak candidate can
  supply; a vague answer that points at the right signal is still a weak answer.
- The construction ratio: roughly 20% context, 60% evidence (the decision, reasoning, and
  action), 20% result and reflection.
- The stress test runs before you stop: ask whether a weak candidate could give the same answer;
  if yes, add one specific thing.
- When a good example is not available, honest scoping plus demonstrated reasoning is better
  than a fabricated or tangential example; integrity about scope is a competency.

<div class="claude-handoff" data-exercise="draft/exercises/02-signal-to-answer/">

**Build It in Claude Code**: Take five questions from the worked-example bank, run the full
four-step Algorithm on each (decompose, identify signal, construct, stress-test), and write
out your constructed answers. Then load the rubric and score each answer against the three
construction properties: specificity, structure, completeness.

</div>
