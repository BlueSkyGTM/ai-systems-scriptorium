# Influence Stories

At the staff level you are hired for leverage, and the behavioral round is where interviewers
decide whether you have it.

## The Signal

Every influence question tests the same hypothesis: does this candidate move people without
formal authority, and does their work change what others can build? The interview is not asking
whether you convinced someone. It is asking whether you left anything behind.

That gap between winning an argument and leaving an organizational artifact is exactly where
senior answers stop and staff answers begin. A senior-level answer says "I shipped X and it
worked." A staff-level answer says "I shipped X, which became the standard the team applies to
every new integration." The artifact is the proof of leverage: a pattern, a template, a
documented process, a set of metrics that outlasts the project that produced them.

Decompose any influence question the same way you decompose any behavioral question. What is the
hypothesis? Can this person lead without authority, and at the staff level, do they leave
organizational artifacts behind? Build your STAR-L toward that evidence, and stress-test it with
one question: if you removed yourself from the story, does anything still exist?

## The Failure Modes

Four patterns kill influence answers. Know them before you construct.

**Influence-as-winning.** The candidate frames the story as a persuasion contest they won. Strong
influence does not work through argument victory; it works through aligning incentives, proposing
concrete alternatives, and making the right call obviously attractive. If your story reads as "I
convinced them I was right," you have described a debate, not leadership.

**"We" without "I changed."** The influence story must name your specific move. "We established a
new template" attributes nothing to you. The staff answer is personal and precise: "I proposed the
collaboration structure, which became the template the team now uses." Ownership lives in the verb
and the "I."

**Ethics framed as obstruction.** When an influence story involves raising a safety or fairness
concern, the failure mode is presenting yourself as a blocker who stopped a project. The strong
move is framing the concern as a business and legal risk, proposing two options, and letting the
decision-maker choose. You are a problem-solver who surfaced a risk, not a conscience who said no.

**Stopping at the decision outcome.** Many candidates end the story when the decision is made. The
influence signal lives in what happened after: what changed for others, what became the standard,
what the team could build next that it could not build before. If your story ends at "and they
agreed with me," it is missing the organizational artifact that proves the influence was real.

## Worked Example One: Raising a Fairness Concern

The question: "Tell me about a time you raised an ethical concern about an AI system."

**Decompose.** The hypothesis is not "does this candidate have a conscience?" It is: "can this
candidate identify an AI-specific risk, surface it in a way that changes what the team does, and
leave an organizational trace that protects future work?" The signal is technical influence,
category-specific: the ability to reframe a values concern as an operational one and move the
organization without authority.

**What evidence does the hypothesis require?** A concrete, quantified problem (not a vague
discomfort), a reframing that makes the concern actionable for a business audience, proposed
options that fit inside the team's actual constraints, and a result that extended beyond this
project.

**Construct the STAR-L.**

Situation: while building a resume screening model, the training data was heavily weighted toward
graduates of a small number of universities. The task was not just technical: raising the concern
in a way that would be taken seriously without being dismissed as blocking the launch.

The action is where the staff signal lives. The first move was quantification: 80% precision on
graduates of top programs versus 45% precision on candidates with similar qualifications from
other schools. That gap is not a values claim; it is a measurement of model behavior. The second
move was reframing: before any meeting, this was presented as a business and legal risk, citing
recent litigation over biased automated hiring decisions. The third move was proposing options
rather than reporting a problem: rebalance the training data for broader demographic
representation, or constrain the model to matching rather than ranking and route all candidates to
human review. Those two options fit different risk tolerances. The team chose the first option and
added fairness metrics to the evaluation suite.

The result: a three-week delay in launch, a model that performed consistently across demographic
groups, and an evaluation requirement that became the standard for every subsequent ML model the
team shipped.

**Stress-test.** Could a weak candidate give this same answer? No. The 80% versus 45% precision
gap is a specific measurement that required running the analysis. The two options are concrete
enough that the team could choose between them. The fairness metric requirement that extended to
all future models is the organizational artifact: it exists after you do, and it changes what the
next engineer has to do before they ship.

The move: decompose the concern into a quantified problem, reframe it in the language the
decision-maker cares about, propose options rather than blocking, and make sure the result
outlasts the project. The detail that earns this answer its credibility is not the ethical
position; it is the measurement that made the ethical position undeniable.

## Worked Example Two: Converting a Lost Argument

The question: "Describe a time you raised a concern and the team decided against you. What did
you do?"

**Decompose.** This question is listed under conflict in some interview frameworks. When you
foreground what happened after the decision, it becomes an influence question: did the candidate
convert a lost argument into something durable, or did they accept the outcome and move on? The
hypothesis is: can this candidate operate constructively after being overruled, and do they leave
a record that protects the organization even when they lose?

**What evidence does the hypothesis require?** Proportional escalation (the concern was real and
the candidate took it seriously, but did not overstep), a constructive action inside the decision
window, and a result that shows the concern was valid even after the argument was over.

**Construct the STAR-L.**

Situation: before a launch, the agent's tool permissions were broader than the feature required.
It had write access to systems it only needed to read. Leadership weighed a two-week delay against
existing launch commitments and decided to ship as-is, with a prioritized follow-up ticket.

The task required a judgment call: disagree with the decision or commit to it? The job was to
ensure the decision was made with full information. After that, the choice was escalate or commit.

The action: rather than accepting a vague "this is risky," the concern was written down precisely.
Specifically: the blast radius if the agent were prompt-injected, including a realistic attack path
and a description of which systems were exposed. Then, two mitigations that fit inside the existing
launch window were proposed: an audit log on the write paths and an anomaly alert on write volume.
Both were accepted. The disagreement was documented in the decision record, and the launch
proceeded without relitigating the argument in hallway conversations.

The result: the launch was fine. Three weeks later, the anomaly alert fired on a misconfigured
integration test, not an attack, but it validated that the monitoring worked. The permission
scoping shipped a month later, prioritized partly because of that signal. The written decision
record, the audit log, and the alert together formed the organizational trace: a set of artifacts
that outlasted the argument.

**Stress-test.** The blast-radius analysis with a realistic attack path is not something any
candidate can fabricate. The two specific mitigations were concrete enough to be accepted inside
the launch window. The documented disagreement in the decision record is the artifact that matters:
it proves the concern was raised with specificity, protects the team if the risk materializes, and
builds the credibility that makes the next concern land harder.

The move: convert the lost argument into cheap guardrails and a written record. That conversion is
the influence, not the original disagreement. The candidate who ends the story at "I disagreed but
deferred" has told a conflict story. The candidate who ends it at the audit log, the alert, and the
decision record has told an influence story.

## The Distinction Between These Two Examples

Both cases involve raising a concern. The resume-screening case foregrounds reframing: the ethical
concern became a business risk, and the organizational artifact was a new evaluation standard. The
permissions case foregrounds conversion: a lost argument became a set of operational guardrails, and
the organizational artifact was the combination of documented disagreement and live monitoring. The
move depends on your situation, not on which story sounds better. What does not depend on the
situation is this: if you cannot name what still exists after you walked out of the room, you have
not yet told an influence story.

## Core Concepts

- The influence signal is organizational: the staff-level hypothesis is whether your work changed what others could build, not whether you convinced anyone.
- Influence operates through aligned incentives and proposed options, not argument-winning; framing a concern as a business and legal risk is more durable than framing it as a moral position.
- The organizational artifact is the test: if you remove yourself from the story, what still exists? A pattern, a standard, a decision record, a monitoring alert.
- Stopping at the decision outcome is the category-specific failure mode; the influence signal lives in what happened after, not in whether you were right.

<div class="claude-handoff" data-exercise="exercises/module3/influence-stories/">

**Try It in Claude Code:** write one of your own influence stories that names the organizational artifact it left behind, run the full Algorithm and the weak-answer audit on it, and add it to your behavioral bank.

</div>
