# The Exam Setup

Retrieval quality dropped overnight. Three defects sit inside the pipeline you built in Module 7, and you have until standup.

## The Incident

It is 03:14 on a Tuesday morning. The on-call pager is yours.

A junior analyst filed a ticket at 22:47 last night: the retrieval system that powers the internal compliance Q&A tool has been returning stale answers for the past two batches.

One of those answers was shown to a regulator yesterday afternoon. Legal is aware. You have until standup.

The system is the multi-source corpus pipeline you built in Module 7 (`pipeline_flow.py`). Someone modified it. The diff was merged with three reviewers, all of whom approved it because the unit tests went green.

The unit tests were wrong.

## Three Defects, One Diff

Three lines changed in `broken_pipeline.py`. Each degrades the pipeline silently:

1. `batch_now_ts` hardcoded to `"2099-01-01"`: batch freshness breach always fires.
2. `capture