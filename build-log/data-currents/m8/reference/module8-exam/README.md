# Module 8: The Diagnostic Exam

> Capstone for *Data Currents*. You have one broken pipeline, one degraded retriever, and a
> rubric that refuses to lie. Pass it, or explain why you can't.

---

## 1. Business Scenario

It is 03:14 on a Tuesday. The on-call pager is yours. A junior analyst filed a ticket: the
retrieval system behind the internal compliance Q&A tool has been returning stale answers
for two batches, and one stale answer reached a regulator yesterday. Legal is aware. You
have until standup.

The system is `broken_pipeline.py`, a distilled version of the Module 7 corpus pipeline
(ingest, freshness check, lineage capture, freshness gate, over SQLite). Someone modified
it; the diff was merged because the unit tests went green. The unit tests were wrong.

Your job, in order:

1. **Diagnose** the defects using only the artifacts the pipeline produces, plus SQL.
2. **Repair** them in a `fix.py` that passes the rubric.
3. **Verify** with `smoke.py` and watch it exit `0`.

You are given symptoms, not defects.

---

## 2. What's in the Box

```
module8-exam/
├── README.md            <- you are here
├── broken_pipeline.py   <- the corrupted pipeline (DO NOT EDIT)
├── diagnose.py          <- six checks q1..q6 that locate the defects
├── fix.py               <- the corrected pipeline
├── rubric.py            <- grades a candidate pipeline by code, not vibes
├── smoke.py             <- the oracle; exits 0 on full pass
├── lib/store.py         <- shared schema + helpers (read-only)
└── tests/test_exam.py   <- pytest suite
```

`broken_pipeline.py`, `rubric.py`, `smoke.py`, and `lib/` are read-only.

---

## 3. The Three Defects

1. **Future-dated clock.** `freshness_check` measures staleness against a hardcoded
   `"2099-01-01"` "now", so every source reads stale even right after a load.
2. **Missing verdict.** `capture_lineage` never records the eval verdict, so the
   answer-to-verdict chain stops short.
3. **Quiet gate.** `freshness_gate` swallows the breach (logs and returns) instead of
   raising, so a stale corpus ships in silence.

The three are not independent: fixing one without the others leaves the system broken in a
more confusing way.

---

## 4. Deliverables

### `diagnose.py` — six checks

Six functions `q1` through `q6`, each returning a finding dict:

```python
{"name": "q1_future_now", "defect": "...", "found": True, "detail": "..."}
```

`found=True` means the defect is present. `diagnose(db_path, result)` runs all six. Against
a broken run, the three defects light up (q1/q2, q3/q4, q5); against a fixed run they go dark.
The checks read the corpus + lineage tables and the run's result; they never read source code.

### `fix.py` — the corrected pipeline

A drop-in `run(db_path, loaded_at, now_ts)` that restores the three contracts: the real
`now_ts`, the recorded verdict, and a gate that raises `FreshnessBreach` on a stale corpus.
Three edits, not fifteen.

### `rubric.py` — the grader (read-only)

Six binary criteria, all must pass:

| R# | Criterion |
|----|-----------|
| 1 | the freshness check uses the real `now`, not a future date |
| 2 | `capture_lineage` records the eval verdict |
| 3 | the gate raises on a stale source (fails loud) |
| 4 | the answer-to-verdict lineage chain is complete |
| 5 | a healthy corpus runs clean |
| 6 | a stale corpus raises rather than shipping in silence |

`python rubric.py` grades `fix.py` and exits 0; `python rubric.py --pipeline broken_pipeline`
exits 1. That negative direction is how you know the grader has teeth.

---

## 5. How to Run

```bash
python broken_pipeline.py              # reproduce the silent breakage
python diagnose.py                     # six checks against a broken run; 3 defects light up
python fix.py                          # the corrected pipeline runs clean
python rubric.py ; echo $?             # grade the fix: 0 = PASS
python rubric.py --pipeline broken_pipeline ; echo $?   # 1 = the broken pipeline fails
python smoke.py                        # the oracle: 19 assertions, exit 0
python -m pytest tests/ -q
```

---

## 6. Rules of Engagement

- **No editing the harness.** `broken_pipeline.py`, `rubric.py`, `smoke.py`, `lib/` are read-only.
- **No network, no HuggingFace, no `pip install` at runtime.** Pure stdlib + sqlite3, CPU, instant.
- **Honest diagnostics.** A check that fires on every pipeline, broken or fixed, is a tautology, not a diagnostic. `smoke.py` checks both directions for exactly this reason.
- **Surgical edits.** `fix.py` is the broken pipeline with three contracts restored, not a rewrite.

Standup is at 09:30. Good luck.
