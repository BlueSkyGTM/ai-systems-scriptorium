# Module 5 — Warehouses and Lakehouses — Build Plan (self-locked)

Status: **PLAN SELF-LOCKED 2026-06-21** (straight-through mandate; gates self-cleared). M5 is where the
batch (M2/M3) and streaming (M4) legs land: the structured warehouse and the open-format lakehouse, the
medallion in OneLake, and the AI engineer's read access pattern to each.

## The stage in one line

M1–M4 produced and moved the data; M5 is about where it lives and how you read it. Seam: the AI
engineer chooses the tier by access pattern (structured BI vs an ML/RAG corpus that needs an open
format) and reads against schemas the data team owns; the open table format's versioning is what makes
the lineage store in M6 possible.

## Settled decisions

1. **Throughline extends M2.** `module5-warehouse/` takes the M2 gold corpus tables and lands them in an
   **open table format (Delta Lake)** with versioning + time-travel, alongside a DuckDB "warehouse"
   query surface. The reuse is real: M5 stores M2's output; the Delta version history seeds M6's lineage.
2. **Teach Snowflake/BigQuery/OneLake; run Delta + DuckDB offline.** Cloud warehouses do not run
   offline, so the lessons teach Snowflake/BigQuery (the structured surface) and Microsoft Fabric
   OneLake + Delta/Iceberg (the open lakehouse) grounded in MS-Learn, while the artifact runs the
   real **`deltalake`** package (delta-rs, pip, local file-based, offline) for the lakehouse side and
   **DuckDB** as the structured warehouse-query stand-in. The artifact-engineer confirms deltalake
   offline write/read/**time-travel**; FALLBACK to a simulated transaction-log table format if it is
   not cleanly offline.
3. **Time-travel is the load-bearing concept.** An open table format adds ACID + versioning +
   time-travel to plain Parquet via a transaction log; querying an old version is exactly the
   capability M6's lineage store depends on. M5 makes it concrete.
4. **The access pattern is read-only and tier-chosen.** The AI engineer reads against a tier they do
   not own; the artifact ships a tier-decision helper (structured BI -> warehouse; open-format
   ML/RAG corpus -> lakehouse) and a read-only access demonstration.

## Proposed M5 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind |
|---|---------------|----------|------|
| 0 | `00-overview` | Where the data lands: warehouse vs lakehouse, open table formats, OneLake, and the read access pattern. | concept |
| 1 | `warehouse-vs-lakehouse` | A warehouse owns its format for fast structured SQL; a lakehouse keeps data in an open format over object storage; you choose by who needs to read it and how. | concept/build |
| 2 | `open-table-formats-delta-and-iceberg` | An open table format (Delta, Iceberg) adds ACID, schema, and time-travel to Parquet via a transaction log; you can query an old version. | build |
| 3 | `the-medallion-in-onelake` | Microsoft Fabric OneLake organizes the lakehouse as one logical store; the medallion (bronze/silver/gold) and shortcuts let you reference data without copying it. | concept/build |
| 4 | `the-ai-engineers-access-pattern` | Read-only, tier-chosen: pick the warehouse for structured BI and the open-format lakehouse for an ML/RAG corpus, and read against a schema the data team owns. Closes the module. | build |

## The artifact + oracle (locked first)

`module5-warehouse/`: writes the M2 gold corpus as a **Delta** table (versioned), demonstrates
**time-travel** (read version N), exposes a DuckDB warehouse-query view over the same data, and a
`choose_tier(access_pattern)` helper. Oracle (`smoke.py` + `pytest`, offline): a Delta write creates
version 0; a second write (an updated row) creates version 1; time-travel reads version 0 and returns
the OLD snapshot while the latest read returns the new; the DuckDB warehouse query over the gold data
returns the expected aggregate; `choose_tier` recommends warehouse for a structured-BI pattern and
lakehouse for an open-format ML/RAG pattern. Negative: a write that violates the table schema is
rejected; a tier helper given an unknown pattern raises rather than guessing.

## Fleet plan

- **Haiku fetch (2):** (a) MS-Learn Fabric Lakehouse + OneLake + medallion + Delta tables + shortcuts +
  (warehouse vs lakehouse / when-to-use), verified URL pack; (b) `deltalake` (delta-rs) offline
  feasibility + minimal API (write, read, version/time-travel, schema) actually run in a temp dir, plus
  Snowflake/BigQuery/Iceberg conceptual grounding from authoritative docs.
- **Sonnet artifact-engineer (1):** builds + tests `module5-warehouse/`; confirms the deltalake-vs-
  fallback path; returns byte-identical code + a green run.
- **Sonnet authors (4):** L1–L4 around the locked code + grounding.
- **Opus conductor:** overview, schema/oracle lock, review, em-dash sweep + `mdbook build`, ship + push.
