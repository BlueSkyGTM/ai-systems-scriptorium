# Warehouse vs Lakehouse: One Store Cannot Serve Both Masters

The BI team wants governed T-SQL, fast dashboard queries, and the right to run `UPDATE` statements when a category label changes. The ML team wants the corpus in an open format that Spark, a local DuckDB session, and a vector pipeline can all read without a proprietary driver. You cannot make one store optimal for both, so you choose per workload.

That choice is the whole module.

## Two Surfaces, One Store

Microsoft Fabric keeps everything in Delta format on OneLake. That part is not a choice: both a Fabric Warehouse and a Fabric Lakehouse store data in the same open Delta files on the same underlying object storage. The difference is the SQL surface sitting on top.

A **Fabric Warehouse** gives you a full T-SQL endpoint: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, multi-table ACID transactions, cross-database joins, the works. It is the surface a BI analyst or a Power BI report targets. The format is governed, the schema is enforced, and the DML runs. [[MS-Learn decision guide: warehouse vs lakehouse](https://learn.microsoft.com/fabric/fundamentals/decision-guide-lakehouse-warehouse)]

A **Fabric Lakehouse** gives you data in open Delta/Parquet over OneLake and a SQL analytics endpoint for structured queries. That endpoint is read-only: DQL only, no `INSERT`, no `UPDATE`, no `DELETE`. Its strength is openness: the same Delta table a Spark job wrote is the table your embedding pipeline reads, with no copy and no conversion. [[MS-Learn lakehouse overview](https://learn.microsoft.com/fabric/data-engineering/lakehouse-overview)]

The split is not warehouse-OR-lakehouse. It is warehouse-for-BI, lakehouse-for-ML, both over Delta on OneLake.

## The Managed Alternatives

Outside Fabric the same split plays out at the managed layer. Snowflake and BigQuery are the structured warehouse tier: proprietary storage, full SQL, governed schema, built for analysts and dashboards. Delta Lake and Apache Iceberg are the open lakehouse formats: Parquet files with a transaction log, readable by any engine that understands the spec.

The tradeoff is identical. The managed warehouse is faster to operate, harder to escape. The open format is portable, readable by every tool in the stack, and requires you to manage your own engine.

## Encoding the Decision

The choice encodes cleanly as keyword routing. A workload that mentions BI, dashboards, T-SQL, reporting, or DML belongs in the warehouse. A workload that mentions ML, RAG, embeddings, open format, Delta, Spark, or corpus belongs in the lakehouse.

```python
def choose_tier(access_pattern: str) -> str:
    """Return "warehouse" or "lakehouse" for the given access pattern; raise on unknown."""
    normalised = access_pattern.lower()
    for kw in _WAREHOUSE_KEYWORDS:   # bi, dashboard, t-sql, reporting, dml, power-bi, ...
        if kw in normalised:
            return "warehouse"
    for kw in _LAKEHOUSE_KEYWORDS:   # ml, rag, embedding, open-format, delta, spark, corpus, ...
        if kw in normalised:
            return "lakehouse"
    raise ValueError(f"Unknown access pattern: {access_pattern!r}.")
```

Unknown patterns raise rather than guess. A system that silently defaults the wrong tier ships data to the wrong surface; one that raises forces the engineer to name the workload explicitly.

## The Two Queries

The module artifact seeds a small gold corpus and runs both surfaces against it. The warehouse query is a structured aggregate over a DuckDB relation (the local stand-in for T-SQL):

```python
def doc_count_by_category(df):
    return duckdb.query("SELECT category, COUNT(*) AS doc_count FROM df GROUP BY category ORDER BY doc_count DESC").df()
```

The lakehouse write is an open-format Delta write that any downstream engine can read without a conversion step:

```python
write_deltalake(delta_path, df, mode="overwrite")   # open Delta/Parquet, any engine can read it
```

Same gold corpus. Two surfaces. The query answers a BI question with governed SQL; the Delta write puts the corpus in an open format a vector pipeline can reach. Neither surface replaces the other.

## Core Concepts

- A Fabric Warehouse and a Fabric Lakehouse both store data in Delta on OneLake; the difference is the SQL surface: the warehouse gives full T-SQL with DML, the lakehouse SQL endpoint is read-only (DQL only).
- Choose the warehouse when the consumer needs governed SQL and write-back (BI, dashboards, reporting); choose the lakehouse when the consumer needs open-format access (ML, RAG, embedding pipelines, Spark).
- Snowflake and BigQuery are the managed warehouse tier; Delta Lake and Apache Iceberg are the open lakehouse formats. The tradeoff is the same: governance and speed vs portability and openness.
- The routing decision is per workload, not per system: the same gold corpus can feed a warehouse surface for BI and a Delta table for ML from the same underlying storage.

When the corpus lands in two places, pick the tier before you write: the wrong surface means a read-only endpoint for the analyst or a proprietary format the embedding pipeline cannot open.

<div class="claude-handoff" data-exercise="exercises/module5/warehouse-vs-lakehouse/">

**Build It in Claude Code**: Write the gold corpus (doc_id, title, text, content_hash, category) as a Delta table using `write_deltalake` (the open lakehouse format), query it with DuckDB's `doc_count_by_category` to get per-category counts (the warehouse stand-in), then write `choose_tier(access_pattern)` with the `_WAREHOUSE_KEYWORDS` and `_LAKEHOUSE_KEYWORDS` sets so it returns `"warehouse"` for structured BI workloads and `"lakehouse"` for open-format ML and RAG workloads, and raises on anything unknown.

</div>
