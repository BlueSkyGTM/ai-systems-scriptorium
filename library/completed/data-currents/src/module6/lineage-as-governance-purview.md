# Lineage as a Governance Surface: Microsoft Purview

A regulator reviewing an AI system does not accept "the model read the corpus." It asks which exact version of which document, which chunks were retrieved, and who verified the answer met the quality threshold. At enterprise scale, the system that answers those questions is not a local SQLite store: it is a governed catalog that spans every data system in the organization.

That catalog is Microsoft Purview Unified Catalog, and lineage is one of its core surfaces.

## What Microsoft Purview Unified Catalog Is

Microsoft Purview Unified Catalog is Microsoft's governance catalog for discovering, governing, and tracking data assets across systems. It spans on-premises stores, Azure data services, and third-party sources. Within it, data lineage tracks data from its source through transformations to its destination, so a reviewer can follow the path a record traveled without reconstructing it from logs. [MS-Learn unified catalog: https://learn.microsoft.com/purview/unified-catalog]

The lineage view in Purview is not a report you author: it is captured automatically from pipeline execution. Azure Data Factory and Synapse pipelines report lineage to Purview as they run, writing the source-to-destination edges in real time. [MS-Learn lineage from Azure Data Factory: https://learn.microsoft.com/purview/data-map-lineage-azure-data-factory]

That automatic capture is exactly what `LineageCapture` does for your local RAG store. The principle is the same; the scope is the enterprise.

## Column-Level Lineage

Purview supports lineage at column granularity: it can trace not just that data moved from table A to table B, but that a specific column in A contributed to a specific column in B. This matters when a downstream consumer needs to know which source field produced the value that failed an audit. Support varies by source system; not every connector reports at column level, but where it does, the trace is precise. [MS-Learn column-level lineage: https://learn.microsoft.com/purview/data-gov-classic-lineage-user-guide]

The local store has an analogue: `content_hash` in `embeddings` ties a chunk's encoding to the exact text at encode time. If a document version changes and the chunk text changes, the `content_hash` changes. That is a column-level signal: the field that changed, and when.

## Impact Analysis

Lineage's most direct operational use is impact analysis: given an asset that is about to change, which downstream consumers are affected? Purview surfaces this through its lineage graph. You navigate to a source asset, scan the forward lineage, and see every table, report, or service that reads from it. [MS-Learn data lineage overview: https://learn.microsoft.com/purview/data-gov-classic-lineage]

`impact_of_version` runs the same motion against the local store. You pass a `doc_id` and `version_id`, and it returns every answer that cited a chunk from that version. Before you reload a corpus version, you run impact analysis; you know exactly which answers will need re-evaluation.

`find_lineage_gaps` is the completeness check governance requires: it scans every answer and reports which are missing a retrieval, a verdict, or a source resolution. An incomplete chain is a governance failure, not just a data quality one.

## The Honest Boundary

Purview does not yet offer lineage features specific to AI inference or RAG pipelines. There is no built-in Purview surface that traces the path from a user query through retrieval through LLM generation to an eval verdict. Purview covers traditional data lineage and ML training-data lineage; RAG-step lineage is not a product feature.

The local `module6-lineage` store is the AI-pipeline-specific layer that Purview does not provide. In an enterprise deployment, you would surface that store's data into Purview as a custom lineage source: your store captures the RAG chain; Purview holds the enterprise view of what systems contributed to it. The two complement each other rather than replace each other. Do not claim Purview handles the answer-to-chunk-to-verdict path out of the box: it does not.

## Core Concepts

- Microsoft Purview Unified Catalog is the enterprise governance surface for discovering, governing, and tracking data assets across systems; data lineage within it traces data from source through transformations to destination.
- Purview captures lineage automatically from Azure Data Factory and Synapse pipelines; support for column-level lineage varies by source but traces which source fields contributed to which destination fields where available.
- Impact analysis in Purview answers "which downstream assets are affected if this source changes?"; `impact_of_version` runs the same motion against the local RAG lineage store.
- Purview does not yet provide lineage for AI inference or RAG steps; the local lineage store is the AI-pipeline-specific layer, and in production it would report into Purview as a custom lineage source.

The store you built in this module is the layer Purview cannot yet see. Knowing where enterprise tooling ends and custom capture begins is how a data engineer decides what to build versus what to buy.

Module 7 composes the whole pipeline: batch and streaming legs through the lakehouse, lineage captured on every indexed document, the governance surface connected at the end, all in one runnable portfolio artifact.

<div class="claude-handoff" data-exercise="exercises/module6/lineage-as-governance-purview/">

**Build It in Claude Code**: Write a `governance_report(conn, doc_id, version_id)` function in `module6-lineage/` that calls `impact_of_version` to return the set of answers affected by the given source version and calls `find_lineage_gaps` to return any incomplete chains across all answers in the store; finalize `smoke.py` and tests to assert that the report names at least one affected answer when a known version is queried and that it flags a gap when an answer is missing its verdict; then write a `PURVIEW.md` note (grounded only in the MS-Learn URLs provided in the lesson) that maps `impact_of_version` to Purview impact analysis, `content_hash` column tracking to Purview column-level lineage, and the full local store to Purview Unified Catalog as a custom lineage source, and states plainly that RAG-step lineage (query through retrieval through generation through eval verdict) is not a built-in Purview feature.

</div>
