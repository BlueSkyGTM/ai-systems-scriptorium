# Module 6: Lineage: From Document to Eval Verdict

Module 1 walked lineage by hand: a query that reconstructed, after the fact, which source-document
version an answer cited. That works once, for one answer, when you already suspect where to look. It
does not scale to a production incident where a hundred answers degraded overnight and you need to know
why, fast. This module builds the automated version: a lineage store that captures the full provenance
chain as the pipeline runs, then answers the two questions every corpus incident asks.

The chain runs from a source-document version through the chunk, the embedding, the retrieval, and the
answer, to the eval verdict that graded it. You record each link as the step that produces it runs, so
the chain is complete by construction, not reconstructed under pressure. Then you query it two ways:
backward, from a failed answer to the exact source version it cited; and forward, from a source version
about to change to the answers it will affect. Module 5's Delta time-travel is what gives those source
versions their content hashes; this module is where they become a queryable graph.

## What This Module Covers

**The Lineage Graph** is the schema: six tables forming the chain, each foreign key an edge. The
load-bearing detail is that chunks anchor to a source-document version, not just a document id, so a
reload creates new chunks and an old answer still traces to the old version. Lineage never blurs across
versions.

**Capturing Lineage Automatically** is the `LineageCapture` wrapper. Each pipeline step calls a record
method before it returns, so the link is written as the work happens. Lineage you reconstruct after an
incident is lineage you might not have; captured lineage is always there when you need it.

**Querying the Lineage Store** is the payoff. The backward query resolves an answer to the exact source
versions and content hashes it cited, plus its verdict. The forward query is impact analysis: which
answers cited a chunk from a version you are about to change. And a gap check flags any chain with a
missing link, so an incomplete answer is quarantined, not served.

**Lineage as Governance: Purview** closes the module. At enterprise scale, lineage is a governance
surface: Microsoft Purview Unified Catalog tracks lineage across systems, supports column-level lineage,
and powers impact analysis. You learn what it does, and you learn the honest boundary: Purview does not
yet track RAG answer-to-verdict lineage, so the store you built is the AI-specific layer it would report
into.

## Who This Is For

You finished Module 5: you have versioned documents in an open table format. Now you make the provenance
from a source version to an eval verdict a first-class, queryable store. This is the chain that turns
"the corpus changed" into "this version of this document changed this answer."

## The Artifact

You build `module6-lineage/`: a SQLite lineage store, a `LineageCapture` wrapper that records each link
automatically, and the two queries plus gap detection. It composes Module 1's lineage shape and Module
5's versioned content hashes. Module 7 puts this store at the end of the full pipeline, writing a lineage
row for every indexed document.

## Prerequisites

- Module 1 (the manual lineage walk) and Module 5 (versioned documents via Delta time-travel)
- Python 3.11+; the lineage store is standard library only (`sqlite3`), fully offline
- Comfort with joins and the content-hash versioning from earlier modules

## Time Estimate

Each lesson runs 60 to 95 minutes including its exercise. The querying lesson is where the module pays
off; the two queries are the ones an interviewer asks you to write.
