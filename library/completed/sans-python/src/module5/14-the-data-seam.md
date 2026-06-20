# The Data Seam: SQL, Streams, and Lineage

Every signal this module taught you to watch lands somewhere. The spans your observability layer emits, the scores your eval gate returns, the per-call dollars your FinOps stamp records; none of it is a dashboard first. It is rows first. And the morning someone asks why p95 latency for tenant 7 doubled last Tuesday, and whether answer quality moved with it, you do not squint at a graph and guess. You answer it the way every data team answers every question: you query. This lesson is the seam where your AI system meets the data platform, and the slice of that seam a Production AI Engineer owns.

## You Own the Seam, Not the Platform

Data engineering is the other half of the MLOps cusp this course sits on, and it is a deep discipline: pipelines that move billions of rows, warehouses modeled for query, streaming systems that never sleep. You are not going to build those, and pretending otherwise is how the fork breaks. What you own is narrower and more useful: the place where the AI system reads from the data platform and writes back to it. Where the retrieval corpus comes from and how fresh it stays. Where the traces, evals, and costs land so they can be queried. Which events the agent emits and who consumes them. The data engineer builds the warehouse; you decide what your system puts in it and what you ask of it. Own that boundary cleanly and you are the person who connects AI to the data platform, which is exactly the hire; blur it and you are rebuilding Kafka badly on a deadline.

## Your Telemetry Is a Dataset

Here is the move most application engineers never make: treat your own telemetry as a dataset you query, not a feed you watch. The traces from Lesson 06, the eval verdicts from Module 2, the cost stamps from Lesson 08 are all tables, whether they live in a trace tool, a warehouse, or a single SQLite file on the box. The Production AI Engineer is the one who can sit down and write the query: p95 latency grouped by route, total cost grouped by tenant, eval pass-rate over a rolling seven-day window. The test is binary. Either you can answer "where did the latency, the money, or the quality go" with a `GROUP BY`, or you are guessing from a chart someone else built.

SQL is the lingua franca for a reason: it is what the warehouse speaks, what the trace tool exposes, and what every data engineer you will work with reads fluently. You do not need window functions and recursive CTEs on day one. You need to be unafraid of a `SELECT` over your own production data, because the answer to "is this regression real" lives in that query and the confidence interval around it, not in an eyeballed line that went up.

## Two Shapes of Ingestion, One Freshness SLA

Lesson 11 ingested documents in a batch: point Docling at a corpus, parse, chunk, index, done. Production data arrives in two shapes, and the difference is operational. Batch is the nightly corpus reload, the warehouse table refreshed on a schedule, the re-index after a quarterly policy update. Streaming is the change-data-capture event, the support ticket that just landed, the document-changed webhook that should reach the index in seconds. Most systems use both, and which one a given source needs is a decision, not a default.

The decision crystallizes into one number the Production AI Engineer owns: the freshness service-level objective. How stale may retrieval be before the answer is wrong? A compliance corpus that changes quarterly tolerates a nightly batch; a bot answering from live inventory or open tickets needs streaming or near-real-time re-indexing, or it will cite a world that no longer exists. Freshness is an SLO like latency or error rate: you set the target, you measure the lag between source-change and index-update, and you alert when it breaches. Naming it is the job; an index with no stated freshness target is one quietly serving yesterday's truth as today's.

## Lineage: From Document Version to Eval Verdict

Lesson 11 left you with the reproducible triple: pin the corpus snapshot, the chunking config, and the embedding-model id, and any index is reproducible. Production lineage extends that triple into a chain that runs the whole length of the system: which document version produced which chunk, which embedding, which retrieved context, which cited answer, and which eval verdict graded it. The chain is what turns "the answer got worse" from a mystery into a lookup. An answer changed; walk its lineage back and you find the corpus reload that swapped the source paragraph, or the embedding upgrade that moved the neighborhood, instead of bisecting the whole pipeline by hand.

You have already seen one end of this. The Module 6 regulated RAG chatbot made the citation visible to the *reader*: every claim carries the source it came from. Lineage is the same chain made visible to the *operator*: every answer carries the data that produced it. It is the retrieval-side twin of the agent audit log from Modules 4 and 7, where every action carried its correlation id; here every answer carries its provenance. Same instinct, applied to data instead of actions: nothing the system produces should be unexplainable after the fact.

## The Vocabulary and the Boundary

To collaborate with a data team you have to speak the nouns, so name them and place yourself. Storage splits into the **warehouse** (Snowflake, BigQuery: structured, query-optimized) and the **lakehouse** (Iceberg or Delta tables over object storage: cheaper, open formats, one store for raw and modeled data). Movement splits into **batch orchestration** (Airflow or Prefect scheduling jobs, dbt transforming tables in the warehouse) and **streaming** (Kafka carrying events, change-data-capture turning database writes into a feed). You read from these and write to these. You do not build or operate them.

That last sentence is the boundary, and holding it is the skill. The pipelines, the warehouse modeling, the streaming topology, the data-quality framework: that is the data engineer's build, and it is the spine of a focused Data Engineering companion, not this book. Your deliverable is the seam: the query that answers the production question, the freshness SLO on the index, the lineage chain that explains an answer, and a clean contract with the platform on both sides. Knowing precisely where your job ends is not a gap in your skills; it is the discernment that keeps the system honest and keeps you valuable as the engineer who wires AI into the data platform rather than the one who reinvents it.

## Core Concepts

- Your telemetry (traces, eval verdicts, cost stamps) is a queryable dataset; a Production AI Engineer answers "where did the latency, cost, or quality go" with a SQL `GROUP BY`, not a guess at a chart.
- Ingestion comes in two shapes, batch and streaming, and the index carries a freshness SLO: a stated number for how stale retrieval may be, measured as source-to-index lag and alerted on like any other objective.
- Lineage extends Lesson 11's reproducible triple end to end (document version, chunk, embedding, retrieved context, cited answer, eval verdict), so a changed answer is a lookup, not a bisection; it is the operator-facing twin of the reader-facing citation and the agent audit log.
- You own the seam into the data platform (the reads, the writes, the queries, and the freshness and lineage contracts), not the platform itself; the pipelines, warehouse modeling, and streaming infrastructure are the data engineer's build and a focused companion book.

<div class="claude-handoff" data-exercise="exercises/module5/14-the-data-seam/">

**Build It in Claude Code**: Add a data seam to `module5-serving/`. Persist the telemetry the stack already emits (spans with latency and route, cost stamps with tenant, eval verdicts) into a local SQLite store, then write three queries an operator actually runs: p95 latency by route, cost by tenant, and eval pass-rate over a rolling window. Put a freshness SLO on the Docling index from Lesson 11 (record an index-built timestamp and a max age, flag a breach), and record a lineage row linking each answer to its corpus version, chunk id, and eval verdict, with one query that walks an answer back to the document version that produced it. Prove it: `python smoke.py` loads sample telemetry, runs the three queries against known values, flags a deliberately stale index, and resolves one lineage chain end to end; `python -m pytest tests/` asserts the p95 query is correct, the freshness breach fires only when stale, and the lineage walk returns the right source version.

</div>
