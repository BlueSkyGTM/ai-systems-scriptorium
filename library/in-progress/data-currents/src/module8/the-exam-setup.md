# The Exam Setup

Retrieval quality dropped overnight. Three defects sit inside the pipeline, and you have until standup.

## The Incident

It is 03:14 on a Tuesday morning. The on-call pager is yours.

A junior analyst filed a ticket at 22:47 last night: the retrieval system that powers the internal compliance Q&A tool has been returning stale answers for the past two batches.

One of those answers was shown to a regulator yesterday afternoon. Legal is aware. You have until standup.

The system is `broken_pipeline.py`, a distilled version of the multi-source corpus pipeline you built in Module 7: ingest, freshness check, lineage capture, freshness gate, over a SQLite corpus store. Someone modified it. The diff was merged with three reviewers, all of whom approved it because the unit tests went green.

The unit tests were wrong.

## Three Defects, One Diff

Three changes degrade the pipeline silently. You are not told their names; you get symptoms.

1. The freshness check measures staleness against a hardcoded `"2099-01-01"` "now". Every source looks ancient, so the check fires even right after a successful load. Freshness against the wrong clock measures nothing.
2. `capture_lineage` never records the eval verdict. The chain from an answer back to the verdict that graded it stops short, so no one can explain why a document was admitted.
3. The freshness gate swallows the breach. It logs a warning and returns instead of raising, so the pipeline reports success on a stale corpus. The gate does not fail loud.

## What You Produce

You receive `broken_pipeline.py`, read-only. You write two files:

- `diagnose.py`: six checks (`q1` through `q6`) that turn the symptoms into findings, reading the data the pipeline emitted, not its source.
- `fix.py`: the corrected pipeline that restores all three contracts.

Then `rubric.py` grades your fix: six criteria, one point each, exit 0 (PASS) or 1 (FAIL). The same grader run against `broken_pipeline.py` exits 1, which is how you know it has teeth.

## Core Concepts

1. A production incident gives you symptoms, not a defect list; the job is turning symptoms into located faults.
2. The three defects each break a contract: freshness against a real clock, a complete lineage chain, and a gate that fails loud.
3. Unit tests can pass while contracts break; the exam grades contract restoration, not test passage.

<div class="claude-handoff" data-exercise="exercises/module8/the-exam-setup/">
**Build It in Claude Code** · Exercise · exercises/module8/the-exam-setup/
</div>

The pager does not hand you a diff at 03:14; it hands you a database full of clues and a deadline.
