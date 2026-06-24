# The Diagnostic Queries

Each defect leaves a SQL-queryable trace. Finding it is the diagnostic skill every prior module pointed toward.

## The Three Defects, Read As Symptoms

The broken pipeline ships three faults, and you are never told their names. You get symptoms: stale answers, a lineage chain that stops short, a gate that should scream but stays quiet. Six queries turn those symptoms into findings. The grader holds them to a fixed bar, verbatim from the reference suite:

```
* diagnose.py exposes >= 6 find_* functions, each returning a non-None
    finding when run against the *broken* artifacts, and None against the
    *fixed* artifacts.
```

Each `find_*` function reads one table, asks one question, returns one finding or `None`. None of them read source code. They read the artifacts the code produced.

## Defect One: The Future-Dated Batch

The pipeline hardcodes `batch_now_ts` to a date in 2099. Every freshness check measures against that anchor and reports nothing real. Two queries catch it.

### Query One: Read The Batch Timestamp

You select the `batch_now_ts` value from the corpus store. A finding looks like a timestamp decades ahead of the wall clock. Why it traces to a defect: no real batch runs in 2099. The value is a literal, not a call to `datetime.now()`. This is the failure Module 2 warned you about when it defined the freshness SLO. A gate measured against the wrong "now" measures nothing.

### Query Two: Read The Freshness Breach Count

You count rows in the freshness verdict table where the verdict is a breach. A finding looks like a count frozen at zero, or pinned at full, regardless of how stale the source actually is. Why it traces to a defect: a breach count that never moves means the comparison anchor is fixed. The hardcoded timestamp locks the verdict in place.

## Defect Two: The Missing Verdict Edge

`capture_lineage` skips `record_verdict`, so the lineage chain renders incomplete. Two queries catch it.

### Query Three: Walk The Lineage Chain

This is the Module 1 lineage walk, now used as a diagnostic. You start at a derived document and follow edges back to source. A finding looks like a chain that terminates at the derivation step and never reaches a verdict node. Why it traces to a defect: a complete chain must include the verdict that admitted the document. A chain with no verdict edge cannot explain why the document passed the gate.

### Query Four: Count Edge Types

You group edges by kind in the Module 6 lineage store and tally. A finding looks like a `record_verdict` count of zero. Why it traces to a defect: if no verdict edge exists, the function that writes it never ran. The zero is the proof.

## Defect Three: The Quiet Gate

`freshness_gate` ships with `retries=2` instead of `retries=0`, so it swallows failures and retries instead of halting. Two queries catch it.

### Query Five: Read The Retry Configuration

You read the `retries` field for the freshness gate from its metadata or configuration table. A finding looks like a value greater than zero. Why it traces to a defect: a freshness gate is a hard stop. Module 2 set retries to zero so a breach halts the batch. A nonzero retry count converts a hard stop into a soft warning.

### Query Six: Read The Gate Execution Log

You scan the gate execution table for retry rows after a breach. A finding looks like retry attempts that should not exist. Why it traces to a defect: if the gate retried, it ran more than once on the same batch. A gate that retries on a freshness breach is a gate that tolerates staleness.

## What The Six Queries Share

Every query follows the same shape: pick one table, ask one question, return one finding or nothing. The grader applies its six criteria, and the contract is plain, verbatim from its own header:

```
Six criteria, each worth one point.
```

The pipeline lied in its unit tests. The artifacts do not lie. The queries read the artifacts.

## Core Concepts

1. A defect leaves its trace in the data it produces, not in the code that produced it.
2. A freshness gate measured against a hardcoded timestamp reports nothing useful about real staleness.
3. A lineage chain missing its verdict edge cannot explain why a document was admitted.
4. A gate configured to retry converts a hard failure into a soft warning the batch survives.

<div class="claude-handoff" data-exercise="exercises/module8/the-diagnostic-queries/">
**Build It in Claude Code** · Exercise · exercises/module8/the-diagnostic-queries/
</div>

The Production AI Engineer who trusts artifacts over code finds the bug before the regulator does.