# System Semantics — Blueprint

## Positioning

*Sans Python* ends at the data seam. Module 5 Lesson 14 names the boundary precisely: you own the
query, the freshness SLO, and the lineage contract into the data platform; you do not build the
platform. *System Semantics* is what comes next. It is the deep build of everything that lesson
named and deferred.

The gap it fills is row 4 of `build-log/sans-python/antilibrary-gap-report.md`: data engineering
and SQL appear in 52% of AI Engineer postings, yet Sans Python teaches only the Docling ingestion
front door (M5 L11) and a single seam lesson (M5 L14). The interview screen is real, the coverage
is thin, and this book closes it.

**Placement in the sequence:** post-Sans-Python. The reader has shipped a governed multi-agent fleet
(M7), traced its costs and quality (M5 L6/L8), and run their first seam queries (M5 L14). This book
is not a prerequisite companion; it is the extension students reach for when they want to own the
platform side of the seam, not just contract with it.

---

## Thesis

Interpreting and routing data for AI systems is the data engineer's job, seen from the AI
engineer's seat. SQL is not a reporting language here; it is the interface to the corpus, the trace
store, the feature table, and the eval warehouse. Ingestion is not a data-ops abstraction; it is the
mechanism that determines whether the retrieval index is fresh enough to answer the question
correctly. Lineage is not a compliance checkbox; it is the chain that explains why an answer
changed, running from the document version that produced the chunk, through the embedding model that
placed it, to the eval verdict that graded it.

*System Semantics* teaches SQL and the data platform as operational instruments for an AI engineer:
ingestion (batch and streaming, with a freshness SLO), pipelines and orchestration (Airflow/Prefect,
dbt transformations, medallion layers), warehouses and lakehouses (Snowflake, BigQuery, Databricks /
Microsoft Fabric OneLake, Delta/Iceberg tables), event streaming (Kafka, change-data-capture,
Eventstream), and lineage (end-to-end provenance from source version to eval verdict, governed
through tools like Microsoft Purview Unified Catalog). Every concept lands in a running artifact; the
final portfolio piece is a multi-source pipeline that feeds an AI system with a documented freshness
SLO and a queryable lineage store.

---

## Scope

### In scope

- SQL as an operator skill: `GROUP BY`, window functions, CTEs, query patterns over telemetry and
  corpus tables; queries an AI engineer actually writes on the job
- Batch ingestion: Docling-to-warehouse pattern extended; scheduled loads, incremental merge, the
  nightly re-index; dbt models and tests as the transformation layer
  [MS-Learn: dbt job in Microsoft Fabric, dbt + Airflow orchestration]
- Streaming ingestion: Kafka fundamentals, change-data-capture, Eventstream routing events to
  lakehouses and eventhouses; the streaming vs. batch decision and the freshness tradeoff
  [MS-Learn: Microsoft Fabric Eventstream, Real-Time Intelligence, Eventhouse + KQL]
- Freshness SLOs: defining, measuring, and alerting on source-to-index lag; owning the target as an
  operational objective, not an afterthought
- Warehouse and lakehouse architecture: medallion pattern (bronze/silver/gold), Delta/Iceberg open
  formats, OneLake shortcuts, when to use structured warehouse vs. lakehouse for AI corpora
  [MS-Learn: Microsoft Fabric Lakehouse, Greenfield Lakehouse on Fabric, medallion architecture]
- Orchestration: Airflow DAGs, Prefect flows, pipeline scheduling and dependency graphs; not
  operating the cluster, but authoring and debugging the DAG that moves data
- Data lineage: end-to-end provenance in the AI system (document version to eval verdict); how
  lineage graphs are built and queried; Purview Unified Catalog as the enterprise lineage surface
  [MS-Learn: Microsoft Purview data lineage, Unified Catalog, column-level lineage]
- Contract with the platform: the AI engineer's read/write interface (schemas, SLAs, access
  patterns) versus the data engineer's build; collaboration vocabulary

### Deliberately out of scope

- Cluster operations: standing up Kafka, sizing a Spark cluster, managing Airflow workers; the
  reader uses these as services, not as an ops engineer
- dbt internals: Jinja macros, custom materializations beyond the standard four; the course teaches
  dbt as a transformation layer, not as a framework to extend
- Data warehouse modeling depth: star schema design, slowly changing dimensions, surrogate key
  patterns beyond what an AI engineer reads and queries
- Feature stores (Feast, Tecton) and MLOps experiment tracking: covered at literacy depth in Sans
  Python M5 L12; deepened in the planned Machine Learning book
- Stream processing internals: Kafka consumer group rebalancing, partition topology, Spark Streaming
  micro-batch tuning; operational knowledge, not authoring knowledge
- Data quality frameworks (Great Expectations, Soda) beyond writing a basic freshness assertion:
  governance tooling is introduced; mastery is out of scope
- BI and reporting (Power BI, Looker, Tableau): downstream consumers of the platform, not the
  platform itself

The cuts keep the frame tight: this is the AI engineer's data seam at depth, not a data engineering
degree.

---

## Ore to Module Map

Primary ore: `vault/made-with-ml` (data pipeline, MLOps workflow, data versioning, serving
pipelines) mapped via `ingredients/source/_repos/made-with-ml/curriculum-map.md`. Secondary ore:
`vault/ai-engineering-from-scratch` (M4/M5 infrastructure and production chapters) and
`vault/ai-performance-engineering` (deploy/serving). Survey at process-ore time via
`vault/MANIFEST.md`.

| Ore artifact | Target module |
|---|---|
| `made-with-ml` data.py, datasets/, MLOps notebook (data loading, versioning, splitting) | M1 SQL + M2 Batch Ingestion |
| `made-with-ml` deploy/jobs/workloads.sh, workloads.yaml (batch pipeline orchestration) | M3 Orchestration |
| `made-with-ml` serve.py, predict.py (offline/online inference seam) | M4 Streaming |
| `aefs` M4/M5 infrastructure chapters (serving, experiment tracking, evaluation) | M5 Warehouses / M6 Lineage |
| `ai-performance-engineering` (deploy/serving docs, NVIDIA GTC material) | M5 Warehouses |

---

## Curriculum Arc

**Module 1: SQL as an Operator Skill**
The twelve queries that answer production questions: p95 latency by route, cost by tenant,
eval-pass rate over a rolling window, corpus freshness by source. `SELECT`, `GROUP BY`, window
functions, CTEs over real telemetry. The literacy test: can you answer "where did the quality go"
with a query, not a guess?

**Module 2: Batch Ingestion**
The nightly corpus reload as a production system: scheduled loads, incremental merge, Docling
extended into a warehouse target, dbt models that transform raw ingestion into clean corpus tables,
and the test suite that gates promotion. Freshness SLO definition and measurement for batch sources.
[MS-Learn: Lakehouse ingestion options, dbt job in Fabric, medallion pattern]

**Module 3: Orchestration**
Airflow DAGs and Prefect flows as the scheduler for every pipeline in this book. Writing a DAG that
depends on upstream data, retries on failure, and alerts on breach. The dbt + Airflow pattern for
transformation pipelines. Not running the cluster; authoring and debugging the graph.
[MS-Learn: Apache Airflow + dbt in Microsoft Fabric Data Factory]

**Module 4: Streaming and Change-Data-Capture**
Kafka topics, consumer groups, and the CDC pattern that turns database writes into a feed. The
streaming-vs.-batch decision crystallized into a freshness SLO: which sources need seconds-to-index
versus hours-to-index. Eventstream routing streaming data to a lakehouse or eventhouse. The
streaming freshness monitor.
[MS-Learn: Fabric Eventstream, Eventhouse KQL, Real-Time Intelligence]

**Module 5: Warehouses and Lakehouses**
Snowflake / BigQuery as the structured query surface; Delta Lake and Iceberg over object storage as
the open-format lakehouse; Microsoft Fabric OneLake and the medallion architecture (bronze/silver/
gold). When to use which tier, and the AI engineer's access pattern to each.
[MS-Learn: Greenfield Lakehouse, Fabric terminology, OneLake shortcuts, Delta tables]

**Module 6: Lineage: From Document to Eval Verdict**
End-to-end provenance for the AI system: source document version, chunk id, embedding model pin,
retrieved context hash, cited answer, eval verdict. Building and querying a lineage store. The
Purview Unified Catalog as the enterprise surface for cross-system lineage. Column-level lineage
for audit and impact analysis.
[MS-Learn: Microsoft Purview data lineage, Unified Catalog, lineage granularity]

**Module 7: The Pipeline Artifact (Portfolio)**
A runnable multi-source ingestion pipeline that feeds an AI retrieval system. Batch source (a
document corpus, nightly dbt-transformed) and streaming source (a CDC feed of live updates), both
routed through a medallion lakehouse to a vector index. The pipeline carries a documented freshness
SLO on each source leg and writes a lineage row for every indexed document. Orchestrated with
Airflow. `python smoke.py` proves end-to-end: batch loads, streaming updates, freshness breaches
fire, lineage resolves answers to source versions.

**Module 8: The Data Platform Exam (Portfolio)**
Given a broken pipeline and a degraded retrieval system: diagnose the data failure with SQL queries
over the trace and corpus tables; identify the freshness breach; walk the lineage back to the
document version that changed the answer; propose and implement the fix. Graded against a rubric
modeled on Sans Python M8: diagnosis query, breach identification, lineage walk, remediation
commit. The portfolio artifact is the graded solution plus the diagnostic query set.

---

## Portfolio Artifact Strategy

Modules 7 and 8 are the runnable proof, mirroring Sans Python M6/M7/M8. The reader exits with two
GitHub artifacts:

**Artifact 1 (M7): The Pipeline.** A fully orchestrated, multi-source ingestion pipeline. It
demonstrates: batch ingestion with dbt transformation into a medallion lakehouse; CDC/streaming
ingestion via Kafka or Eventstream; a freshness SLO monitor that alerts on breach; a lineage store
that resolves every indexed document to its source version, chunk id, and eval verdict; Airflow
orchestration with retry and alerting. Every layer is smoke-tested and pytest-asserted.

**Artifact 2 (M8): The Diagnostic Exam.** A broken system, a diagnostic playbook, and a working
fix. The reader must query their way to the answer, walk the lineage, and prove the repair.
Interviewers see: SQL fluency under pressure, lineage reasoning, and production instincts.

Together these demonstrate the 52% screen at production depth: not textbook knowledge but a running,
queryable, lineage-tracked pipeline that feeds an AI system.

---

## Dual-Use Note

Every page is written to be read by a human learner and ingested by an LLM. Dense, linked, plain
markdown, no filler. An AI agent navigating this book should be able to answer "what does the
freshness SLO for the batch leg of the M7 pipeline look like" from the lesson text alone. The same
density makes the human reader fast.

---

## Candidate Names (GATE-NAME-BOOK)

**Lead: System Semantics.** Data engineering taught as the interpretive layer between raw data and
AI inference. "Semantics" captures the why: this is not about moving bytes; it is about what those
bytes mean to an AI system and how the pipeline preserves or destroys that meaning in transit.
Distinct, memorable, and true to the thesis.

**Alt 1: The Data Seam.** Directly extends M5 L14's title and signals continuity for Sans Python
readers. Clear, practical, and grounded. Risk: sounds like a chapter supplement rather than a
standalone book; may undersell the depth.

**Alt 2: Pipeline Fluency.** Foregrounds the operational skill (running a production pipeline)
rather than the conceptual frame. Approachable for hiring screens. Risk: generic enough to blur
with any data-engineering primer; does not distinguish the AI-system focus.

Propose the final name at `GATE-NAME-BOOK` before starting ore processing.
