# Module 5: Warehouses and Lakehouses

Modules 1 through 4 produced the corpus and moved it: queried, ingested in batch, orchestrated,
streamed. This module is about where it lands and how you read it. The data team gives you two kinds of
place to put it. A warehouse owns its format for fast, governed, structured SQL. A lakehouse keeps the
data in an open format over object storage, readable by any engine without a license. The choice is not
ideology; it is a match between the workload and the surface.

You learn the production tiers (Snowflake, BigQuery, Microsoft Fabric Warehouse on the structured side;
Delta Lake and Apache Iceberg over OneLake on the open side) and you build the part that runs offline:
a real Delta table with versioning and time-travel, and a DuckDB query surface standing in for the
warehouse. The time-travel is the piece that matters most downstream; it is what lets Module 6 resolve
any answer back to the exact corpus version it cited.

## What This Module Covers

**Warehouse vs Lakehouse** is the choice. A warehouse gives you full T-SQL, DML, and governed
dashboards; a lakehouse keeps the corpus in open Delta or Parquet that any engine reads, with a
read-only SQL endpoint. You pick by who needs to read the data and how.

**Open Table Formats: Delta and Iceberg** adds ACID, schema, and time-travel to plain Parquet through a
transaction log. You write a new version, and the old one stays readable. Time-travel is the load-bearing
capability: you can read the table as it existed at version zero.

**The Medallion in OneLake** is the storage organization. OneLake is one logical lake for the whole
tenant; the medallion organizes it into bronze, silver, and gold; and shortcuts reference data in
another location without copying it, which is how you avoid the stale-duplicate sprawl that rots a data
platform.

**The AI Engineer's Access Pattern** closes the module. You read against tiers you do not own:
read-only, and tier-chosen by the workload. It is the same stance as Module 1's telemetry queries, now
at the warehouse and lakehouse tier.

## Who This Is For

You finished Module 4: you can produce the corpus by batch and by stream. Now you decide where it lands
and how your AI system reads it. You choose the tier and write the queries; you do not own the schema or
run the platform.

## The Artifact

You build `module5-warehouse/`: the gold corpus written to a real Delta table with versioning and
time-travel, a DuckDB warehouse-query surface over the same data, and a tier-decision helper that routes
a workload to the warehouse or the lakehouse. The Delta version history is the exact mechanism Module 6's
lineage store uses to answer "what did this answer cite last week."

## Prerequisites

- Module 2 complete (the gold corpus this module lands)
- Python 3.11+ with `deltalake`, `pandas`, `pyarrow`, and `duckdb` (all pip, all offline)
- Comfort with the medallion idea from Module 2 and the content-hash versioning

## Time Estimate

Each lesson runs 60 to 100 minutes including its exercise. The open-table-format lesson is the one to
linger on; time-travel is the concept the rest of the book leans on.
