# Exercise: The Exam Setup

## Goal

Run the broken pipeline, read its output, and write down the three symptoms before you
name a single defect.

## Why

A production incident hands you symptoms, not a defect list. The discipline that separates
a fast fix from a slow one is resisting the urge to source-dive: look at what the pipeline
produced first.

## What You Are Building

A short incident note: the three observable symptoms (a source stale right after a load, a
lineage chain that stops short, a stale corpus that shipped) and which artifact each shows up in.

## Steps

1. Run `python broken_pipeline.py`. Note that it reports success.

2. Open the resulting `outputs/broken.db` (or run it in-process) and look at three things:
   the freshness result, the `eval_verdicts` table, and whether the gate blocked.

3. For each symptom, write one sentence: what you observed, and which table or result field
   shows it.

4. Do NOT yet open the source to find the defect. The next exercise turns these symptoms
   into queries.
