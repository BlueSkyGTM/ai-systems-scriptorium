# Exercise: The DAG: Tasks and Dependencies

**Goal**: Seed `module3-orchestration/` and write `pipeline_flow.py`, a Prefect flow that wires four tasks (extract, ingest, transform, freshness_gate) into a DAG by result-passing, where the ingest task calls the M2 loader.

**Why**: A pipeline whose order lives only in your head is not a system; a DAG makes the dependency order a contract the scheduler enforces.

---

## Steps

This exercise seeds `module3-orchestration/`. Start there.

**1. Create the project layout.**

```
module3-orchestration/
├── pipeline_flow.py   # the flow and its four tasks
└── smoke.py           # the acceptance gate
```

**2. Copy the M2 loader into the project.**

Copy `module2-ingestion/ingest.py` and `module2-ingestion/freshness_check.py` (if it exists) into `module3-orchestration/`. Do not rewrite them. You are reusing M2 work, not rebuilding it.

**3. Install Prefect.**

```
pip install prefect
```

Prefect runs an ephemeral local server; no cloud account or separate server process is needed. The flow runs fully offline.

**4. Write `pipeline_flow.py`.**

Declare four `@task` functions and one `@flow`:

- `extract(run_date, corpus_csv) -> str`: locates or copies the corpus CSV for the given run date and returns `csv_path`.
- `ingest(csv_path, db_path) -> dict`: calls `run_ingest(csv_path=csv_path, db_path=db_path)` from the M2 loader and returns the load summary dict.
- `transform(ingest_summary, db_path) -> str`: reads `ingest_summary["new_versions"]`; if it is greater than zero, runs any post-load transform (a `SELECT COUNT(*)` query is enough for now) and returns a status string.
- `freshness_gate(db_path) -> dict`: calls the M2 freshness check and returns its results dict.

Wire them in a `@flow` by passing each task's return into the next:

```python
@flow(name="corpus-pipeline")
def pipeline_flow(run_date, corpus_csv, db_path):
    csv_path          = extract(run_date=run_date, corpus_csv=corpus_csv)
    ingest_summary    = ingest(csv_path=csv_path, db_path=db_path)
    transform_status  = transform(ingest_summary=ingest_summary, db_path=db_path)
    freshness_results = freshness_gate(db_path=db_path)
    return {"ingest_summary": ingest_summary, "freshness_results": freshness_results}
```

At the bottom of the file, add an `if __name__ == "__main__":` block that calls `pipeline_flow` with a test `run_date`, the corpus CSV path, and a local `db_path`.

**5. Write `smoke.py`.**

The gate runs two checks and exits non-zero if either fails:

- **Dependency order**: capture the order tasks actually ran by appending to a `call_order` list inside each task (or by reading Prefect's flow run state). Assert that `extract` completed before `ingest`, `ingest` before `transform`, and `transform` before `freshness_gate`.
- **Ingest summary present**: assert the flow's return value contains `"ingest_summary"` with a `"new_versions"` key and the value is a non-negative integer.

Run it:

```
python smoke.py
```

It should exit 0 and print a short pass summary.

---

## Done When

- `python pipeline_flow.py` runs the flow offline (no Prefect server) without error and lands the M2 gold tables in the local database.
- The four tasks execute in topological order: extract, then ingest, then transform, then freshness_gate.
- `python smoke.py` exits 0: dependency order is asserted, the returned ingest summary contains `new_versions`.
- The M2 `ingest.py` is reused, not rewritten.

---

## Stretch

Print the DAG's task names in topological order before the flow runs. After the flow completes, assert that the printed order contains no cycles by checking that no name appears before a task it depends on. Confirm this with a deliberate bad ordering (swap ingest and transform in the print list) and assert the check catches it.
