# Skill write-up: The Pipeline Artifact

**What this artifact demonstrates** (fill in your own words below)

---

## What the pipeline does

_Describe the business problem: a multi-source ingestion pipeline that keeps an AI retrieval
system fresh. One nightly batch leg, one streaming CDC leg, a versioned lakehouse, automatic
lineage on every indexed document, and a dual freshness gate that halts serving when either
leg falls behind its SLO._

## Skills demonstrated

- **M2 — Batch ingest**: idempotent bronze -> silver -> gold MERGE keyed on content_hash.
  Plug in any CSV; the corpus store never produces duplicate versions.
- **M3 — Orchestration pattern**: Prefect 3.x `@flow` / `@task` with retries, dependency
  order, and an `on_failure` alert hook wired to a module-level ALERTS list.
- **M4 — CDC streaming**: in-process Kafka simulation (Topic, Producer, ConsumerGroup);
  LagMonitor with injectable clock for deterministic SLO testing.
- **M5 — Delta lakehouse**: `write_corpus_v0` / `write_corpus_v1` with time-travel read
  (`read_version`) to prove the pre-stream snapshot is preserved.
- **M6 — Lineage capture**: `LineageCapture` wraps every indexed chunk; `trace_answer_to_sources`
  walks the full chain; `impact_of_version` answers "which answers break if I update this doc?"
- **Composition, not reimplementation**: all five prior artifacts are vendored as-is into
  `lib/`; thin adapters (`_corpus_to_dataframe`, `_corpus_chunks`) bridge schema differences
  without touching the vendored code.

## Portfolio talking points

- _Add your own notes here after running the artifact and reading the output._
