# Querying the Lineage Store

Two questions decide every corpus incident. Which exact source versions did this answer cite? And which
answers break if you change this source version? The lineage store answers both with a query, before
you touch anything.

## Two Directions, One Store

The schema records the chain as it runs: source document to chunk to retrieval to answer to verdict.
Once the chain is in the store, you can walk it in either direction.

**Backward** starts at an answer and walks toward the source. You have a failed eval verdict. You need
to know which document version, at which content hash, the model read. That is root-cause: not "the
corpus," but the exact row in `source_documents` that seeded the chunk the retriever ranked first.

**Forward** starts at a source version and walks toward answers. You are about to update a document.
Before you do, you want to know which answers cited a chunk from it. That is impact analysis: the
list of answers you will need to re-evaluate after the change lands.

Both directions are joins, not reconstructions. The capture wrapper wrote every link as the pipeline
ran, so the store guarantees the chain resolves.

## The Backward Query

`trace_answer_to_sources` walks from an answer through retrievals, chunks, and source documents to the
content hash, and joins in the eval verdicts so you see the terminal judgment alongside the provenance.

```python
def trace_answer_to_sources(conn, answer_id):
    cur = conn.execute("""
        SELECT a.answer_id, a.query, r.chunk_id, r.rank, r.score AS retrieval_score,
               c.source_doc_id, c.source_doc_version, sd.content_hash,
               ev.criterion, ev.verdict, ev.score AS verdict_score
        FROM answers a
        JOIN retrievals r      ON r.answer_id  = a.answer_id
        JOIN chunks c          ON c.chunk_id   = r.chunk_id
        JOIN source_documents sd ON sd.doc_id = c.source_doc_id AND sd.version_id = c.source_doc_version
        LEFT JOIN eval_verdicts ev ON ev.answer_id = a.answer_id
        WHERE a.answer_id = ?
        ORDER BY r.rank, ev.criterion
    """, (answer_id,))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]
```

The result gives you one row per (chunk, verdict) combination, ordered by retrieval rank. The
`content_hash` column is the anchor: if the same document was re-ingested at a new version after this
answer was produced, the hash still points at the version the model actually read. A `LEFT JOIN` on
`eval_verdicts` means you see the verdict rows alongside the source rows, not in a separate query. For
an unknown `answer_id`, the result is an empty list.

## The Forward Query

`impact_of_version` walks the other direction: from a source document version through its chunks,
through the retrievals that cited them, to the answers that cited those retrievals.

```python
def impact_of_version(conn, doc_id, version_id):
    cur = conn.execute("""
        SELECT DISTINCT a.answer_id, a.query, a.answer_text, c.chunk_id
        FROM source_documents sd
        JOIN chunks c     ON c.source_doc_id = sd.doc_id AND c.source_doc_version = sd.version_id
        JOIN retrievals r ON r.chunk_id      = c.chunk_id
        JOIN answers a    ON a.answer_id      = r.answer_id
        WHERE sd.doc_id = ? AND sd.version_id = ?
        ORDER BY a.answer_id
    """, (doc_id, version_id))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]
```

Call this before you update the document. The list it returns is the re-evaluation queue: every answer
that now needs a fresh eval run. `DISTINCT` collapses the case where an answer cited multiple chunks
from the same version. For a version no answer ever cited, the result is an empty list.

## The Regression Trace

Combine the two directions and you have a regression trace. An answer surfaces a `fail` verdict. You
run `trace_answer_to_sources` and read the `content_hash`. You compare that hash to the current value
for that document version. They differ. The source changed after this answer was produced, and the
original hash proves it. That is the explanation the on-call engineer needs: not a guess about what
changed, but the exact version the model cited when the verdict was recorded.

M1's CTE query did this reconstruction by hand, from tables that happened to have the right keys. Here
the lineage is a property the pipeline wrote down as it ran, so the trace is a read, not a derivation.

## Gap Detection

A chain is only useful if it is complete. An answer missing a retrieval or a verdict is a silent
failure: the store has the answer row, but the backward walk dead-ends and the forward walk is invisible.

```python
def find_lineage_gaps(conn):
    """For every answer, report missing links: no_retrieval, no_verdict, or unresolved_chunks."""
    # returns a list of LineageGap(answer_id, missing_links=[...]); [] when all chains are complete
```

`find_lineage_gaps` scans every answer and flags three conditions: no retrieval row, no verdict row,
and any retrieved chunk that does not resolve to a `source_documents` row. An incomplete chain is
flagged here, not silently served. The on-call engineer sees a `LineageGap` with the specific missing
links, not an empty trace that looks like a valid result.

## Core Concepts

- Backward lineage (`trace_answer_to_sources`) walks from an answer to the exact source document
  version and content hash it cited, plus the eval verdict: the root-cause read for any failed answer.
- Forward lineage (`impact_of_version`) walks from a source document version to every answer that cited
  a chunk from it, producing the re-evaluation queue before any corpus change lands.
- The regression trace combines both directions: a failed verdict, traced backward, surfaces the content
  hash the model read; compared against the current hash, it explains the regression without
  guesswork.
- `find_lineage_gaps` flags any answer whose chain is incomplete, so an answer with no retrieval or no
  verdict is quarantined rather than returned as a valid trace.

When backward and forward both answer in one query, the lineage store pays for itself the first time an
incident fires and no one has to ask which version the model read.

<div class="claude-handoff" data-exercise="exercises/module6/querying-the-lineage-store/">

**Build It in Claude Code**: Implement `trace_answer_to_sources` (backward: walk from an answer to the source document versions and content hashes it cited, plus its eval verdicts, ordered by retrieval rank), `impact_of_version` (forward: return every answer that cited a chunk from a given source document version), and `find_lineage_gaps` (flag every answer missing a retrieval row, a verdict row, or an unresolved chunk); then seed a regression scenario where a `fail` verdict traces back to a changed content hash and an answer with no retrieval is flagged by the gap checker.

</div>
