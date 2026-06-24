# The Fix

## A Fix Restores The Contract

Every defect breaks a contract the pipeline owes its consumers. A patch makes the symptom disappear. A fix restores the promise.

The broken pipeline from Module 7 (`pipeline_flow.py`) has three defects. Each one violates a specific guarantee. Your `fix.py` must restore all three. The rubric checks for contract restoration, not test passage.

## Three Broken Contracts

### The Freshness Contract

The pipeline guarantees data is current as of the batch timestamp. The broken pipeline hardcodes `batch_now_ts` to `"2099-01-01"`. Nothing can be stale relative to the year 2099. Every freshness check passes. The contract is dead: the timestamp no longer reflects when the data was processed.

The fix replaces the hardcoded value with the actual processing timestamp. The freshness gate measures real staleness against real time. This matches M7's `pipeline_flow.py`, which reads the timestamp from the environment at batch start.

### The Lineage Contract

The pipeline guarantees every derived document traces back to its source through an unbroken chain. The broken pipeline's `capture_lineage` skips `record_verdict`, the edge that connects a quality verdict to the document it evaluates. The audit trail has a gap. A consumer asking what verdict was reached on a given document hits a dead end.

The fix restores `record_verdict` in the lineage capture. The chain is complete again, matching M7's implementation.

### The Fail-Loud Contract

The freshness gate exists to halt the pipeline on stale data. The broken pipeline sets `retries=2` on the gate. The gate retries twice before failing, masking persistent breaches behind transient retry windows. The contract says stop on breach. Retries add a grace period nobody authorized.

The fix sets `retries=0`. The gate fails on first contact with stale data.

## Why The Unit Tests Lied

The unit tests passed because they tested implementation details, not contracts. A test that checks whether `batch_now_ts` exists passes on `"2099-01-01"`. A test that checks whether `capture_lineage` runs passes even when it skips `record_verdict`. Tests validate behavior. They do not validate intent.

The rubric validates intent. Six criteria, each worth one point:

```python
"""
rubric.py
The Module 8 grader. Six criteria, each worth one point.
"""
```

It runs `fix.py` in a fresh tempdir, executes the pipeline, and inspects the resulting lineage and corpus DBs. It also runs your `diagnose.py` queries against the output. If any diagnostic query returns a non-None finding, the rubric fails.

## Your Fix Against The Original

Your `fix.py` is not a new pipeline. It is M7's `pipeline_flow.py` with three contracts restored. Every other line should match the M7 reference.

Three changes, three contracts:

1. `batch_now_ts` reads the real timestamp from the processing environment.
2. `capture_lineage` includes `record_verdict` edges.
3. `freshness_gate` runs with `retries=0`.

If you find yourself rewriting pipeline logic, you are patching. Go back to the diff.

The negative case proves the rubric has teeth. The test suite pins both outcomes:

```python
# From tests/test_exam.py
BROKEN_PIPELINE = EXAM_DIR / "broken_pipeline.py"
FIX = EXAM_DIR / "fix.py"
RUBRIC = EXAM_DIR / "rubric.py"
SMOKE = EXAM_DIR / "smoke.py"
```

Run the rubric against the broken pipeline:

```bash
python rubric.py --fix ./broken_pipeline.py
```

It exits `1`. The broken pipeline fails because it breaks contracts, regardless of what unit tests report.

Run the rubric against your fix:

```bash
python rubric.py
```

It exits `0` when `fix.py` restores all three contracts.

## Core Concepts

1. A fix restores a broken contract. A patch silences the alarm without repairing the system.
2. A hardcoded `batch_now_ts` breaks the freshness contract by creating a fake reference point that makes real staleness invisible.
3. A skipped `record_verdict` edge breaks the lineage contract by leaving a gap in the provenance chain that consumers cannot traverse.
4. A retry-configured freshness gate breaks the fail-loud contract by masking persistent breaches behind transient retry windows.

<div class="claude-handoff" data-exercise="exercises/module8/the-fix/">
**Build It in Claude Code** · Exercise · exercises/module8/the-fix/
</div>

Your reputation in production is built on the contracts you restore at 3 AM, not the tests you green at standup.