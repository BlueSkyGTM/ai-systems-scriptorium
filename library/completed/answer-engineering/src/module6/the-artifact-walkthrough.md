# The Artifact Walkthrough

The walkthrough is not a code reading. That gap, between narrating what each function does and narrating the reasoning behind the decisions, is where offers are won or lost.

Every engineer who interviews on a portfolio tends toward the same mistake: they open the code and begin describing it. The interviewer can read code. What they cannot learn from the code alone is whether you made the choices on purpose, whether you understood the failure modes you were guarding against, and whether you can explain all of that to someone who was not there. The walkthrough is that explanation, and its shape is not the shape of the code.

## The Signal the Interviewer Is Reading

When an interviewer asks you to walk them through a project, they are running a two-part test. First: can you make them understand a system they have never seen, quickly? Second: can you show them the judgment that went into it?

The failure mode looks like preparation from the outside. The candidate names the components in order. The terminology is fluent. The architecture sounds plausible. Then the interviewer asks: "Why did you make the agent's kill switch read-only?" If the answer is "that's how the lesson did it," or a blank pause, the walkthrough is over. The candidate memorized the artifact. They did not own it.

The interviewer is listening for three things in particular: the decisions you made (and could have made differently), the alternatives you rejected (and why), and the failure modes you designed against (and how). A walkthrough that lists components scores low. A walkthrough that defends choices scores high. It is the same discipline as justifying every box in a systems-design round, except now the system is real, the constraints were real, and you are the one who shipped it.

## The Sixty-Second Overview

A walkthrough opens with an overview, and the overview has one job: orient the listener fast. You are not summarizing every feature. You are giving the interviewer the frame they need to hear the decisions.

The overview has three beats:

1. What the artifact is (one sentence on purpose).
2. What it does (one sentence on mechanism).
3. The one impressive thing: the single decision that makes this artifact interesting, stated plainly and led with.

Lead with the differentiator. The first thing out of your mouth should be the decision that most clearly shows judgment, not the component list. If you bury the impressive thing at the end of a component tour, the interviewer may have already formed their impression.

Here is the sixty-second overview for the terminal coding agent you built in Sans Python:

> "This is a terminal coding agent: it reads a failing file, writes a fix, runs the real test suite in a subprocess, and loops until a deterministic verification gate accepts the result. The most important design decision is that gate, which defaults to REJECT and runs the actual tests, not the model's self-assessment. The agent also holds a read-only kill switch the operator owns, and a budget with two hard caps, dollar cost and iteration count, checked before every model call to guard against runaway billing."

That overview runs about forty-five seconds spoken. It orients the listener on what the system does, then immediately foregrounds the three decisions that give the artifact its character: the verification gate, the kill switch, and the budget. The interviewer now has the frame to hear the decision tour.

Notice what the overview does not include: the tool registry, the mock model seam, the path-jailing logic, the subprocess wall-clock timeout. Those are real parts of the system. They are not what makes the system interesting to an interviewer. You lead with the judgment; you skip the inventory.

## The Decision Tour

After the overview, you go deep on three or four choices that mattered. Not every choice. Not the obvious ones. The ones where you had a real alternative, made a call, accepted a tradeoff, and guarded against a specific failure mode.

Each decision in the tour follows the same four beats:

1. State the decision.
2. Name the alternative you rejected.
3. Name the tradeoff you accepted.
4. Name the failure mode you guarded against.

You do not read the code. You narrate the reasoning.

### The Verification Gate

The terminal coding agent defines "done" as a fact returned by running the real test suite, not a claim from the model. The alternative: trust the model's self-assessment. The model loops, writes a fix, and reports whether it believes the fix is correct.

The tradeoff you accepted: the agent runs the full suite on every candidate fix. That costs time and money. But the failure mode you guarded is the one that makes coding agents unreliable in practice: the agent declares victory on a broken fix. A model that checks its own output is an optimist, not a verifier. The gate is the antidote, and it defaults to REJECT, not to pass. You have to earn the pass.

That default matters. A gate that defaults to pass with a threshold is a gate that can be gamed by an agent that barely tries. A gate that defaults to REJECT can only be cleared by running the tests and having them pass. The distinction is architectural, not a detail.

### The Read-Only Kill Switch

The kill switch is a file the operator owns. The agent can read it (`tripped()`) but cannot write it. The alternative: a flag in the agent's own reachable state, something the agent sets when it decides to stop.

The tradeoff: the kill switch requires an external file check before every action. That is one more thing that can fail. But the failure mode guarded is more serious: if the kill switch lives in state the agent can write, the agent can disable its own kill switch. You have a kill switch in name only. The read-only constraint is what gives the operator actual control, not apparent control.

This is the kind of decision an interviewer cannot infer from the code. Reading the source, they see a file check. They do not see the reasoning: that write access was considered and removed because write access defeats the purpose.

### The Budget With Two Caps

The agent checks a budget before every model call. The budget has two ceilings: total dollar cost and total iteration count. Both are checked before paying for another action, not after. The alternative: check the budget after the call, or ask the model to monitor its own spend.

The tradeoff: the pre-call check means the agent stops one action sooner than a post-call check would. You occasionally leave a loop on the table. The failure mode guarded is Denial of Wallet: a runaway loop billing indefinitely because no hard ceiling was enforced. A budget you ask a model to enforce is a budget the model can reason its way past. Two deterministic ceilings, checked before the cost is incurred, cannot be argued with.

### What You Skip

Notice what the decision tour did not cover: the tool registry's schema validation and path jailing, the subprocess sandbox timeout, the mock model seam. Those are real decisions with real reasoning. They are not the decisions that show interviewer-relevant judgment in a portfolio walkthrough.

You skip them not because they are unimportant, but because the walkthrough is not exhaustive. You are demonstrating judgment, and part of that demonstration is choosing which decisions to surface. An interviewer who asks about the tool registry gets a full answer; but you do not volunteer it in the tour when you have only ten minutes and three stronger decisions to make the case.

You also do not read the code aloud. Saying "line 47 calls `budget.check()` and then..." is the failure mode the overview warned against. The decision is not the line; the decision is the reasoning that put that line there.

## The Transfer: Any Artifact, Same Shape

The walkthrough shape you just saw works for any portfolio artifact. The structure is fixed; the content is the artifact.

Open with the sixty-second overview: purpose in one sentence, mechanism in one sentence, the differentiator first. The differentiator is whichever decision most clearly shows that you understood the hard part of the problem, not the flashy part.

Then run three or four decisions through the four-beat structure: what you chose, what you rejected, the tradeoff you accepted, the failure mode you guarded. Choose the decisions that are genuinely defensible: ones where you had a real alternative, not ones where there was only one obvious answer.

Close the decision tour before the interviewer's attention runs out. Ten minutes is about right for a portfolio walkthrough in an interview setting. If you are running longer, you have too many decisions in the tour; cut to the three that are strongest.

One note on adaptation: the decisions do not change between interviewers, but the order and emphasis do. An infrastructure-focused interviewer will want the kill switch and the budget early; they are the operability story. A product-focused interviewer may want the verification gate and its implications for reliability. You read the role before the walkthrough, and you lead with the decision the role values. That adaptation is not dishonesty; it is signal discipline. The walkthrough is for them.

## Core Concepts

- A walkthrough is the reasoning behind an artifact told to someone who was not there, not a narration of what each function does; that distinction is where interviews turn.
- The sixty-second overview orients fast and leads with the single most differentiating decision, not a component list.
- Each decision in the tour follows four beats: what you chose, what you rejected, the tradeoff accepted, the failure mode guarded.
- Choosing which decisions to surface is itself a demonstration of judgment; the candidate who volunteers every decision buries the three that matter.

<div class="claude-handoff" data-exercise="exercises/module6/the-artifact-walkthrough/">

**Try It in Claude Code:** pick one portfolio artifact (a Sans Python one you built, or your own) and write its sixty-second overview and the one decision you would lead with into your portfolio-narrative document.

</div>
