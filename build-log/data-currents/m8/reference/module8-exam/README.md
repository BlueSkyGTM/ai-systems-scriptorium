# Module 8 — The Diagnostic Exam

> Capstone for *Data Currents*. You have one broken pipeline, one degraded
> retriever, and a rubric that refuses to lie. Pass it, or explain why you
> can't.

---

## 1. Business scenario

It is 03:14 on a Tuesday morning. The on-call pager is yours.

A junior analyst filed a ticket at 22:47 last night: the retrieval system
that powers the internal compliance Q&A tool has been returning *stale*
answers for the past two batches. One of those answers was shown to a
regulator yesterday afternoon. Legal is aware. You have until standup.

The system in question is the multi-source corpus pipeline you built in
**Module 7** (`pipeline_flow.py`). Someone — possibly you, possibly a
well-meaning PR from the data platform team — has modified it. The diff
was merged with three reviewers, all of whom approved it because the unit
tests went green. The unit tests were wrong.

Your job, in order:

1. **Diagnose** — find every defect, using only the artifacts the pipeline
   produces (the SQLite lineage DB and the corpus DB) plus standard SQL.
2. **Repair** — produce a corrected `fix.py` that passes the rubric.
3. **Verify** — run `smoke.py` and watch it exit `0`.

You are not given the defects. You are given the symptoms.

---

## 2. What's in the box

```
module8-exam/
├── README.md            ← you are here
├── broken_pipeline.py   ← the M7 pipeline, corrupted (DO NOT EDIT)
├── diagnose.py          ← YOU WRITE THIS (six diagnostic queries)
├── fix.py               ← YOU WRITE THIS (corrected pipeline)
├── rubric.py            ← grades your fix.py by code, not by vibes
├── smoke.py             ← the oracle; exits 0 on full pass
└── lib/                 ← vendored M7 reference library (read-only)
```

You may read every file in this directory. You may not edit
`broken_pipeline.py`, `rubric.py`, `smoke.py`, or anything under `lib/`.

---

## 3. The symptoms

The on-call journal from the analyst contains four clues. They are all
you have to go on at the start.

> **Clue 1 — "Every batch trips the freshness gate."**
> The freshness gate fires on every run, even when the source documents
> are seconds old. The pipeline then retries and *succeeds* on retry. This
> is the opposite of failing loud.

> **Clue 2 — "Lineage stops mid-chain."**
> When the analyst queried the lineage DB to find which document
> influenced a given chunk, the chain terminated at the chunker stage.
> The record-level verdict that a document actually entered the corpus
> was never captured. You cannot audit what you cannot see.

> **Clue 3 — "The `batch_now_ts` is in the future."**
> A grep for the literal `2099` returns a hit in the pipeline source.
> This should be impossible. `batch_now_ts` is supposed to be *now*,
> not the heat death of the universe.

> **Clue 4 — "The retriever was right; the index was wrong."**
> A document that was *re-ingested* after a correction did not update
> the answer the retriever returned, because the pipeline never recorded
> the re-ingestion in lineage. The retriever has no way to know it is
> stale — the pipeline lied to it.

There are **three** defects. They are not independent — fixing one
without the others leaves the system broken in a more confusing way.

---

## 4. Deliverables

### 4.1 `diagnose.py` — six diagnostic queries

Write six functions, each returning a *finding dict*. The finding dict
must conform to the schema in `rubric.py`:

```python
{
    "defect_id": str | None,       # e.g. "D1", "D2", "D3", or None
    "evidence":  str | None,       # one-line human-readable proof
    "query":     str | None,       # the SQL or Python you ran
}
```

A finding of `None` for every field means *no defect of this class was
detected*. (This is how `smoke.py` confirms your fix worked: after
`fix.py` runs, every diagnostic query should return all-`None`.)

The six queries, in the order the rubric expects them:

| #  | Function                | Hunts for                                                |
|----|-------------------------|----------------------------------------------------------|
| Q1 | `find_future_batch_ts`  | A `batch_now_ts` materially in the future.               |
| Q2 | `find_gate_retries`     | A freshness gate configured to retry (retries > 0).      |
| Q3 | `find_lineage_gap`      | A document that entered the corpus but has no            |
|    |                         | `record_verdict` lineage edge.                           |
| Q4 | `find_freshness_breach` | A source document whose `ingested_at` is *after*         |
|    |                         | the configured freshness SLA, given a correct            |
|    |                         | `batch_now_ts`.                                          |
| Q5 | `find_stale_answer`     | A query whose retrieved answer references a document     |
|    |                         | version older than the latest ingested version.          |
| Q6 | `find_orphan_chunks`    | A chunk in the corpus with no lineage ancestor at all.   |

Each query operates **only** on:
- the lineage SQLite DB produced by a run of `broken_pipeline.py`, and/or
- the corpus SQLite DB produced by the same run.

You may use `sqlite3` from the stdlib. You may read the schema by
attaching to the DBs. You may not modify the DBs.

### 4.2 `fix.py` — the corrected pipeline

`fix.py` must be a drop-in replacement for `broken_pipeline.py`: same
entry points, same function signatures, same CLI. It must produce a
lineage DB and a corpus DB that pass all six diagnostic queries (i.e.,
every query returns all-`None`).

There are exactly **three** edits to make. Find them.

### 4.3 `smoke.py` — you do not write this

`smoke.py` does the following, in order:

1. Runs `broken_pipeline.py` against a fresh temp dir.
2. Runs `diagnose.py` against the resulting DBs.
   - **All six queries should return non-None findings** — this is the
     *negative* case that proves your diagnostics actually detect the
     defects.
3. Runs `rubric.py` against `broken_pipeline.py`.
   - It must **fail** (`exit 1`). This proves the rubric is honest.
4. Runs `fix.py` against a fresh temp dir.
5. Runs `diagnose.py` against the resulting DBs.
   - **All six queries should return all-None findings.**
6. Runs `rubric.py` against `fix.py`.
   - It must **pass** (`exit 0`).
7. Exits `0` if and only if all of the above held.

24 assertions minimum. The negative case (`broken_pipeline` fails the
rubric) is one of them — a rubric that passes a broken pipeline is
itself broken.

---

## 5. The rubric (six criteria)

`rubric.py` grades `fix.py` directly by code inspection and by running
it. Each criterion is binary. All six must pass.

| R# | Criterion                                                       |
|----|-----------------------------------------------------------------|
| R1 | `batch_now_ts` is derived from the system clock, not hardcoded. |
| R2 | `capture_lineage` records a `record_verdict` edge per document. |
| R3 | `freshness_gate` is configured with `retries=0`.               |
| R4 | Defect D1 (future timestamp) is detected by `diagnose.py`.      |
| R5 | Defect D2 (lineage gap) is detected by `diagnose.py`.           |
| R6 | Defect D3 (silent retries) is detected by `diagnose.py`.        |

R4–R6 are checked by running `diagnose.py` against the **broken**
pipeline's output and confirming the relevant queries fire. This is the
"your diagnostic actually works" check — a fix that no one can verify
is not a fix.

---

## 6. How to run

```bash
# Step 1: reproduce the breakage
python broken_pipeline.py --output /tmp/m8-broken
# Expect: pipeline "succeeds" but the freshness gate fired and retried.

# Step 2: write your diagnostics, then point them at the broken output
python diagnose.py --lineage /tmp/m8-broken/lineage.db \
                   --corpus   /tmp/m8-broken/corpus.db
# Expect: six findings, three of them non-None.

# Step 3: write your fix, then prove it
python fix.py --output /tmp/m8-fixed
python diagnose.py --lineage /tmp/m8-fixed/lineage.db \
                   --corpus   /tmp/m8-fixed/corpus.db
# Expect: six findings, all None.

# Step 4: the oracle
python smoke.py
echo $?   # must print 0
```

---

## 7. Rules of engagement

- **No editing the test harness.** `rubric.py`, `smoke.py`, `lib/`, and
  `broken_pipeline.py` are read-only. If you find yourself changing them,
  you are solving a different problem.
- **No network.** The pipeline must run on a laptop in airplane mode.
  No HuggingFace, no OpenAI, no `pip install` at runtime.
- **Reproducibility.** Set `random.seed(42)` and (where applicable)
  `torch.manual_seed(42)` at the top of every script you write. The
  rubric will not forgive nondeterminism.
- **Honest diagnostics.** A diagnostic that returns a finding for *every*
  pipeline — broken or fixed — is not a diagnostic, it is a tautology.
  `smoke.py` checks the negative case for this reason.
- **One commit per defect.** When you submit, the grader will diff your
  `fix.py` against `broken_pipeline.py` and expect to see three logical
  changes, not fifteen. Surgical edits are a grading criterion in
  spirit, if not in code.

---

## 8. What success looks like

```
$ python smoke.py
[1/7] running broken_pipeline.py ............... OK (pipeline completed)
[2/7] running diagnose.py against broken ....... 3 findings (expected ≥3)
[3/7] running rubric.py against broken ......... FAIL (expected)
[4/7] running fix.py ........................... OK (pipeline completed)
[5/7] running diagnose.py against fixed ........ 0 findings (expected 0)
[6/7] running rubric.py against fixed .......... PASS
[7/7] all assertions ........................... PASS (24/24)
$ echo $?
0
```

Standup is at 09:30. Good luck.

---

## 9. Hints (use sparingly)

1. The defects cluster around *time*, *provenance*, and *failure mode*.
   One per cluster.
2. `git log` on `broken_pipeline.py` is cheating, but it's also how this
   would actually happen in production. We'll allow it for the hint.
3. If your `find_lineage_gap` returns nothing on the broken pipeline,
   your query is wrong, not the pipeline.
4. The freshness gate is *supposed* to be a circuit breaker. A circuit
   breaker that retries is a wire.
5. When in doubt, read `lib/` from Module 7. The reference
   `pipeline_flow.py` lives there, unbroken, in full.
