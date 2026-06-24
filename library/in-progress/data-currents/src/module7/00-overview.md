# Module 7: The Pipeline Artifact

The retrieval system needs both batch and stream fresh, every answer traceable. This module proves the five prior modules compose into one run.

Production AI systems fail when you rebuild working components. This capstone satisfies the Part 3 contract: portfolio artifacts must reuse prior work off disk, not restate it. You wire the batch ingestion from [M2](../module2/the-incremental-merge.md), the streaming engine from [M4](../module4/change-data-capture.md), the lakehouse formats from [M5](../module5/open-table-formats-delta-and-iceberg.md), and the lineage capture from [M6](../module6/capturing-lineage-automatically.md).

```python
# Vendored M2 — batch ingest + freshness
from lib.m2_ingest import (
    run_ingest,
    bootstrap_db as m2_bootstrap_db,
)
from lib.m2_freshness_check import check_freshness

# Vendored M4 — streaming / CDC
from lib.m4_kafka_sim import Topic, ConsumerGroup
from lib.m4_cdc_pipeline import cdc_source, apply_event, LagMonitor

# Vendored M5 — Delta lakehouse
import pandas as pd
from lib.m5_lakehouse import write_corpus_v0, write_corpus_v1, read_version, get_version_num

# Vendored M6 — lineage
from lib.m6_schema import init_schema
from lib.m6_lineage import LineageCapture, trace_answer_to_sources, impact_of_version
```

## What This Module Covers

The Architecture establishes the Prefect flow structure mapping dependencies between batch and stream paths.

Wiring the Legs connects the SQLite batch target and the Kafka-simulated stream into a unified Delta Lake.

The Freshness Lineage Proof executes the 28-assertion smoke oracle validating SLO thresholds and source-to-verdict traces.

The Orchestrated Run triggers the complete pipeline locally and verifies artifact generation.

## The Diagram

```text
batch_ingest   -> stream_apply -> land_lakehouse
                               -> capture_lineage
all of the above               -> freshness_gate
```

## The Artifact

You build `module7-pipeline/`. This directory contains a Prefect flow composing five vendored modules, a 28-assertion smoke oracle, and a dual freshness gate. Reuse is real here. You import modules, never restate them.

## Who This Is For

You finished M2 through M6. Now you compose them.

## Prerequisites

* Module 1 through Module 6
* Python 3.11+
* Prefect 3.x
* deltalake
* pandas

## Time Estimate

Plan 60 to 90 minutes per lesson, including the exercise.

## Core Concepts

The capstone pipeline orchestrates five existing modules by importing them off disk.
The dependency DAG routes batch and stream outputs through a unified lakehouse landing step.
A dual freshness gate blocks the pipeline if batch or streaming SLOs fail.

For a Production AI Engineer, composing existing artifacts into a single orchestrator defines the boundary between a notebook experiment and a production system.

<div class="claude-handoff" data-exercise="exercises/module7/00-overview/">
**Inspect It in Claude Code** · Exercise · exercises/module7/00-overview/
</div>