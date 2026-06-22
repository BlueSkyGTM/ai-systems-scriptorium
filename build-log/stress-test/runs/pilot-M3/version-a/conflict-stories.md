# Conflict Stories

Behavioral rounds are where AI Engineers with strong technical records lose offers on a question that has nothing to do with code: can you disagree, hold a position, and still move with the team?

That is the conflict signal, and it is harder to answer than it looks, because the failure modes sit on opposite ends. Defend your position past the point of evidence and you signal low calibration. Roll over without a trace and you signal you do not have real views. The interviewer is watching for the narrow path between them: the candidate who can argue, absorb new information, and then commit, without relitigating the outcome in every hallway conversation for the next month.

## The Signal the Interviewer Is Collecting

Every conflict question is a test of one hypothesis: does this candidate make the team better under disagreement, or worse?

The two patterns the interviewer wants to see are disagree-and-commit and proportional escalation. Disagree-and-commit means you made your case clearly, the decision went a different way, and you executed the decision as if it were your own, because once a team commits, continuing to campaign against it is not principle, it is friction. Proportional escalation means the force of your pushback matched the stakes: you did not treat a color choice and a security risk the same way.

The four failure modes that surface most often in conflict answers:

**Defending past the evidence.** The answer frames the conflict as a situation where the candidate was simply right and the other party was simply wrong. No calibration, no acknowledgment that the other position had merit. This signals a fragile ego, not a strong perspective.

**No specific move.** "We eventually aligned" without naming the action that produced alignment. Alignment is an outcome; the interviewer wants the mechanism. What did you actually do to get from disagreement to a shared direction?

**Relitigating.** The answer reveals, sometimes without meaning to, that the candidate kept campaigning after the decision was made. Side conversations, passive resistance, waiting for the approach to fail. This is the pattern that makes teams dysfunctional.

**Only the technical answer.** Conflict questions are about the human dimension. A candidate who explains why they were technically correct but says nothing about the working relationship afterward has answered a different question than the one asked.

One more: no relationship outcome. A conflict story that ends at the decision, with no sentence about what the working relationship looked like after, reads as a grievance report. You are not describing a dispute; you are describing a collaboration that survived one.

## How to Run the Algorithm on a Conflict Question

Decompose the question first. "Tell me about a disagreement with a colleague about a technical approach" and "Describe a time you raised a concern and the team decided against you" look different on the surface. They are collecting the same signal: the disagree-and-commit pattern. Name that before you reach for a story.

Then build your STAR-L toward the signal, not toward proving you were right. The Result step is not "I was vindicated." The Learning step is not "I was right all along." The Action step is where the disagree-and-commit move lives, and it has to show two things: the specific thing you did to make your case clearly, and the specific thing you did to commit cleanly after the decision was made.

The stress test for a conflict story: could a weak candidate give this same answer? If your conflict story contains no named mechanism for how you reached alignment, no number or outcome tied to the decision, and no sentence about the relationship afterward, you have described the shape of a conflict story without filling it in.

## Worked Example 1: Research Team, Different Priorities

**Question:** "Describe working with a team that had different priorities."

**Decompose the question.** "Different priorities" is cross-functional collaboration language. The hypothesis behind it: can this candidate identify what actually motivates someone with a different job, and use that to find alignment rather than forcing a compromise that leaves both sides unhappy?

**Identify the signal.** The conflict here is structural, not personal: two teams whose incentive structures point in different directions. The interviewer wants to see whether the candidate understood the other team's incentives, not just their own, and built a solution from that understanding.

**Construct the STAR-L:**

*Situation.* A research team developed a novel retrieval approach showing 20% better recall on benchmarks. They wanted to publish and move to the next research question. Product wanted the system in production. The candidate was responsible for productionizing it.

*Task.* Ship the system in production without burning the relationship with researchers who had no particular reason to care whether it shipped.

*Action.* This is where the candidate earned the outcome. Rather than negotiating from "you need to help us ship this," they started by asking what the researchers actually cared about: credit for the innovation, and not having their approach simplified past recognition. The candidate proposed a collaboration structure: researchers remain authors on publications about the production system; the candidate documents exactly which contributions affected production metrics; weekly meetings let the research team review any changes and verify scientific integrity. When a simplification was needed for latency, the candidate showed benchmarks proving the core innovations were preserved. Researchers, with skin in the game, contributed optimization ideas.

*Result.* The system shipped in eight weeks with 18% recall improvement in production (slightly below the 20% benchmark due to latency constraints). Researchers published a follow-up paper on production learnings. The collaboration structure became a template for future research-to-production handoffs.

*Learning.* Understanding what the other party is optimizing for is the key move in a cross-functional conflict. The technical dispute (how much to simplify) was easy to resolve once the incentive structure was aligned. A collaboration that looks like a tradeoff argument is usually a motivation problem in disguise.

**Stress-test.** The unfakeable specifics: 20% on benchmark, 18% in production, latency as the named constraint explaining the delta, co-authorship credit as the specific mechanism, a follow-up paper, a template that outlasted the project. A candidate who was not there cannot reconstruct those numbers. The Learning step names the generalizable principle, not a restatement of the outcome.

**The conflict angle to foreground.** The disagreement was real and structural. The candidate did not pretend the research team's priorities were wrong; they found the move that made production success serve the researchers' own goals. That is disagree-and-commit at the cross-functional level: you acknowledge the other party's position is legitimate, you find an alignment, you commit to the outcome together.

## Worked Example 2: Overruled Before a Launch

**Question:** "Describe a time you raised a concern and the team decided against you. What did you do?"

**Decompose the question.** This question names the hardest version of disagree-and-commit: you were not part of the decision, the decision went against your explicit position, and you still had to execute it. The hypothesis is whether the candidate can commit cleanly after a loss, or whether they undermine the decision through inaction or continued campaigning.

**Identify the signal.** The conflict is vertical: the candidate versus leadership with a launch date in view. The interviewer is looking for two things that are easy to say and hard to demonstrate: the candidate made their case with real specificity (not vague risk), and they committed without relitigating.

**Construct the STAR-L:**

*Situation.* Before a launch, the candidate flagged that the agent's tool permissions were broader than the feature required: it could write to systems it only needed to read. Leadership weighed that risk against the launch commitment and decided to ship as-is, with permission scoping as a fast-follow.

*Task.* The candidate disagreed with the call. Their job was to ensure the decision was made with full information, then either escalate or commit.

*Action.* First, the candidate made the risk concrete: not "this is risky," but a specific blast radius if the agent were prompt-injected, with a realistic attack path written out. That is the distinction between a vague concern and a case someone can actually evaluate. Then, rather than asking for a delay, the candidate asked for two mitigations that fit inside the launch window: an audit log on the write paths and an anomaly alert on write volume. Both were accepted. The candidate documented their disagreement in the decision record and committed to the launch without relitigating it in hallway conversations.

*Result.* The launch was fine. Three weeks later, the alert fired on a misconfigured integration test, not an attack, but it proved the monitoring worked. Permission scoping shipped a month later, prioritized by that signal.

*Learning.* Being overruled is not the end of the job. Converting a lost argument into cheap guardrails and a written record is usually worth more than winning the argument, and it builds the credibility that makes the next concern land harder. The candidate who says "noted" and commits is the candidate leadership trusts with the next hard call.

**Stress-test.** The specifics that make this unfakeable: the named blast radius (prompt injection, specific write systems), the two named mitigations (audit log on write paths, anomaly alert on write volume), the alert firing three weeks later on a misconfigured integration test. The candidate did not just "raise a concern and commit." They ran a blast-radius analysis and converted a lost argument into instrumentation that proved its value independently.

**The conflict angle to foreground.** This example appears elsewhere in this module from a different angle. Here the signal is conflict and disagree-and-commit: what the candidate did with the loss matters more than what they said during the argument. The specific move is the documented disagreement plus the cheap guardrails plus the clean commit. That combination is what separates a candidate who knows the phrase "disagree-and-commit" from a candidate who actually practices it.

## The Weak-Answer Audit for Conflict Stories

A conflict answer fails the audit if it contains any of these:

- The resolution is described but the specific mechanism that produced it is not named.
- The story ends at the decision with no sentence on the working relationship afterward.
- The Learning step explains why the candidate was correct rather than what changed in how they operate.
- The other party's position is described only as wrong or unreasonable.

Run this audit on your own stories before the room does.

The interviewer is not looking for a candidate who wins disagreements. They are looking for a candidate who makes the team functional when disagreements are in progress, and that is a different, harder thing to prove.

## Core Concepts

- The conflict signal tests whether you make the team better or worse under disagreement, not whether you win arguments.
- Disagree-and-commit requires two visible moves: making your case with specificity, then committing cleanly without relitigating the outcome.
- The mechanism that produced alignment must be named; "we eventually aligned" is not an answer.
- Being overruled is not the end of the job; converting a lost argument into cheap guardrails and a written record is the move that builds credibility for the next concern.

<div class="claude-handoff" data-exercise="exercises/module3/conflict-stories/">

**Try It in Claude Code:** Write one of your own conflict stories, run the full Algorithm on it (decompose the question, name the signal and hypothesis, build the STAR-L toward disagree-and-commit, stress-test for unfakeable specifics), and add it to your behavioral bank with the weak-answer audit results attached.

</div>
