# Conflict Stories

The question "tell me about a disagreement with a colleague" sounds like an invitation to vent. It is not. The interviewer is running a specific test: can you operate constructively after you lose an argument?

That is the conflict category in one sentence. Every question in it, from "describe working with a team that had different priorities" to "describe a time you raised a concern and the team decided against you," is probing the same thing: the disagree-and-commit pattern, de-escalation, and proportional escalation. Whether you won is beside the point. What you did after the decision is the whole signal.

This lesson runs the Algorithm twice, on two real conflict questions, and shows the construction rather than the answer. Read for the moves, not the words. The words belong to your story.

## What the Interviewer Reads For

The hiring hypothesis in the conflict category is: can this candidate navigate real organizational disagreements, with a PM over AI capability claims, with a peer over a technical approach, with leadership after being overruled, and come out with the relationship and the work intact?

Three sub-signals drive the scoring:

1. **The disagree-and-commit pattern.** Did you make the concern legible before committing? Did you then actually commit, or did you relitigate it afterward in hallway conversations?
2. **Concrete mechanisms.** "We aligned" does not score. The positive models in the source material all name a specific move: a collaboration structure with co-authorship credit, two mitigations asked for inside the launch window, a written disagreement in the decision record. Vague resolution is the same as no resolution.
3. **Relationship outcome.** A conflict story that ends at the decision without naming what happened to the working relationship is a grievance story. Interviewers ask: "What was the relationship like after?" If you have no answer, you have told the wrong story.

## Worked Example A: Different Priorities

**Question:** "Describe working with a team that had different priorities."

### Step 1: Decompose the Question

Before reaching for a story, name the hypothesis and the signal.

```
Question type:    Collaboration and Conflict (asdg 05, Example 4)
Primary signal:   Communication / influence
Secondary signal: Judgment under uncertainty (incentive alignment vs. override)
What they're really asking:
  Did you impose your priorities, or find the lever that made their priorities
  and yours point the same direction?
Unfakeable specificity needed:
  A named mechanism for the alignment; a result with numbers;
  something the researchers got out of it
```

### Step 2: Map a Story to the Signal

The Algorithm's second move is choosing the story with the right fit, not the most impressive one you remember. Here the question is not "what did you build?" but "how did you handle someone whose success criteria differed from yours?" That narrows the pool: you want a story where the other party had a coherent, legitimate reason for their position, and where the resolution was mutual rather than one-sided.

For this example, the ore surfaces a real shape: a research team that had developed a novel retrieval approach showing 20% better recall on benchmarks. They wanted to publish and move on. Product wanted it shipped. The engineer responsible for productionizing is the candidate.

That tension is genuine. Researchers optimize for credit and scientific integrity; engineers optimize for latency and operational stability. Neither is wrong. The question is what you do about it.

### Step 3: Construct the STAR-L Answer Toward the Signal

```
S:  Research team developed a retrieval approach with 20% better recall on benchmarks.
    They wanted to publish and move on; product wanted it shipped.
    I was the engineer responsible for productionizing it.

T:  Get the system into production while keeping a good relationship with researchers
    who had different incentives.

A:  Started by understanding what they actually cared about: credit for the
    innovation and not having their method "dumbed down" in production.
    Proposed a collaboration structure:
      - They stay as authors on publications about the production system.
      - I document which contributions directly impacted production metrics.
      - Weekly meetings to review changes and ensure scientific integrity.
    When simplification was needed for latency, I ran benchmarks proving
    their key innovations were preserved in the simplified version.
    That evidence converted a potential veto into optimization ideas from
    the researchers themselves.

R:  Shipped in 8 weeks with 18% recall improvement (slightly below the 20%
    benchmark because of latency constraints; I was transparent about why).
    Researchers published a follow-up paper on production learnings.
    The team established a template for research-to-production handoffs
    that we now use across projects.

L:  Understanding what motivates others is the actual lever. Once production
    success supported researchers' goals (impact and credit), the friction
    inverted into partnership. The template is the artifact that proved it
    was a real collaboration, not a compromise.
```

### Step 4: Stress-Test Before Finishing

The Algorithm's fourth move is the weak-candidate test. Ask: could any candidate give this answer?

No. The specific mechanism (co-authorship credit, weekly scientific-integrity review) is not generic. The delta between 20% on benchmarks and 18% in production, with an explicit reason for the gap, is not something a candidate who only read about the project can fake. The follow-up paper and the template are outcomes that either exist or do not.

The conflict signal is clear: you did not win by overpowering the researchers. You aligned their incentives with yours and let them contribute rather than resist. That is the pattern the interviewer is looking for.

**One thing that makes it unfakeable:** name the delta and the reason for it. "18% recall in production (slightly less than the 20% benchmark due to latency constraints, which we documented and explained to the research team)" is a sentence a candidate who was there can say. A candidate who was not cannot.

## Worked Example B: Raised a Concern, Got Overruled

**Question:** "Describe a time you raised a concern and the team decided against you. What did you do?"

### Step 1: Decompose the Question

```
Question type:    Collaboration and Conflict (asdg 05, Example 6)
Primary signal:   Judgment (proportional escalation, disagree-and-commit)
Secondary signal: Communication / influence (converting a lost argument)
What they're really asking:
  After you lost, did you sulk, relitigate, or find the constructive move?
  The "what did you do" is the whole test.
Unfakeable specificity needed:
  The specific risk you named; the specific mitigations you asked for;
  evidence that the concern was real (what happened later)
```

### Step 2: Map a Story to the Signal

This question has a sharp structure: it has two parts, and candidates almost always answer only the first. They describe the concern, the disagreement, and the decision. Then they stop. The interviewer is waiting for the second part, which is what you did after.

The category's positive model shows the shape: an engineer flags, before a launch, that an agent's tool permissions are broader than the feature needs. Leadership weighs the delay against launch commitments and decides to ship as-is with a fast-follow ticket. The engineer disagrees with the call. What they do next is the entire answer.

### Step 3: Construct the STAR-L Answer Toward the Signal

```
S:  Before a launch, I flagged that the agent's tool permissions were broader
    than the feature needed: it could write to systems it only needed to read.
    Leadership weighed the two-week delay against launch commitments and
    decided to ship as-is, with a fast-follow ticket.

T:  I disagreed with the call. My job was to ensure the decision was made
    with full information, then either escalate or commit. I did not have
    grounds to escalate past the decision; the risk was real but not
    launch-blocking at that moment.

A:  I wrote the risk down concretely: specific blast radius if the agent
    were prompt-injected, with a realistic attack path, not "this is risky."
    Then I asked for two mitigations that fit inside the launch window:
      - An audit log on the write paths.
      - An anomaly alert on write volume.
    Both were accepted. I documented my disagreement in the decision record
    and committed to the launch without relitigating it in hallway
    conversations after the call was made.

R:  The launch was clean. Three weeks later, the alert fired on a
    misconfigured integration test, not an attack, but it proved the
    monitoring worked. The permission scoping shipped a month later,
    prioritized in part because of that signal.

L:  Being overruled is not the end of the job. Converting a lost argument
    into cheap guardrails and a written record is usually worth more than
    winning the argument. It also builds the credibility that makes the next
    concern land harder.
```

### Step 4: Stress-Test Before Finishing

Again, the weak-candidate test. The generic version of this answer is "I raised a concern, the team decided against me, and I accepted the decision." That sentence scores nothing. It describes compliance, not judgment.

What separates this answer: the specific risk articulation (blast radius, realistic attack path), the two named mitigations, the documented disagreement in the decision record, and the follow-up where the alert actually fired. A candidate who was not there cannot reconstruct that sequence. The Learning step earns its place because it names a generalizable principle ("converting a lost argument into cheap guardrails") that the candidate can apply in the next role, not just the story where it happened.

**One thing that makes it unfakeable:** the alert firing on a misconfigured integration test three weeks later is the kind of mundane, specific detail that only someone who lived through it would include. It is also the detail that proves the concern was real, not retrospective credit-claiming.

## The Conflict Category's Failure Modes

After the two examples, name what kills these answers. Four patterns are consistent across the source material:

**Telling a grievance story.** The candidate spends most of the answer explaining why they were right and the other party was wrong. The interviewer is not scoring correctness; they are scoring what you did after. An answer that reaches the decision and then stops has answered zero percent of the second question.

**Vague alignment.** "We eventually aligned" or "we found common ground" without naming the specific mechanism is indistinguishable from no resolution. The score-able version names what you actually did: proposed the co-authorship structure, asked for the two specific mitigations, documented the disagreement in the decision record.

**Only technical content, no human factor.** Conflict questions probe the human dimension. A candidate who answers the disagreement-over-technical-approach question with a comparison of two architectural options and no mention of how the relationship navigated it has missed the category entirely. The ore flags this directly: "only technical answers" is a named red flag.

**Relitigating after committing.** If the story ends with "I committed to the launch," and the interviewer later asks how the relationship was after, and the candidate mentions that they kept bringing it up in team meetings: that retroactive detail collapses the answer. The conflict category tests whether you can close an argument. An answer that commits but then campaigns is an answer that does not commit.

## Weak-Answer Audit

Here is a weak version of the second example. Read it, then the analysis.

> "I raised a concern about security before the launch. My manager heard me out but decided to ship anyway because of timeline pressure. I didn't agree but I respected the decision and we launched. It ended up being fine."

**Why it fails:**

The answer describes compliance, not judgment. It names the concern in a single word ("security") without quantifying the risk. It reports the outcome ("fine") without naming anything the candidate did to make it more likely to be fine. There is no mechanism: no mitigations asked for, no written record, no specific action after the call was made. The Learning step is absent.

The weak-candidate test surfaces the problem immediately. Any candidate who has ever disagreed with a manager and said nothing could give this answer. It requires no experience. The signal the interviewer wanted, the specific move you made after the decision, is not here.

**The fix:**

The answer needs the mechanism and the Learning step. Specifically: what you asked for inside the launch window, what you put in writing, and what the experience taught you about how to operate after being overruled. The concrete mitigations (audit log, anomaly alert) are not polish; they are the entire second half of the answer the question asked for.

A conflict story is not a story about a decision. It is a story about what you did when the decision was not yours to make.

## Core Concepts

- The conflict category tests what you did after the argument, not whether you won it: every question in this group probes the disagree-and-commit pattern, not the strength of your position.
- Concrete mechanisms score; vague resolution does not: name the specific move (the co-authorship structure, the two mitigations, the written decision record), not the feeling of alignment.
- A conflict story without a relationship outcome is a grievance story: if you cannot say what happened to the working relationship after, you have told the wrong story.
- Converting a lost argument into cheap guardrails and a written record often builds more credibility than winning the argument would have.

<div class="claude-handoff" data-exercise="exercises/module3/conflict-stories/">

**Try It in Claude Code:** pick one conflict question from the category list above, run the four-step Algorithm on a real story from your own experience, and write out the full STAR-L skeleton. Then run the weak-answer audit: write the weakest version of the same answer, name what each failure mode it trips, and write the one sentence that would fix the most damaging omission.

</div>
