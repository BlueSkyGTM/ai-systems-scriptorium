# The AI Engineer's Access Pattern

You do not own the warehouse. You do not run the lakehouse. And you still have to answer for the data your AI system reads: which version, which surface, which tier. That is the position, and the skill is reading correctly from a system you did not build.

## Read-Only by Contract

The Fabric Lakehouse SQL analytics endpoint is read-only. It serves DQL: `SELECT`, `WITH`, `GROUP BY`. No `INSERT`, no `UPDATE`, no `DELETE`. Writes go through the Delta table directly; the SQL endpoint exposes the result for querying. [MS-Learn lakehouse overview: https://learn.microsoft.com/fabric/data-engineering/lakehouse-overview]

The Fabric Warehouse is different: it gives you full T-SQL DML. But the AI engineer's use of both surfaces is the same posture: read-only. You are not the schema owner. You are not the platform team. Your job is to query a surface the data team built and answer a question about AI system behavior. [MS-Learn decision guide: https://learn.microsoft.com/fabric/fundamentals/decision-guide-lakehouse-warehouse]

This is the same stance from Module 1, two tiers up. In M1 you queried a telemetry schema your production system emitted; you did not own the schema, you read it. Here the schema is a gold corpus on a warehouse or lakehouse surface. Same contract, different tier.

## Tier-Chosen by Workload

The read is not just read-only; it is tier-chosen. You pick the surface based on what the downstream job needs, not what is convenient.

Structured BI goes to the warehouse. An AI engineer building a compliance dashboard queries the warehouse surface, where governed SQL runs aggregates that a Power BI report or a stakeholder query can consume without format negotiation.

```python
# warehouse.py: the warehouse is READ-ONLY in this module; writes go through the Delta table.
def doc_count_by_category(df):
    return duckdb.query("SELECT category, COUNT(*) AS doc_count FROM df GROUP BY category ORDER BY doc_count DESC").df()
```

Open-format ML and RAG go to the lakehouse. An embedding pipeline, a feature-store extraction, or a retrieval corpus reads the same gold corpus from Delta, because Spark, a local DuckDB session, and a vector pipeline can all open that format without a proprietary driver or a format conversion.

The router makes this explicit:

```python
choose_tier("bi dashboard for compliance reporting")   # -> "warehouse"
choose_tier("rag corpus embeddings for retrieval")      # -> "lakehouse"
choose_tier("feature-store extraction for model training")  # -> "lakehouse"
```

`choose_tier` raises on an unknown pattern rather than guessing. A silent default ships data to the wrong surface; raising forces the engineer to name the workload before the read starts.

## What the Contract Covers

The data team owns the schema, runs the platform, and sets the write path. Your contract with them is narrow and explicit: you read the surface they expose, you do not mutate it, and you pick the tier before the query runs.

That narrowness is not a limitation. It is what lets you reason about freshness, lineage, and correctness without owning the pipeline. When something goes wrong, "I read the warehouse surface at this version with this query" is a statement you can verify. "I wrote to the Gold layer to fix the data" is not your call.

The read-only access pattern is the seam. Keep it.

## Core Concepts

- The Fabric Lakehouse SQL analytics endpoint is read-only (DQL only); writes go through the Delta table, so the AI engineer's access on that surface is read-only by design, not by discipline.
- The Fabric Warehouse supports full T-SQL DML, but the AI engineer treats both surfaces as read-only: you query the schema the data team owns, you do not mutate it.
- Tier selection is per workload, made before the query runs: structured BI to the warehouse (governed SQL, dashboard-ready aggregates), open-format ML and RAG to the lakehouse (any-engine Delta reads, no format conversion).
- `choose_tier` raises on an unknown pattern rather than defaulting; a silent wrong-tier choice ships data to the wrong surface and is harder to audit than an explicit error.

The access contract you hold here, read a versioned corpus you did not write, on a surface someone else built, is the same contract that lets Module 6 trace any AI system answer back to the exact corpus version it cited.

<div class="claude-handoff" data-exercise="exercises/module5/the-ai-engineers-access-pattern/">

**Build It in Claude Code**: Write a read-only access helper (`doc_count_by_category`) that queries the gold corpus through the warehouse surface without mutating it, and a tier router (`choose_tier`) that, given a workload description, returns `"warehouse"` for BI workloads and `"lakehouse"` for ML and RAG workloads; prove the read does not change the Delta table's version (assert the version before and after the query is identical), and prove the router picks `"warehouse"` for compliance reporting and `"lakehouse"` for RAG corpus and feature-store workloads.

</div>
