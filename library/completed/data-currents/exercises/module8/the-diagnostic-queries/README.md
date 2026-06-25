# Exercise: The Diagnostic Queries

## Goal

Write `diagnose.py`: six checks (`q1` through `q6`) that turn the three symptoms into
findings, reading the artifacts the pipeline produced.

## Why

A defect leaves its trace in the data, not the code. Writing the checks forces each symptom
into a precise, falsifiable question, which is the diagnostic skill the whole book pointed toward.

## What You Are Building

A `diagnose(db_path, result)` that runs six checks, each returning a finding dict with a
`found` flag that is `True` on a broken run and `False` on a fixed one.

## Steps

1. Two checks for the future-dated clock: `q1` reads the "now" the freshness check used and
   flags a far-future value; `q2` confirms the source reads stale despite a recent load.

2. Two checks for the missing verdict: `q3` left-joins `answers` to `eval_verdicts` and flags
   answers with no verdict; `q4` walks the full chain and flags one that never reaches a verdict.

3. One check for the quiet gate: `q5` flags the case where the source is stale but the gate
   reported `blocked=False`.

4. A rollup: `q6` counts how many defects are present.

5. Run all six against a broken run (three light up) and a fixed run (all dark). A check that
   fires on both is a tautology; fix it.
