# Construct the Answer

You decomposed correctly and named the signal. You still lose the offer if the answer only points at the signal instead of delivering the evidence it demands.

## The Construction Problem

Most candidates conflate "aimed at the right signal" with "good enough." They are not the same. The answer gestures at the right territory and stops short of proof.

A strong answer has three properties: specific enough that a weak candidate could not give it, structured so the interviewer can follow the reasoning, complete enough to close the loop on the hypothesis. Specificity is the most critical and the most commonly abandoned under pressure. When you are nervous you reach for the general case: "I used eval-driven development." That is a claim. The evidence version: "I built three binary judges, one for groundedness, one for answer relevance, one for format compliance, calibrated each against fifty labeled examples from our support queue, and set the groundedness judge as a hard gate in CI." The first sentence is something anyone can say. The second is not.

Structure makes the reasoning visible so the interviewer can score it. Completeness means you close the loop: a story that ends with "we made the decision" without naming the outcome is not complete.

## Build Backward From the Hypothesis

Start from the hypothesis, not from the beginning of the story.

Ask: what does the hypothesis require as evidence? If the hypothesis is "this candidate makes defensible calls under uncertainty," the required outputs are a real decision (not "I contributed to the discussion"), explicit uncertainty (what you did not know and why), and a reasoning process you can trace. Those three are your required outputs. Everything else is optional context.

Then find the shortest path to that evidence. Shortest is not always chronological. You can start with the decision, unpack the uncertainty, then describe the reasoning. Or start with the constraint, name the options, then the call. Cut everything that does not move toward the evidence. The construction ratio: roughly 20% context, 60% evidence (the decision, reasoning, and action), 20% result and reflection.

## The Named Construction Scaffolds

Five frameworks exist because five question types exist. Pick the scaffold that matches the type, build inside it.

**STAR-L** for behavioral questions: Situation, Task, Action, Result, Learning. Two moves separate strong STAR-L answers from weak ones: use "I" for every action (not "we" -- "we" hides ownership), and quantify the result (behavioral answers without numbers get scored as anecdotal). The Learning step is load-bearing for AI roles: AI projects carry unique uncertainty, and the Learning step is where you demonstrate you internalized the AI-specific lesson, not a generic one.

Take a real case. The question: "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong." A weak answer names the mistake and moves on. The strong STAR-L runs the full arc: pushed to replace the retrieval pipeline with a pure long-context approach, argued in two design reviews, committed the team to a quarter of migration work. Eval results showed quality matched but cost ran 4x projection: cache hit rates collapsed under update frequency, p95 latency doubled. After two weeks of marginal gains, wrote a one-page memo stating plainly that the recommendation was wrong on the economics, then proposed a hybrid approach to the same audience. The hybrid shipped; 60% of migration work was salvaged; the postmortem produced a team rule that any architecture pitch must include a cost model under realistic update patterns. The specificity that makes this unfakeable: "cost ran 4x projection," "two weeks of marginal gains," "one-page memo." No one invents those details. The answer lands because they are real.

**SPIDER** for systems-design questions: Scope and clarify, Prioritize requirements, Initial architecture, Deep dive critical paths, Evaluation and observability, Reliability and scale. The biggest gap between senior and staff answers shows up in the E and R phases: end every deep dive with a sentence on observability and a sentence on failure modes. This is not stylistic. The Azure Well-Architected Framework for AI workloads states that the nondeterministic nature of AI workloads makes vigilant quality monitoring essential, because measurements can change unexpectedly at any time after deployment (learn.microsoft.com/azure/well-architected/ai/operations). Azure AI Foundry's observability model names evaluation, monitoring, and tracing as the three core capabilities spanning the full lifecycle, from pre-production evaluation through post-production quality and latency tracking (learn.microsoft.com/azure/foundry/concepts/observability). A SPIDER answer that reaches the E and R phases and names these in production terms demonstrates operational experience. One that stops at the architecture diagram does not.

**ETA** for concept-explanation questions: Explain simply, Technical details, Applications and tradeoffs. Go from the one-sentence definition to appropriate depth, then connect to practical usage. ETA is for explaining a component; SPIDER is for designing a system.

**Tradeoff analysis** for comparison and justification questions: "RAG vs fine-tuning," "when would you skip reranking?" The key construction move: "it depends" is fine only when followed immediately by "it depends on X, Y, Z, and here is how each changes the answer." Without the second half it reads as hedging. Name the options, define the evaluation criteria weighted for this decision, analyze each against the criteria, make a recommendation, and name the risk. The recommendation is non-negotiable: identifying tradeoffs without committing demonstrates indecision, not nuance.

**Debugging framework** for production-incident questions: gather information first (when did this start, what changed, all requests or a subset), form three to five hypotheses ranked by likelihood, describe the diagnostic approach, propose fixes with a verification plan. The construction move is leading with the gather step. Candidates who open with hypotheses before naming what information they have are showing the same reasoning gap they would in production.

## The Stress Test

Before you stop, run one check: could a weak candidate give this same answer?

If yes, add one specific thing. A number, a decision with real stakes, a failure mode you caught.

This check is internal. You are not asking the interviewer; you are asking yourself, in the final seconds before you stop talking, whether you delivered the evidence or only gestured at it. Consider another case. When flagging that an agent's tool permissions were broader than needed, the weak version says "I raised a security concern and was overruled." The strong version names the specific blast radius if the agent were prompt-injected, the two mitigations that fit inside the launch window (an audit log on the write paths and an anomaly alert on write volume), and the decision record entry before committing. Any candidate can say they raised a concern. Only one candidate ran the blast-radius analysis and converted a lost argument into cheap guardrails.

Decomposing the question is table stakes. The construction step is where you deliver the evidence or describe the shape of where it would be.

## Core Concepts

- Construction starts from the hypothesis: identify what evidence the hypothesis requires, then choose the example and order that reaches that evidence fastest.
- Specificity is the critical property: an answer that points at the right signal but supplies no detail a weak candidate could not also supply is still a weak answer.
- The five named construction scaffolds match question type: STAR-L for behavioral, SPIDER for systems design, ETA for concept explanation, tradeoff analysis for comparison questions, the debugging framework for production-incident questions.
- The stress test runs before you stop: ask whether a weak candidate could give the same answer; if yes, add one specific thing.

<div class="claude-handoff" data-exercise="exercises/module1/construct-the-answer/">

**Try It in Claude Code:** run the full four-step Algorithm on five questions (one per signal category plus one systems-design prompt), write out the complete constructed answer for each, and self-score every answer on specificity, structure, and completeness using the prep-dossier rubric.

</div>
