# The Weak-Answer Audit

You are the last reviewer before the interviewer scores you. The one-line stress test from Module 1 catches the obvious problem: the answer any candidate could give. This lesson turns that single check into a system you can run on any answer, against two bars, in the final seconds before you stop talking.

## Why the Catalog Exists

Weak answers do not look weak from the inside. They feel complete. They aim at the right signal, run the right scaffold, and arrive at a conclusion. What they miss is specific: they describe a move without showing it, name a decision without grounding it, or stop at the architecture diagram when the interviewer was waiting for the failure mode.

The pitfalls that kill offers are not random. They cluster by which step of the Algorithm they attack. Running the catalog as a checklist lets you catch them the same way a code reviewer catches a class of bug, not by reading every line hoping to spot one, but by scanning for the known failure patterns first.

## The Catalog by Step

**Step 1 failures: Decompose.** The most common is jumping to solutions. The answer opens with a tool choice, a vendor, a framework, before the candidate has named the scale, the latency budget, or the compliance constraint. It signals someone who has built things without requirements. A related failure is solving a different problem: the question asked for a lightweight Q&A tool and the answer designed a multi-agent autonomous system. Excitement about a technology overrode the stated need.

**Step 3 failures: Construct.** These are where most offers die, because they are invisible to the candidate.

Skipping the data pipeline is the clearest technical tell. A retrieval and generation architecture that says nothing about how documents get into the system is a RAG answer with a missing third of the system. A beautiful retrieval pipeline is worthless if the ingestion produces garbage chunks.

Ignoring the evaluation layer is the second. The answer describes building the system but not how to know if it works. AI systems fail in ways that are subtle and delayed; without an explicit eval plan, you are describing a prototype you intend to ship without a quality signal.

One-size-fits-all model selection, "the biggest frontier model for best quality," tells the interviewer you have not shipped under a cost constraint. No routing, no cascade, no back-of-envelope on token economics.

Treating prompts as magic is closely related. "And then we prompt the model to..." without naming a system prompt structure, an output format spec, or few-shot examples is not operational experience. It is intent, not implementation.

**Communication failures: they attack the signal regardless of technical content.** Monologuing without check-ins signals you cannot read a room. Not leading with structure makes the interviewer work to follow your reasoning rather than evaluate it. Defending a wrong answer once you have been corrected is the worst of the four: it signals low calibration and tells the interviewer you will be difficult to work with in production, where being wrong is routine.

## Running the Audit

The audit runs after you construct an answer and before you stop talking. Three passes:

**Pass 1: The pitfall scan.** Against each category above, ask whether the answer trips the pattern. Did you name a tool before scoping? Does the answer describe the happy path and nothing else? Does it include an evaluation approach, or does it assume the system works because the components are right? Did you state a prompt strategy or just reference "prompting"?

**Pass 2: The weak-candidate test by signal category.** Apply the stress test by category, not as a single check. For a technical signal, ask whether every claim is grounded: not "I improved retrieval quality" but "hybrid retrieval with RRF fusion over BM25 and dense embeddings, calibrated on a 200-case golden set, lifted our hit rate from 71% to 89%." For a judgment signal, ask whether you made a recommendation or only named tradeoffs: "it depends" without the second half reads as hedging. For a communication signal, ask whether you have been talking for five minutes without a check-in.

**Pass 3: Failure modes and observability.** This is the pass that separates the answer you stop at from the one that keeps going. Every systems-design deep dive ends with two sentences: one on observability (how you know it is working after deployment) and one on failure modes (what breaks first and how you handle it). A candidate who reaches the architecture diagram and stops has answered the easy half of the question. The E and R phases of SPIDER are not polish; they are where the production experience shows.

## The Senior-vs-Staff Bar

The audit has two rungs, and passing the first does not clear the second.

A senior-bar answer owns a system end-to-end: the technical decisions were defensible, the result was quantified, the learning was specific to the AI problem rather than a generic one. Strong. It fails the staff bar if it stops there.

A staff-bar answer shows what the work enabled for others. The result was not just a shipped feature but a platform, a pattern, a standard, a rubric that changed what the team could build next. Where a senior answer says "I built the eval pipeline and it reduced hallucination rate by 40%," a staff answer adds: "and it became the template our team now uses on every new model integration, with the calibration process documented as a runnable script so the next engineer does not have to reconstruct the approach."

The other staff signals are cross-cutting rather than feature-level. A staff candidate names governance unprompted: the eval gaming risk, the audit trail on write paths, the compliance boundary (SOC 2, HIPAA, EU AI Act Article 27) as a constraint the architecture accounts for, not a checkbox on the way out. A senior candidate can be technically precise on all of this and still miss the staff signal because the framing is component-level, not platform-level.

The behavioral version of the gap is equivalent. A senior-level behavioral answer: "I built X and it worked." A staff-level behavioral answer: "I built X, which became the organizational artifact that changed how Y and Z could be built." The staff answer includes a pattern that compounded, not just a feature that shipped.

## Putting It Together

Running the audit in your head takes about ten seconds once the patterns are automatic. Pitfall scan, weak-candidate test by signal category, failure-modes pass. Then ask which bar the answer cleared. If it cleared senior and you are targeting a staff role, add the cross-cutting element: the organizational artifact, the platform-level framing.

The audit does not change your answer; it tells you where to add one specific thing. That is what the stress test was always doing. This is the version that runs against the full catalog, at both bars.

The interviewer scores your answer by asking how many engineers they could swap in who would give the same one. Your job is to make the answer theirs alone.

## Core Concepts

- The pitfalls that kill offers cluster by Algorithm step: jumping to solutions attacks decompose; skipping the evaluation layer and the data pipeline, monologuing, and defending wrong answers attack construct and the signal; the catalog runs faster than a general "could a weak candidate say this" check.
- The weak-candidate test applies by signal category: technical answers need grounded claims with numbers; judgment answers need a recommendation not just tradeoffs; communication signals need check-ins not monologues.
- The senior bar requires a specific, quantified, technically grounded answer no weak candidate could fake; passing it does not clear the staff bar.
- The staff bar requires a cross-cutting, platform-level framing: scope that multiplies others, governance named unprompted, and an organizational artifact (a pattern, a standard, a platform) not just a shipped feature.

<div class="claude-handoff" data-exercise="exercises/module2/the-weak-answer-audit/">

**Try It in Claude Code:** run the full three-pass audit on two of your own answers from the M1 answers log, score each against the senior bar and then the staff bar, and write an audit log entry naming the exact sentence you would add to clear the bar you did not reach.

</div>
