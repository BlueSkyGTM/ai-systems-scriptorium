# Reading the Design Prompt

The systems-design round opens with a blank whiteboard and a question broad enough to fill a sprint. What separates the candidates who score well from the candidates who fill the whiteboard is not how much they draw: it is what they do in the first ten minutes, before any box touches the board.

Most candidates design the moment they hear the prompt. That impulse is the failure mode. What the interviewer collects in the first ten minutes is whether you scope an ambiguous problem into a bounded one, or whether you build a confident answer to a question you invented yourself.

## The Signal: Scope Before You Draw

The SPIDER framework the field uses for design rounds reserves its first two phases, Scope and Prioritize, for the time before any architecture goes on the board. Together they run about eight minutes. The candidate who respects that allocation demonstrates something the candidate who skips it cannot: the habit of treating an open-ended prompt as an information-gathering problem before it becomes a design problem.

The interviewer is running a specific hypothesis in those first minutes. They want to know whether you ask the questions that bound the design, or whether you reach for a reference architecture and retrofit the requirements later. The distinction matters because a system designed without real requirements is a different system from one designed with them. Constraints change components. Scale changes cost. The latency bar changes the retrieval stack. The permission model can restructure the entire query path. A candidate who draws first and asks later often spends the middle of the round quietly redesigning, which the interviewer can see.

**Three failure modes to avoid:**

The first is jumping straight to architecture. You hear "design an enterprise RAG system" and you start drawing the ingestion pipeline. The interviewer has not yet told you whether this is internal or customer-facing, whether the document corpus has 10,000 or 10 million entries, or what the latency bar is. Each of those answers changes your design.

The second is solving a different problem. You get excited about a multi-agent approach on a prompt that needed a simple Q&A system. You spend twenty minutes on agent orchestration and never address the retrieval or permission requirements the prompt implied. At the end, the interviewer redirects you: you spent the round on the wrong system.

The third is failing to manage the clock. The design round is forty-five minutes. Five minutes on scoping is not a tax on your design time: it is the investment that makes the remaining time coherent. A candidate who monologues through architecture for twenty minutes with no scoping invitations leaves the interviewer with no steering point and runs out of time before reaching evaluation and reliability.

## Worked Example 1: The Enterprise Knowledge Assistant

**The prompt:** "Design a RAG-based knowledge assistant for a large enterprise."

That sentence is a design-round opening, not a specification. Run the Algorithm: decompose first. What is actually being asked? The prompt names the approach (RAG) and the context (large enterprise), but tells you nothing about users, corpus size, access model, language requirements, or the latency bar. Everything that would let you choose components is missing.

**What a strong candidate asks, and why each question matters:**

*How many documents, from what sources?* The answer shapes the indexing strategy and the connector architecture. Ten thousand documents is a single-night batch job. Ten million documents from SharePoint, Confluence, Google Drive, and internal wikis is a delta-sync architecture with per-source connectors, adaptive chunking by document type, and a vector database that can handle metadata filtering at that scale.

*Who are the users, and how do they access the system?* Internal employees and external customers are different design surfaces. An internal system serving 50,000 employees has role-based access control tied to existing Active Directory groups. A customer-facing system has a different auth model entirely.

*What are the language requirements?* A global enterprise may need multilingual retrieval. That changes the embedding model choice, which changes the chunking strategy for non-English text.

*What is the latency bar?* A soft "feel responsive" target and a hard "p95 under 3 seconds" target require different architectures. The 3-second bar is a budget. You can spend 50 milliseconds on permission resolution (cached), 100 milliseconds on embedding the query, 100 milliseconds on vector search, 150 milliseconds on reranking, and 1,500 milliseconds on generation, with buffer remaining. A candidate who does not ask this question cannot do that math, and cannot explain why they chose a reranker or why they cached the permission lookup.

*Must the system respect document permissions?* This is the question that changes the most. If yes, the answer is not "filter after retrieval." Filtering post-retrieval means sensitive documents are pulled into memory before anyone checks access, which is a data-leak risk. Permissions must be resolved at retrieval time: every chunk carries access-control tags, and the query filters on the caller's groups before similarity scoring runs. Cache keys must include the permission set, or a cached response from one user can be served to another with different access rights.

**What the scoping reveals:** You now know you are designing for 10 million documents, 50,000 employees, a multilingual corpus, a sub-3-second p95 target, and retrieval-time permission enforcement. Those five facts bound the design. The connector architecture follows from the corpus size and source diversity. The embedding model follows from the language requirement. The retrieval-time permission check follows from the access model. The latency budget math follows from the p95 bar. Before you have drawn anything, you have named the constraints that will justify every component you are about to place.

That is what scoping does. It converts "design a RAG system" into a set of requirements specific enough to defend against.

## Worked Example 2: The Customer Support Chatbot

**The prompt:** "Design an AI-powered customer support system for an e-commerce company."

This prompt wears its familiarity as a trap. Every AI engineer has seen a customer support chatbot. The impulse is to draw the agent loop you already know: intake, classify, route, respond, escalate. That loop is fine. The question is what you route toward, what you respond with, and especially what you escalate, which you cannot answer until you know the success metric and the integration constraints.

**What a strong candidate asks:**

*What does "success" look like?* This is not a soft question. The answer is "resolve 70% of tickets without a human handoff." That number is now a design constraint. Your architecture needs a resolution rate, which means it needs a classifier that can recognize when it has resolved something and when it has not, escalation triggers specific enough to catch the 30% that need a human, and a measurement system that can track the rate. A design without this metric does not know if it is working.

*What is the existing ticket infrastructure?* The answer is Zendesk. Now the integration model is specified: the system receives tickets via webhook, handles them through its own flow, and either closes the ticket on resolution or assigns it to a human queue on escalation, with a context summary so the human agent does not start from scratch. That context summary is not optional polish; it is the mechanism that makes the handoff useful. An escalation that passes only a ticket number transfers work without context.

*What data sources does the agent need?* The answer: a product catalog with 1 million products, order history, and FAQs. Those three sources become three tools, with different access patterns. The order lookup tool is a read against the customer's order history. The product search tool is a semantic query against the catalog. Both are read-only. The returns tool creates a record: it requires a reason and a specific item list, not a free-form instruction. Write and read tools are separated, not because it is tidy but because giving an agent broad write access is a reliability risk.

*What languages does the system need to support?* Three languages: English, Spanish, and Mandarin. That affects both the model choice and the escalation logic for sentiment detection.

**The facet scoping surfaces here:** The 70% resolution target forces the question of escalation criteria. When does the system hand off? A shallow answer is "when confidence is low." The deeper answer names six triggers: explicit user request, high negative sentiment, payment disputes, low confidence after two attempts, complex multi-order issues, and refund amounts above a business-defined threshold. That last one is not a model confidence question: it is a business rule. The escalation logic without it hands refund disputes to the AI agent, which is a business risk the design should name and close.

**What the scoping reveals:** You are building an agent for 10,000 conversations per day, with a 70% resolution target, integrated with Zendesk, supporting three languages, backed by three scoped tools (two read, one write with explicit parameters), and with six named escalation criteria at least one of which is a business rule rather than a confidence threshold. The 70% target is the number your design must beat; the escalation criteria are the mechanism that keeps the 30% from being a reliability problem. Before you draw the agent loop, you know what goes inside it.

## How to Scope a Prompt You Have Never Seen

Scoping transfers across prompt types because the questions that matter are always variants of the same four inquiries: scale (how much, how many, how fast), users and access (who, with what permissions, from where), success criteria (what does "working" mean, what metric proves it), and integration and constraints (what already exists, what cannot change, what compliance applies). You do not need to memorize a checklist. You need to ask yourself, on every prompt, what you do not yet know that would change the design.

The practical move: after you hear the prompt, say one sentence that acknowledges it, then name the two or three dimensions you need to resolve before drawing. "Before I start, I want to make sure I understand the scale and access model, because those will shape the retrieval architecture." That sentence does two things: it demonstrates the scoping reflex, and it invites the interviewer to tell you what they care about, which steers the rest of the round.

One thing scoping is not: a way to run the clock. Five to eight minutes of genuine clarifying questions is a signal of engineering maturity. Twenty minutes of questions to avoid designing is visible to the interviewer. Ask what you need; then scope, state your priorities out loud, and draw.

## Core Concepts

- The first ten minutes of a design round test whether you scope an open-ended problem into a bounded one before drawing; the candidate who designs blind is solving a question they invented.
- Scope produces the numbers and constraints that justify every architectural choice; without them, component decisions are assertions, not reasoning.
- Three failure modes kill a design round before the first box lands: jumping to architecture, solving the wrong problem, and failing to manage the clock.
- The escalation criteria, success metric, and integration constraints on a support system are requirements scoping surfaces; a design that begins without them reaches wrong conclusions about what the agent must do.

<div class="claude-handoff" data-exercise="exercises/module5/reading-the-design-prompt/">

**Try It in Claude Code:** scope an open-ended design prompt of your own into your systems-design log: write the prompt, the clarifying questions, what they reveal, and the bounded requirements and priorities you would design toward.

</div>
