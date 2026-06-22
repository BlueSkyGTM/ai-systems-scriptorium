# Tailoring to the Role

The production RAG chatbot you built in Sans Python is a single artifact. It is also three different stories, depending on who is sitting across the table. Delivering the identical walkthrough to every interviewer, regardless of the role, is not confidence; it is a failure to read the room, and it costs you offers.

This is the anti-memorization thesis applied to the portfolio. The decisions are fixed: you built what you built, the choices are on disk, and nothing about your narrative changes the artifact itself. What bends is which decisions you lead with, how deep you go on each, and the vocabulary you reach for. Reading the role and calibrating the narration to it is the skill the lesson builds.

## Why the Same Artifact Is a Different Story

An interviewer from an applied-AI product team and an interviewer from an ML-platform team are running different hypotheses when they ask you to walk them through a project.

The product-team interviewer wants to know whether you understood the user-facing failure modes. Can this system stay reliable for the people who depend on it? Do you know what "reliable" means for a citation-enforced chatbot in a regulated vertical? They are listening for the decisions that protected the user: the refusal when nothing retrieval-worthy surfaced, the guardrails that held a floor the operator could not lower, the eval that ran in CI so the chatbot could not regress silently.

The platform-team interviewer wants to know whether you understood the operational structure. Can this system be maintained, extended, and integrated with infrastructure that did not exist when you built it? They are listening for the seams: the `VectorIndex` protocol that made Azure AI Search a one-constructor swap, the deterministic gates that ran without a live model, the drift monitor that turned a diffuse quality signal into a concrete operational flag.

The research-adjacent interviewer wants to know whether you built rigorous measurement into the system itself. Do you know the difference between a test that passes and an eval that means something? They are listening for the metrics: precision and faithfulness scored offline, a gate that defaulted to FAIL rather than PASS, a drift monitor with a named window and a named SLO.

None of these interviewers are wrong about what matters. They are each listening for a different dimension of the same artifact. The candidate who knows that, and adjusts, is demonstrating the judgment a senior engineer brings: you can translate the work for the audience in front of you.

## The Worked Example: Three Rooms, One Chatbot

The production RAG chatbot has seven load-bearing decisions. Every walkthrough covers all of them, in the sense that the interviewer will ask follow-ups and you must be able to speak to any of them. What changes is your opening, your depth allocation, and the frame you put on each decision before you explain it.

### Applied-AI and Product Engineer: Lead With Reliability

The opening orients around what the user experiences: "This system retrieves from a corpus, grounds every answer in retrieved chunks with explicit citations, and refuses rather than fabricates when nothing retrieval-worthy surfaces. I want to walk you through how I kept it reliable for the people depending on it."

The first decision you foreground is the relevance floor. The retriever holds a minimum similarity score; if the top results all fall below it, the system returns a refusal instead of returning low-confidence chunks and letting the model paper over the gap. You explain the tradeoff plainly: some valid questions receive "I don't have a source for that." The failure mode guarded is more important than the cost: hallucinated citations in a regulated vertical are not a quality miss, they are a liability. The decision is to accept the false-negative cost to eliminate the false-positive risk.

From there you move to the citation contract: every answer carries the `doc_id` and section of the chunk it came from, not as a decoration but as a verifiable claim the user can check. The guardrail pairs with this; it splits rules into a hardcoded floor (prompt injection, PII exfiltration) and operator-tunable scope, and the floor is bounded so an operator under pressure cannot configure their way below it. You spend real time on this split: the product interviewer understands that configurable guardrails are only as strong as the people configuring them.

The drift monitor and eval gate are where you answer "does it stay reliable over time?" The drift monitor samples quality over a rolling window and flags an SLO breach when the mean drops below tolerance. You say explicitly that infrastructure metrics would not have caught this failure mode; corpus shifts and model updates degrade answer quality while uptime stays green. The eval gate, scoring retrieval precision and answer faithfulness, runs in CI so a degraded build cannot ship. Those two together are your answer to "how did you know it was staying good in production?"

Notice what you spend less time on: the `VectorIndex` protocol seam, the deterministic mock at the generation seam, the path jailing in the tool registry. Those are real decisions. A product interviewer will follow up on them if they probe the architecture. But they are not what the role is evaluating as the lead.

### ML-Platform and Infra Engineer: Lead With Seams and Operability

The opening reframes: "This is a citation-enforced RAG system built around two clean seams that separate the retrieval backend from the application and the generation model from the pipeline. I want to walk you through how it's designed to be maintained and extended."

The first decision you foreground is the `VectorIndex` protocol: a two-method interface, `add` and `search`, that both the in-memory default and Azure AI Search satisfy. You walk through why the seam is there: a pipeline without a seam couples every downstream component to one backend, so migrating storage touches every layer. With the seam, migrating is one constructor call. The platform interviewer has lived this problem; they know the migration cost, and they are listening for whether you do.

From there you move to the deterministic gates. The eval gate scores precision and faithfulness offline, without a live model, so it runs in CI and means the same thing every time. You say "deterministic" deliberately: the platform interviewer's concern is operational consistency. A gate that behaves differently in CI than in production is not a gate; it is a suggestion. The `Chunk` contract feeds this: ingest maps every format onto one shape, so a document parser change does not propagate downstream and cannot cause the gate to behave differently on a different run.

The drift monitor translates differently in this room. You frame it not as a quality story but as an operational signal: the monitor turns "something got worse" into a named metric with a defined threshold and a binary outcome. That is what makes it operable; a diffuse quality perception cannot trigger an alert or a runbook.

The guardrail's two-tier split matters here in a specific way: the hardcoded floor holds regardless of operator configuration, which means the security contract is stable and testable. You can write a test that verifies the floor holds. That is a different property than "the operator did not configure anything bad."

What you spend less time on: the refusal behavior for low-relevance queries, the user-facing citation contract, the specific metrics the eval gate measures. Those decisions are real and answerable on follow-up. But the platform interviewer's signal is the structural properties of the system, not the user-experience implications of the refusal.

### Research-Adjacent and Applied Science: Lead With Eval Rigor

The opening centers measurement: "This system has a deterministic eval gate that scores retrieval precision and answer faithfulness offline, a drift monitor that tracks quality over a rolling window against a defined SLO, and a refusal mechanism built on a principled threshold rather than a confidence heuristic. I want to walk you through the measurement layer."

The first decision you foreground is the eval gate. It scores two things: retrieval precision (did the retrieved chunks actually match the query?) and answer faithfulness (did the generated answer stay within what the retrieved chunks support?). It does not use an LLM judge, because an LLM judge is not deterministic; the same test can pass and fail across runs without any change to the system. The gate defaults to FAIL; a passing score must be earned, not assumed. You explain the tradeoff: simple metrics miss sophisticated hallucinations. But the tradeoff you accepted is the one that gives you a gate with the property you need for CI: it runs the same way every time.

The relevance floor is where you connect refusal to measurement. The threshold is a named number, not a feeling. Setting it too low and you are generating answers from low-relevance context; setting it too high and you are refusing valid queries. The refusal rate is measurable, the threshold is tunable, and the failure mode (fabrication from weak context) is not recoverable after the fact in a regulated vertical.

The drift monitor closes the loop: you specify the window size, the quality metric, and the breach threshold in advance. "Something degraded" is not a useful signal; "the rolling precision mean dropped below 0.75 in the last 100 queries" is. The research-adjacent interviewer hears this and knows you understand the difference between an observation and a measurement.

The `Chunk` contract supports reproducibility: because every ingested document maps to the same shape before it enters the index, the eval is running against a stable unit. A change to the parser does not change the eval target. That is not a performance property; it is a measurement property.

What you spend less time on: the seam architecture, the CI operability of the gates, the user-facing citation UI. Those are real properties of the system. The applied-science interviewer will follow up if they probe the implementation. But what they are buying in this room is evidence that you built rigorous measurement in, not as a retrofit, but as a load-bearing component.

## Reading the Role

The three narrations above were not invented after the interview. They were prepared before it. The skill is reading the signal early enough to calibrate the lead.

Three inputs give you most of what you need before the interview starts.

**The job description.** Look for the words that recur in the responsibilities and requirements. A description heavy on "reliability," "user experience," and "production quality" is signaling the applied-AI frame. One heavy on "infrastructure," "platform," "scalability," and "integrations" is signaling the platform frame. One heavy on "evaluation," "measurement," "benchmarks," and "rigor" is signaling the research-adjacent frame. The JD is a public statement of what the team values; read it that way.

**The interviewer's team.** If you know the interviewer's current project or team, that is a stronger signal than the JD. A platform engineer working on vector search infrastructure will listen for seams. A product engineer working on a user-facing AI feature will listen for reliability and user trust. A researcher working on eval methodology will listen for measurement rigor. LinkedIn and the company's engineering blog often tell you enough before the call.

**The questions they ask first.** If the first two questions are about the user experience or failure modes in production, that is a live signal: shift your depth allocation toward the product frame. If the first questions are about how you would extend or replace a component, shift toward the platform frame. If the first questions are about how you measured what you built, shift toward the research-adjacent frame. This is not a rigid decision; it is a continuous update. The interviewer's questions are data about what they are evaluating, and you are allowed to use that data.

Once you have read the signal, the choice is which decision to lead with: the refusal and citation contract, the protocol seam, or the eval gate. The rest of the walkthrough follows from the lead. You foreground what the role values, you depth-allocate there, and you hold the other decisions ready for follow-ups. You did not change the artifact; you changed where you entered it.

This is what makes the portfolio narration a live skill rather than a speech. A memorized monologue has one entry point. A walkthrough built from the decision layer has seven, and you choose the right one for the room.

## Core Concepts

- The same portfolio artifact narrates differently for different roles because different roles are evaluating different dimensions of the same decisions; the artifact does not change, the emphasis and the lead do.
- The decision set is fixed by what you built; what bends is which decision you open with, how deep you go on each, and the vocabulary frame you put around it.
- Three inputs let you read the role before and during the interview: the job description's recurring vocabulary, the interviewer's team and current work, and the first questions they ask; treat all three as live data.
- A walkthrough built from the decision layer has multiple entry points; a memorized monologue has one, which is why the monologue fails at least one room.

<div class="claude-handoff" data-exercise="exercises/module6/tailoring-to-the-role/">

**Try It in Claude Code:** take the artifact in your portfolio-narrative document and write two role-tailored versions of its walkthrough, leading with different decisions for two different role types, and note what changed and what did not.

</div>
