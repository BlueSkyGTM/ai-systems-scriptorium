# The Fix

## A Fix Restores The Contract

Every defect breaks a contract the pipeline owes its consumers. A patch makes the symptom disappear. A fix restores the promise.

The broken pipeline has three defects. Each one violates a specific guarantee. Your `fix.py` must restore all three. The rubric checks for contract restoration, not test passage.

## Three Broken Contracts

### The Freshness Contract

The pipeline guarantees data is current as of a real processing time. The broken pipeline measures staleness against a hardcoded `"2099-01-01"` "now". Nothing can be stale relative to the year 2099, so every freshness check passes. The contract is dead: the timestamp no longer reflects when the data was processed.

The fix uses the real `now_ts` passed into the run. The freshness gate measures real staleness against real time.

```python
def freshness_check(db_path, now_ts):
    now = now_ts  # FIX 1: use the real 'now', not a hardcoded date
    loaded = store.last_load(db_path)
    age = store.hours_between(loaded, now)
    return {"is_stale": age > store.MAX_AGE_HOURS, ...}
```

### The Lineage Contract

The pipeline guarantees every answer traces back to its source through an unbroken chain, ending in the verdict that admitted it. The broken `capture_lineage` skips the verdict insert. The audit trail has a gap: a consumer asking what verdict was reached on a given answer hits a dead end.

The fix records the verdict, completing the chain:

```python
# FIX 2: record the verdict so the answer -> verdict chain is complete.
conn.execute("INSERT INTO eval_verdicts VALUES (?, ?, ?)", (answer_id, "groundedness", "pass"))
```

### The Fail-Loud Contract

The freshness gate exists to halt the pipeline on stale data. The broken gate swallows the breach: it logs a warning and returns instead of raising, so the run reports success on a stale corpus. The contract says stop on breach; the broken gate downgrades it to a log line.

The fix raises, so the gate fails loud:

```python
def freshness_gate(fresh):
    if fresh["is_stale"]:
        raise FreshnessBreach(...)  # FIX 3: a stale corpus must stop the pipeline
    return {"blocked": False}
```

## Why The Unit Tests Lied

The unit tests passed because they tested whether functions ran, not whether contracts held. A test that checks `capture_lineage` runs passes even when it skips the verdict. Tests validate behaviour; they do not validate intent.

The rubric validates intent. It runs your `fix.py` from scratch, runs `diagnose.py` against the result, and checks that a stale corpus actually raises:

```python
The Module 8 grader. Six criteria, each worth one point.
```

If any diagnostic check still reports `found=True`, or the stale run fails to raise, the rubric fails.

## Your Fix Against The Broken Pipeline

Your `fix.py` is not a new pipeline. It is the broken pipeline with three contracts restored: the real clock, the recorded verdict, the raising gate. If you find yourself rewriting pipeline logic, you are patching. Go back to the three defects.

The negative case proves the rubric has teeth. Run the grader against the broken pipeline:

```bash
python rubric.py --pipeline broken_pipeline
```

It exits `1`. The broken pipeline fails because it breaks contracts, regardless of what its unit tests reported.

Run the grader against your fix:

```bash
python rubric.py
```

It exits `0` when `fix.py` restores all three contracts.

## Core Concepts

1. A fix restores a broken contract. A patch silences the alarm without repairing the system.
2. A hardcoded "now" breaks the freshness contract by creating a fake reference point that makes real staleness invisible.
3. A skipped verdict breaks the lineage contract by leaving a gap consumers cannot traverse.
4. A gate that swallows a breach breaks the fail-loud contract by downgrading a hard stop to a log line.

<div class="claude-handoff" data-exercise="exercises/module8/the-fix/">
**Build It in Claude Code** · Exercise · exercises/module8/the-fix/
</div>

Your reputation in production is built on the contracts you restore at 3 AM, not the tests you green at standup.
