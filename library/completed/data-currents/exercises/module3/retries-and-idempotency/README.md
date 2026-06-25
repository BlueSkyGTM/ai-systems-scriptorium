# Exercise: Retries and Idempotency

**Goal**: Add `retries=2, retry_delay_seconds=0.1` to the `extract` and `ingest` tasks in
`module3-orchestration/`, then write tests that prove the retry heals a transient failure and that a
retried ingest adds zero new `source_document` versions.

**Why**: Retries handle transient failures without human intervention; the `ingest` task can carry
them safely only because the `merge_gold` MERGE underneath is idempotent on `(doc_id, content_hash)`.

---

## Steps

This exercise extends `module3-orchestration/`. Find the folder, read the current state of the DAG,
and verify the existing tests pass before adding anything.

**1. Locate the task decorators.**

Open `module3-orchestration/flow.py` (or wherever the prior lesson landed `extract` and `ingest`).
Find the `@task` decorator on each. Add `retries=2, retry_delay_seconds=0.1` to both:

```python
@task(name="extract", retries=2, retry_delay_seconds=0.1)
def extract(run_date, corpus_csv): ...

@task(name="ingest", retries=2, retry_delay_seconds=0.1)
def ingest(csv_path, db_path): ...
```

These are the only changes to the production code. Do not touch the DAG wiring.

**2. Write the retry-recovery test.**

In `module3-orchestration/tests/test_retries.py`, write a test that:

- Monkeypatches `run_ingest` (or the ingest task's inner call) to raise `RuntimeError` on the first
  call and return normally on the second.
- Runs the flow via Prefect's test runner (or calls the task directly in a test context).
- Asserts the flow completes without raising.
- Asserts `run_ingest` was called exactly twice (once failed, once succeeded).

Prefect tasks under `retries=2` retry on any exception by default; you do not need extra
configuration. A `unittest.mock.patch` with a `side_effect` list achieves the call sequence:

```python
side_effect=[RuntimeError("transient"), DEFAULT]
```

**3. Write the idempotency assertion.**

In the same test file, add a second test (or extend the first) that:

- Runs the ingest against the synthetic corpus once.
- Runs it a second time on the same unchanged corpus.
- Queries `source_documents` and asserts the count after the second run equals the count after the
  first: zero new versions were added.

Use the `merge_gold` return value to assert directly (it returns `0` on a no-change run). This
assertion is the proof that `retries=2` on the `ingest` task is safe: a retried ingest cannot
double-load.

**4. Run the full test suite.**

```
python -m pytest module3-orchestration/tests/
```

All prior tests must still pass. The two new tests must pass. No network calls; the test suite is
offline.

---

## Done When

- `python -m pytest module3-orchestration/tests/` exits 0.
- The retry-recovery test passes: the flow completes after one simulated failure, and `run_ingest`
  was called exactly twice.
- The idempotency assertion passes: a second ingest run on unchanged corpus returns `0` new
  `source_document` versions.
- No external services or network calls; stdlib `sqlite3` and `pytest` only.

---

## Stretch

Add a third test that removes idempotency: replace the `merge_gold` MERGE with a naive `INSERT`
(no existence check), run the ingest twice, and assert the `source_documents` count doubled. This
makes the pairing concrete: without idempotency, `retries=2` turns a transient failure into a
data-quality bug. Revert the naive insert after the test; it is for demonstration only.
