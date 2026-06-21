# The Full Design Under Pressure

The real test of SPIDER is not whether you know the phases. It is whether you can run them under a clock, in front of someone who is watching how you think, on a prompt you have never seen.

This lesson does three things. It runs one complete design from the first question through the final reliability check, so you can watch the whole motion at speed. Then it turns the weak-design audit on that design, the way Module 2 turned the weak-answer audit on a behavioral story, so you have a checklist you can run on your own work before the room does. Finally it shows how the same prompt produces a different design under a different stress, because the design is not a fixed artifact to memorize; it bends to the signal being evaluated.

## The Prompt

*"Design the memory system for a personal AI assistant that works with a user over months. It should remember preferences and facts, learn from past sessions, recall relevant history at the right moments, and forget what it should not keep. Sessions can run for hours. Support one million users."*

The clock starts now.

## Phase S: Scope and Clarify (0:00 to 0:05)

Before drawing anything, you need numbers. The prompt gave you the shape; you need the dimensions.

You ask: What is the p95 latency budget for recall on each turn? What are the deletion requirements, GDPR or otherwise? How long should facts persist, and does the user control that? Is memory shared across devices, or per-device? What counts as a session, and when does one end?

The interviewer fills in the constraints: p95 under 150ms for recall; full GDPR deletion required; cross-device, cross-session memory that persists over months; one million users; sessions up to hours long.

You state back the scope explicitly before moving on: "So I am designing a multi-tier memory system for 1M users, sessions up to hours, cross-session persistence over months, 150ms p95 recall budget per turn, and GDPR deletion as a hard constraint. I will prioritize correctness of what gets written into memory and the relevance gate on what gets read back, because a wrong memory is worse than a missing one."

That last sentence is not throat-clearing. It is the priority matrix, stated out loud, before you draw anything.

## Phase P: Prioritize Requirements (0:05 to 0:08)

Three tensions are live in this prompt.

Freshness vs. cost: writing to memory after every session is expensive; batching is cheaper but delays cross-session recall. You will write asynchronously after session close, with a queue and worker pool, and note the tradeoff explicitly.

Recall precision vs. recall completeness: the prompt says "recall relevant history at the right moments." The failure mode is stuffing weak matches into the context window. You will design a relevance gate that drops weak matches rather than including them, and you will call that out as a first-class decision.

Privacy vs. utility: GDPR deletion must be complete and fast. That constrains the storage architecture more than the retrieval architecture.

You state the priority order out loud: "I will optimize for write correctness first, recall precision second, deletion compliance third, and raw storage cost fourth. That ordering drives the design."

## Phase I: Initial Architecture (0:08 to 0:18)

You draw four tiers before explaining any of them, so the interviewer can see the structure before the detail.

**L1: Working memory.** The context window for the current session. Tool results, the current turn, a scratchpad. This is managed by compaction and just-in-time loading; it is not persisted.

**L2: Episodic memory.** What happened. Past session summaries, trajectories, outcomes. Stored in a vector database, partitioned by user_id. Retrieved by a weighted combination of similarity, recency, and importance.

**L3: Semantic memory.** What is true. Extracted facts and preferences, each with provenance: where the fact came from, when, and how confident you are in it. Structured records or a per-user knowledge graph.

**L4: Procedural memory.** How to do things. Learned workflows, per-user playbooks, style preferences. Versioned files loaded on demand.

You narrate each component with one sentence on what it does and one on why it is separate. L1 is separate from L2 because in-session context management and cross-session memory are different problems with different latency and persistence requirements; conflating them is the first place designs go wrong.

The interviewer nods. You keep moving.

## Phase D: Deep Dive Critical Paths (0:18 to 0:33)

You signal intent before diving: "I am going to go deep on the write path, because that is where the hard problems live in a system like this. Retrieval is conceptually straightforward; extraction, dedup, and conflict resolution are where most candidates go thin."

### The Write Path

A session ends, or a checkpoint fires. The write path runs four steps in order.

**Step 1: Summarize the episode.** A cheap model, something at the Haiku tier, summarizes the session into an episodic entry with metadata: timestamp, topics discussed, outcome, sentiment. This entry goes into L2 as an embedding plus structured metadata.

**Step 2: Fact extraction.** The same cheap model runs a separate pass over the session, extracting candidate facts and preferences with a strict schema. "User prefers Python over JavaScript for scripting tasks." "User has a meeting cadence of Monday standups." Cheap model here because the schema is tight and the extraction is classifiable; you do not need a frontier model for this.

**Step 3: Dedup and conflict resolution.** Each candidate fact is checked against L3. If the fact already exists with the same meaning, you update the timestamp and confidence. If the new fact conflicts with an existing one, you apply a supersession rule: newer plus higher confidence wins, but the old fact is kept with a `valid_to` timestamp, not deleted. This bitemporal record makes supersession auditable and reversible. For ambiguous conflicts, you store the candidate as a provisional fact and confirm it with the user at the next natural opportunity.

**Step 4: Importance filter.** Chit-chat is discarded. Preferences, commitments, corrections, and domain facts are kept. The filter runs as a classifier; the threshold is tuned to prefer false negatives over false positives, because the cost of a wrong memory is higher than the cost of a missing one.

The interviewer asks: "What happens to memory poisoning? If a user pastes untrusted content into a session, can it write into memory?"

You answer: "Yes, and that is a named attack surface. Untrusted content written today can be trusted and acted on tomorrow. The defense is provenance tags: every L3 fact carries its source, and facts derived from user-pasted or external content are tagged as unverified. A gate in the write path can hold unverified facts in a quarantine tier until a secondary review, either a model review pass or explicit user confirmation."

### The Read Path

Each turn, you build a recall query from the current intent. You retrieve top-k from L2 using a weighted combination of similarity, recency, and importance. You pull matching facts from L3 by semantic match and topic tag.

Then the relevance gate runs. Weak matches are dropped. You are not filling a context window; you are picking the two or three memories that are most likely to improve this response. The budget is a few hundred tokens of memory per turn, never a transcript dump.

You say it plainly: "A context window full of weak memories is worse than no memory at all. Wrong recall poisons the response. The gate is not an optimization; it is a correctness requirement."

**Latency budget:** ANN search on a per-user slice in a user-partitioned vector DB is fast; the slice is small. L3 lookup on a per-user fact table hits a structured index. The 150ms p95 budget is achievable because you are not searching the full index; you are searching one user's partition.

## Phase E: Evaluate and Observability (0:33 to 0:38)

Four things to instrument.

**Recall precision:** sample 1% of production turns and judge whether the recalled memories were relevant to the response. A judge model scores relevance; low precision is a signal to tighten the relevance gate threshold.

**Write coverage:** what fraction of sessions produce at least one L3 fact? A sharp drop in write coverage signals the extraction model is under-extracting, possibly due to a model update.

**Deletion latency:** GDPR deletion must complete within the statutory window. You log deletion jobs and alert if any exceed the SLA, which you set internally at 24 hours to give buffer.

**Conflict rate:** how often does a session's extracted facts conflict with existing L3 facts? A rising conflict rate signals either model drift (the extraction model changed what it calls a fact) or genuine user behavior change.

You also flag a known weakness unprompted: "The importance filter threshold is set once at launch and then held. In practice, what counts as important varies by user and changes over time. A production system would run per-user calibration, but that adds complexity I have not designed for. If the interviewer wants to go deeper there, I can."

That sentence does two things: it flags a real weakness before the interviewer does, and it invites steering rather than making an assumption about what to cover next.

## Phase R: Reliability and Scale (0:38 to 0:43)

**Failure modes:**

The write path is async. If the queue backs up or the worker pool is overwhelmed, sessions can close without their memories being persisted. You add idempotency keys to every write job so retries do not create duplicate facts, and you alert when queue depth exceeds a threshold.

If the vector DB is unavailable, the read path falls back to L3 facts only (structured lookup, more available than the vector index) and then to no memory. The agent degrades gracefully to a sessionless baseline rather than failing.

**Scale:**

Storage at 1M users is bounded. A few thousand episodic entries plus a few hundred L3 facts per active user; the vector DB is partitioned by user_id so searches are always within one user's slice. The expensive operation is the write path at session close; it runs async and the worker pool scales horizontally.

The latency budget for the read path closes because the per-user index is small. At 1M users, each with at most a few thousand L2 entries, the ANN search runs against a tiny slice. The global index size is large; the per-query search space is not.

**Build vs. buy:** Mem0, Zep, and Letta (formerly MemGPT) all provide production memory primitives. The design above is the from-primitives version, which is what the design round is evaluating. In production, you would evaluate those frameworks against the from-scratch cost before committing either way.

*Clock stops at 0:43. You are on budget.*

## The Weak-Design Audit

Now you turn the audit on your own design. Not to congratulate yourself, but to find where the room is about to probe you.

The audit runs by category. For each one, ask the question against your own design.

### Architecture

**"Did I design the full pipeline, or just the interesting half?"** The write path and the read path are both present. The forgetting and deletion path is also present (decay, consolidation, GDPR deletion). Full pipeline: pass.

**"Does every component have a fallback?"** The vector DB has a fallback to L3-only. The write path has idempotency and retry. Single provider dependency: this design did not name the vector DB vendor or the extraction model provider; in a real design, you would name failover explicitly. Flag this as a gap.

**"Did I pick one model for everything?"** No: the extraction pass uses a cheap model; the session summarizer uses a cheap model; the agent itself uses whatever tier the product requires. Pass, but you did not name a routing decision on the agent model itself. Another gap to flag.

### Technical Knowledge

**"Did I explain why hybrid retrieval, or just name it?"** The read path uses similarity plus recency plus importance weighting, not pure vector similarity. You explained why: recency matters for memory in a way it does not for RAG over a document corpus. Pass.

**"Did I treat the context window as infinite?"** You named the recall budget explicitly: a few hundred tokens per turn, never a transcript dump. Pass.

**"Did I account for token economics on the write path?"** You specified a cheap model for extraction and summarization. Pass, but you did not give a cost estimate. That is a gap for a staff-level answer.

### Communication

**"Did I signal intent before every deep dive?"** Yes: "I am going to go deep on the write path." Pass.

**"Did I check in at phase boundaries?"** The flag at 0:33 inviting steering was one check-in. There should have been one after the initial architecture (0:18) as well: "Before I deep dive, is there a part of this you want me to prioritize?" Note that as a protocol repair for your next run.

**"Did I critique my own design before the interviewer did?"** Two unprompted flags: the importance filter calibration, and the missing per-user routing decision on the agent model. Pass.

### AI-Specific

**"Did I treat the extraction model as a black box?"** You specified cheap-model tier and strict schema, which implies awareness of prefill cost and output formatting constraints. Pass on the surface; if probed on batch vs. streaming inference for the extraction pass, you would need to go deeper.

**"Did I name hallucination risk?"** The provenance tagging and the unverified-fact quarantine address the memory poisoning case. You did not address hallucination in the agent's responses generally; for a memory system design that is acceptable scope, but note it.

**"Did I treat security as a first-class design concern?"** Memory poisoning was addressed when probed. Tenant isolation (per-user partition keys, no cross-user similarity search) was named explicitly. GDPR deletion was named as a hard constraint and wired into the architecture. Pass.

### Eval-Specific

**"Did I design measurement, or just describe the system?"** Four instrumented metrics, with alert conditions. Pass.

**"Did I link offline eval to production outcomes?"** Recall precision is sampled in production. Deletion latency is monitored against the statutory SLA. Pass.

**"Did I name the write path as the hard part?"** You foregrounded it, named it explicitly, and spent the majority of the deep dive there. Pass.

**Verdict:** The design is solid. The two clearest gaps are the missing token cost estimate (a staff-level signal) and the missing explicit check-in at 0:18. Neither kills the answer. Both should be repaired in the next run.

## The Same Prompt, a Different Stress

Here is what the module overview said and what this lesson has been building toward: the design is not a fixed artifact you memorize. It bends to the signal being evaluated.

Take the same prompt. Two different interviewers stress it differently.

**Stress A: Latency and scale.** The interviewer keeps returning to "one million users" and "sessions up to hours." Every follow-up is about throughput, partitioning, the cost of the write path at scale.

Under this stress, the deep dive shifts. You spend less time on conflict resolution and provenance tagging, and more time on the write path's queue architecture: how you size the worker pool, how you avoid write amplification when millions of sessions close overnight, how you shard the vector DB for parallel ANN, how you keep the per-user read slice small as user history grows. The latency budget math becomes the centerpiece of the E phase: you work through the 150ms breakdown component by component, with concrete estimates for ANN on a user-partitioned index versus a full index. The cost estimate comes into the R phase: what does the extraction pass cost at 1M sessions per day, and at what scale does the cheap model become the dominant spend?

The design under stress A de-emphasizes provenance tagging and the unverified-fact quarantine. Those are real problems, but the interviewer's signal is scale and latency; foregrounding memory poisoning when they are asking about throughput is misreading the room.

**Stress B: Correctness and compliance.** The interviewer keeps returning to "forget what it should not keep" and "GDPR." Every follow-up is about deletion, about what happens when a fact is wrong, about how you prevent the memory system from encoding a user's mistake as permanent truth.

Under this stress, the deep dive shifts the other direction. Conflict resolution and the bitemporal record become the center: you walk through exactly how supersession works, why `valid_to` is not deletion, and what the audit trail looks like when a user's preference changes. The unverified-fact quarantine gets a full design: what the review gate looks like, who triggers the confirmation, how long an unverified fact sits before it either graduates or is discarded. The GDPR deletion path gets explicit: partition key design, the cascade that removes L2/L3/L4 rows, the cache invalidation that prevents deleted facts from appearing in recall.

The E phase under stress B foregrounds deletion latency monitoring and the audit log; the R phase foregrounds the failure mode where a deletion job silently fails.

The same architecture. Different deep-dive targets. Different emphasis in evaluation and reliability. That is not inconsistency; it is calibration. You read the stress, you direct the 15 minutes of deep dive at the thing the interviewer is actually evaluating, and the design you produce demonstrates production judgment rather than a rehearsed answer.

That is why the SPIDER phases are a motion, not a template. The phases are stable; what you fill them with bends to the signal.

## Core Concepts

- The write path is the hard part of a memory system design: extraction, dedup, conflict supersession with bitemporal records, and importance filtering are all harder than retrieval and are where most designs go thin.
- Wrong recall is worse than no recall; the relevance gate is a correctness requirement, not an optimization, and it belongs in the design as a first-class component.
- The weak-design audit runs by category against your own design before you stop talking: architecture completeness, technical knowledge, communication discipline, AI-specific risks (poisoning, hallucination, tenant isolation), and eval coverage.
- The same prompt produces a different design under a different stress; the phases of SPIDER are stable, but the deep-dive target and the priority ordering bend to the signal being evaluated.

<div class="claude-handoff" data-exercise="exercises/module5/the-full-design-under-pressure/">

**Try It in Claude Code:** run the full SPIDER motion on your systems-design-log design under a 45-minute timer, then turn the weak-design audit on your own design and record the verdict: which red flags it risks, and the one change you made after the audit.

</div>
