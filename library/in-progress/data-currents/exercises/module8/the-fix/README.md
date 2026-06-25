# Exercise: The Fix

## Goal

Write `fix.py`: the broken pipeline with three contracts restored, not a rewrite.

## Why

A patch silences a symptom; a fix restores the promise the defect broke. Making exactly
three surgical edits is how you prove you understood the defects rather than papering over them.

## What You Are Building

A `run(db_path, loaded_at, now_ts)` that uses the real clock, records the verdict, and raises
on a stale corpus.

## Steps

1. **Freshness contract:** in `freshness_check`, use the real `now_ts` instead of the
   hardcoded `"2099-01-01"`.

2. **Lineage contract:** in `capture_lineage`, insert the `eval_verdicts` row so the
   answer-to-verdict chain is complete.

3. **Fail-loud contract:** in `freshness_gate`, raise `FreshnessBreach` when the source is
   stale instead of logging and returning.

4. Wire `run()` so a stale corpus propagates the breach (a `raise_on_breach` flag is fine).

5. Confirm: `python diagnose.py` against a fixed run shows all six checks dark, and a stale
   run raises. If you are rewriting pipeline logic, go back to the three defects.
