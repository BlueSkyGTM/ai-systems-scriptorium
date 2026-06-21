# The Question Behind the Question

M1 gave you the three-part parse: strip the framing, assign a signal category, name the primary
hypothesis. It works cleanly when one signal dominates. Real loops deliver the harder kind, and
getting them right is the margin between candidates who pass screens and candidates who collect offers.

Three cases M1 does not cover. You need to recognize all three before you speak.

## The Latent Signal

Some questions wear one category on the surface and carry a different one underneath. The stated
words point one direction; context points another.

Take "walk me through the architecture of a production RAG system." On the surface it reads as a
technical depth question. But context changes the hypothesis. If you mentioned a specific retrieval
pipeline two minutes ago and the interviewer immediately followed with this question, they are not
running a survey of RAG patterns. They are checking whether you built the thing you implied you
built: the primary signal has shifted to ownership, with technical depth as the instrument. The
same words, a different probe.

Before you assign a category, register one additional data point: what was said in the thirty
seconds before this question? The interviewer's previous move almost always surfaces the latent
signal; follow-up questions are not random. They are a probe calibrated to what the interviewer
just heard.

## The Follow-Up That Reveals the Real Probe

Miss the latent signal on the first question and the follow-up gives you a second chance, but only
if you treat it as data.

The follow-up an interviewer chooses tells you what they were after in the first question. If you
answered "walk me through the architecture of a production RAG system" by covering the retrieval
and generation stack, and the interviewer follows with "who made the chunking decision?", they have
told you the real probe was ownership all along, not technical depth. The answer they needed was
evidence that you drove the decisions in the system you described, not an architecture diagram.

The follow-up is a second-chance decomposition. Run it: what does this new question reveal about
what the first one was collecting? Then reorient. Most candidates treat a follow-up as a new
question to answer in isolation; the stronger move is to treat it as a correction signal on where
the decomposition went wrong.

Missing one follow-up is correctable. Treating four follow-up questions as four unrelated probes
and never reading the pattern is not.

## How the Hypothesis Shifts With Level

The same question, asked of a senior IC and a staff IC, collects different evidence. The words are
identical. The primary hypothesis is not.

Consider "tell me about a time you led a technical initiative without formal authority." At the
senior level, the hypothesis centers on technical ownership and individual delivery: did you drive
the system, make the call, own the technical direction? The answer that lands is first-person and
specific: what you built, what tradeoffs you made, what the system does.

At the staff level, the hypothesis shifts: not just "can this person drive a system?" but "does
this person change what others around them can do?" The L8+ bar is clear: staff ICs own
orchestration layers and LLMOps platforms that serve all engineering teams. The scope moves from
a system to the platform that enables systems. Multiplying others is not an optional flourish; it
is the primary thing being tested.

What changes in the three-part parse is step three: the primary hypothesis you name.

- **Senior:** "I drive technical initiatives end-to-end and own the outcome."
- **Staff:** "I drive technical initiatives in ways that change what the team can build afterward,
  and I can name the organizational artifact that proves it."

The staff answer must contain that organizational artifact: a platform, a pattern, a standard, a
template other engineers adopted. Without it, a technically strong answer reads as a senior answer
delivered by someone applying for the wrong level.

The third differentiator is ambiguity tolerance that extends into governance. At the senior level,
defensible decision-making under uncertainty is the bar. At the staff level the interviewer checks
whether the candidate thinks structurally about non-deterministic systems: runtime governance,
compliance surfaces, cross-cutting concerns that live above any single feature. "How do you
implement guardrails for an autonomous agent?" at the staff level expects a candidate who surfaces
audit requirements, blast radius, and the review gate that governs the system over time, not just
the guardrails that ship with version one.

## Worked Decomposition: Same Question, Two Levels

Question: "Describe a situation where you changed direction mid-project."

**Senior decomposition.** Literal parse: "changed direction" (judgment call under new information),
"mid-project" (decision made while committed). Primary signal: judgment under uncertainty; ownership
secondary, because the interviewer wants to see you owned the pivot. Primary hypothesis: "I make
defensible direction changes and own the result."

**Staff decomposition.** Same parse. Different primary hypothesis, because the question at this
level carries an additional probe: what was the organizational ripple? Did you manage the impact
across teams, update the standards other engineers depended on, and leave a cleaner system in
place of the original direction? Primary hypothesis: "I make direction changes in ways that don't
create organizational debt for the teams around me, and I can name what I put in place so the new
direction held."

The difference is not the story you tell. It is which part of the story you lead with.

## Core Concepts

- A question's stated category and its actual signal category can differ; the thirty seconds before
  the question almost always surfaces the latent probe.
- The interviewer's follow-up question is a second-chance decomposition: it reveals what the first
  question was actually collecting, and the correct move is to reorient, not answer in isolation.
- The same question asked of a senior IC and a staff IC names a different primary hypothesis:
  senior tests technical ownership and individual delivery; staff tests whether the candidate
  changes what others can do and names the organizational artifact that proves it.
- Ambiguity tolerance at the staff level extends beyond individual decisions into runtime governance
  and cross-cutting concerns; a technically strong answer without that layer reads as a senior
  answer at the wrong level.

<div class="claude-handoff" data-exercise="exercises/module2/the-question-behind-the-question/">

**Try It in Claude Code:** Take three real questions from the taxonomy: "tell me about a time you
led a technical initiative without formal authority," "describe a situation where you changed
direction mid-project," and "how do you implement guardrails for an autonomous agent." For each
one, write out two full decompositions (senior level, staff level), naming the literal parse, the
primary hypothesis for each level, and one sentence on what the answer must include to hold that
hypothesis. Then compare: where does the decomposition stay the same across levels, and where does
it shift?

</div>
