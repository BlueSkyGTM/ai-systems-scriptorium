# Influence Stories

Most behavioral answers stop where the work stopped. You shipped the feature, you fixed the model, you hit the metric. The interviewer writes it down and moves on. But a specific class of questions is not asking what you built: it is asking what you changed, for people who were not you.

"Tell me about a time you led a technical initiative without formal authority." "Describe a situation where you had to convince others to adopt a new approach." "Tell me about a time you raised an ethical concern." These questions probe a signal the behavioral bank names as the staff bar: did the candidate move from "I shipped" to "I changed what others could ship"?

This lesson walks the Algorithm through two of those questions end-to-end. The goal is not a script; it is the construction logic, so you can apply the same moves to your own experience.

## What the Interviewer Is Reading For

The influence signal category sits at the intersection of communication and judgment. The hiring hypothesis, grounded in the behavioral bank, is: does this candidate leave organizational artifacts, processes, standards, patterns, that outlast the individual project?

Senior engineers are evaluated for technical depth. Staff engineers are evaluated for whether they multiply others. An influence story that ends at "I convinced my team" is a conflict story. An influence story that ends at "and that became the template we now use" is a staff story.

Two secondary signals ride along: first, how the influence was exercised. The bank's worked examples show influence operating through alignment of incentives, concrete evidence, and proposed alternatives, not persuasion contests. A story framed as "I convinced them I was right" reads as ego, not leadership. Second, what the candidate did when the influence did not immediately work. Example 6 shows the key move: after being overruled, the candidate converted the lost argument into cheap guardrails and a documented record. Stopping at "I disagreed but deferred" fails the signal.

## Worked Example A: The Ethical Concern Story

**Question:** "Tell me about a time you raised an ethical concern about an AI system."

**Step one: identify the signal.** This question sits inside Theme 5 of the behavioral bank: Responsible AI. The interviewer is not testing whether the candidate has ethics; they are testing whether the candidate can act on an ethical concern in a way that is organizationally effective. The trap is framing the concern as a moral objection. The signal is framing it as a problem with a proposed solution.

**Step two: what the Algorithm needs.** Situation: a specific project with a specific bias risk, not a general belief that AI bias is bad. Task: the candidate's responsibility to raise it, and the actual difficulty (the risk of being dismissed as a blocker). Action: the concrete moves, especially the reframing. Result: a measurable outcome. Learning: what the candidate would carry forward.

**Step three: build toward the signal.** The bank's Example 3 gives the construction materials. The situation: a resume screening system in development, training data heavily skewed toward graduates of a small set of universities. The task: raise the concern without being sidelined. The candidate does not open with a moral argument. The first move is to quantify: 80% precision on graduates of top universities, 45% on state school graduates with equivalent qualifications. That number does the work. A vague concern is a blocker. A number attached to a concern is a risk, and the bank notes the candidate explicitly frames it as a business and legal risk, citing recent litigation in the space.

The second move is to arrive with options, not objections. Two specific proposals: rebalance the training data for demographic representation, or restrict the model to matching rather than ranking with mandatory human review on all candidates. Presenting alternatives converts the candidate from someone stopping the project into someone steering it.

**Step four: name the unfakeable specificity.** The result: a three-week launch delay, a system that performed consistently across demographics, and fairness metrics that became the evaluation standard for all ML models the team built afterward. That last detail is what separates a senior answer from a staff answer. The concern was not just addressed; it created an organizational artifact, a fairness evaluation suite that outlasted the project.

**Step five: the Learning.** The candidate's extracted lesson is precise: framing ethical concerns in terms of business risk makes them actionable, and raising them early with proposed solutions is more effective than waiting until problems are entrenched. The learning is generalizable and shows the candidate's model for future behavior, not just a reflection on the past event.

**What the interviewer writes down.** The candidate quantified the bias before raising it. The candidate arrived with options. The concern shipped as a standard. This is influence through evidence and alignment, not argument-winning. The staff signal is present.

## Worked Example B: The "Concern Overruled" Story

**Question:** "Describe a time you raised a concern and the team decided against you. What did you do?"

**Step one: identify the signal.** This question is often categorized as conflict, and it is, but at the influence level it is testing something more specific: what does this candidate do with a lost argument? The bank places it in the influence category because the decisive move is not the disagreement; it is what the candidate builds after the disagreement ends.

**Step two: what the Algorithm needs.** The situation requires a real concern with real stakes, not a trivial preference overruled. The task must show the candidate understood their role: ensure the decision was made with full information, then either escalate or commit. The action is where most candidates underdeliver; ending at "I disagreed but deferred" reads as passive. The result and learning need to show the constructive work that followed.

**Step three: build toward the signal.** The bank's Example 6 gives the construction. Before a product launch, the candidate flags that the agent's tool permissions are broader than the feature requires: it has write access to systems it only needs to read. Leadership weighs the delay against the launch commitment and decides to ship, with a fast-follow ticket. The candidate disagrees with that call.

Here is where the construction diverges from a conflict story. The candidate does not relitigate. The next move is to convert the lost argument into cheap guardrails that fit inside the launch window. Two mitigations, both specific: an audit log on the write paths, an anomaly alert on write volume. Both accepted. The candidate also writes the risk down concretely, with a specific blast radius if the agent is prompt-injected and a realistic attack path, and logs the disagreement in the decision record.

**Step four: name the unfakeable specificity.** Three weeks after launch, the anomaly alert fires, not on an attack but on a misconfigured integration test. The alert proved the monitoring worked. The permission scoping shipped a month later, prioritized off the back of that signal. The candidate's work after the lost argument directly accelerated the fix.

**Step five: the Learning.** The candidate's extracted lesson: being overruled is not the end of the job. Converting a lost argument into cheap guardrails and a written record is usually worth more than winning the argument, and builds the credibility that makes the next concern land harder. The learning closes the loop: influence is a long game, and a candidate who treats a lost argument as the end has misunderstood the role.

**What the interviewer writes down.** The candidate disagreed, documented the risk concretely, and built monitoring instead of relitigating. The monitoring worked. That is the organizational artifact. The staff signal is present.

## Influence-Specific Failure Modes

The behavioral bank names five failure modes specific to this category. Run these as a checklist against your own stories before you use them.

**"We" without "I changed."** An influence story that describes a team outcome without naming the candidate's specific move is a participation story. "We established a template" is weaker than "I proposed the collaboration structure, which the team adopted as the template for research-to-production handoffs." The second version names the move; the first does not.

**Influence-as-winning.** Framing the story as convincing others you were right signals low calibration. The bank's positive models, Examples 3, 4, and 6, all show influence operating through alignment of incentives and concrete evidence. A candidate who tells it as a persuasion contest is describing a different skill.

**Stopping at the decision outcome.** If the story ends at "they rejected my concern," the candidate has answered two-thirds of the question. The interviewer is waiting for what came next: the guardrails, the written record, the alternative path forward.

**Ethics framed as obstruction.** Example 3 shows the correct framing: a business and legal risk with proposed solutions. The failure mode is presenting as a moral blocker rather than a problem-solver who surfaced a risk. Interviewers do not want a candidate who slows teams down; they want one who surfaces the cost of a risk before it lands.

**No questions for the interviewer.** This failure mode matters specifically in this category. A candidate who has raised ethical concerns or led cross-functional initiatives and has no questions about the company's processes for doing the same is missing an opportunity to demonstrate the very mindset the questions are testing.

## Weak-Answer Audit

**The weak version:**

"I noticed our ML model seemed biased toward certain candidates, so I brought it up with the team. We had a conversation about it and decided to add some fairness checks before launching. I thought it was important to consider these things and I'm glad we did."

**Why it fails.** The signal the interviewer is reading for is nowhere in this answer. There is no quantification; "seemed biased" is a vague impression, not a finding. There is no named move by the candidate: "we had a conversation" describes a meeting attended, not an action taken. There is no concrete outcome; "fairness checks" is a noun, not a result. The learning is a generic values statement. The organizational artifact is absent entirely.

Against the bank's failure modes: "we" is doing all the work, "I changed" is missing, and the influence is framed as a good-citizenship move rather than a technical and business intervention. The answer could be given by someone who sent one Slack message and then watched others fix the problem.

**The fix.** Quantify the problem before raising it. Arrive with two concrete proposals. Name the specific outcome, including the metric that changed and the standard that persisted. The Learning step must name what the candidate would do differently or earlier, not just express satisfaction. The story is not "I flagged bias"; it is "I quantified the bias, reframed it as a legal risk, proposed two alternatives, and the fairness evaluation it produced became the standard for all ML models the team shipped after." That version is unfakeable. Every specific detail either exists in the candidate's memory or it does not.

## Core Concepts

- The influence signal tests whether the candidate leaves organizational artifacts, processes, patterns, and standards, that outlast the individual project; an answer that ends at "I shipped" clears the senior bar and misses the staff one.
- Influence in the bank's positive examples operates through alignment of incentives and concrete evidence, not persuasion; a story framed as "I convinced them I was right" reads as a different, weaker signal.
- When the influence does not work immediately, the decisive move is what the candidate builds after the lost argument: cheap guardrails, a written record, a documented risk; stopping at "I deferred" fails the signal.
- Quantification is the tool that converts a concern from an opinion into a finding; "seemed biased" is invisible to an organization; "45% precision versus 80% on equivalent credentials" is a call to action.

<div class="claude-handoff" data-exercise="exercises/module3/influence-stories/">

**Build It in Claude Code:** select one influence story from your own experience, map it to the STAR-L scaffold, identify which of the five failure modes it risks, then run the weak-answer audit: write the weak version, name exactly where it fails the signal, and write the fix. Log both versions and the audit verdict to your behavioral bank.

</div>
