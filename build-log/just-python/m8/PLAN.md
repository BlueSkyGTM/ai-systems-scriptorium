# Module 8 — Integrated Python Engineering Exam — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared — Ray locked as drafted: all 4 decisions
accepted — 5 lessons, canonical harness + `pipeline.py` shape + six criteria + locked oracle, reuse the M7
oracle as M8's, skill write-up + Haiku fetchers + conductor reference run).** **SHIPPED 2026-06-21
(`GATE-APPROVE-SHIP` cleared).** Eighth and final authoring
stage for Just Python: the **capstone** (the Operate/Exam phase, STANDARDS Part 1 ramp). M1–M7 shipped. M8 turns the blueprint's
eighth module into a finished mdBook chapter + a graded exam harness, under AUTHOR → VERIFY → BUILD/TEST →
SHIP. On ship, **Just Python is complete (8/8)**. Do not author until Ray locks.

## The stage in one line

M6 produced a clean dataset; M7 judged a model on one. M8 is the take-home that **chains both**: the reader
builds `pipeline.py`, which **imports `wrangle.py` (M6) and `eval_engine.py` (M7) off disk** (it does not
rebuild them), runs a raw corpus through wrangle → feeds the cleaned data + a prediction batch through
eval_engine → emits one integrated Markdown report, and a `rubric.py` **grades the produced run by code**
against a six-criterion acceptance rubric. Seam: this is the exam a hiring manager actually runs — does the
whole pipeline compose, validate its data, get the metrics right, and frame the finding?

## Settled decisions (from the blueprint + the contracts)

1. **Capstone shape, not a new build (STANDARDS Part 1 Operate/Exam rung + Part 3).** The exam **reuses the
   composition artifacts**: `pipeline.py` composes M6 + M7 off disk via a tiny `artifact_adapter.py` (the
   `fleet_adapter.py` analog), exactly as Sans Python M8 operates the M7 fleet via `fleet_adapter.py`.
   Rebuilding `wrangle.py` or `eval_engine.py` inside M8 is a misread of the assignment (the STYLE of the
   exam: "compose, do not rebuild").
2. **Graded by code, not opinion (STANDARDS Part 2 Capstone Rubric).** The rubric exists in **two forms that
   must match**: a `rubric.py` checker and the same rubric in the guide prose (`the-rubric-and-grading.md`).
   A `CRITERIA` tuple is the single source of truth for both. **A deliberately deficient run must fail the
   criterion it offends** (the invariant).
3. **Data-domain criteria (drop the fleet ones, keep schema-validation).** STANDARDS says a book keeps the
   capstone criteria that fit its domain. Sans Python's seven were fleet-ops (HITL, audit, budget). Just
   Python's six are data-ops: **RUNS, SCHEMA-VALID, METRICS-CORRECT, COMPOSED, PROBLEM-FRAMED,
   TESTED+VERSIONED** (below).
4. **Deterministic, hand-verifiable oracle that ties M6 + M7 together.** The bundled `sample_corpus.jsonl`
   (12 raw rows) wrangles down to the **10-row M7 sample**, and `sample_predictions.csv` is the **locked M7
   prediction set** — so the integrated report's metrics are the **already-locked M7 oracle** (cat/dog/bird
   below). One oracle proves the whole chain; the smoke gate is deterministic and offline (stdlib + pandas).
5. **Learner-built, conductor-verified (not committed), like M6/M7.** The exercises build `pipeline.py` /
   `artifact_adapter.py` / `rubric.py` / `smoke.py` / `tests/` / the skill write-up. The conductor assembles
   a **reference harness — reference `wrangle.py` + `eval_engine.py` + the M8 files — and runs it green**
   (BUILD/TEST: the run grades PASS, the deficient run grades FAIL), then discards the reference. Nothing
   reference-only is committed.

## The canonical M8 harness (locked here so the four workers build one design)

The exam harness, mirroring the Sans Python M8 file set, scoped to the data domain:

```
exercises/module8/
  artifact_adapter.py   # resolve + import wrangle.py (M6) and eval_engine.py (M7) off disk   (L2)
  pipeline.py           # chain: ingest raw -> wrangle.run -> eval_engine.run -> write report.md (L2)
  rubric.py             # CRITERIA tuple (6) + grade(ExamRun) -> RubricReport (code form)       (L3)
  smoke.py              # run pipeline on the sample, grade PASS; run deficient input, assert FAIL (L4)
  sample_corpus.jsonl   # 12 raw rows -> wrangles to the 10-row M7 sample (1 dup + 1 null dropped) (L1/L4)
  sample_predictions.csv# the locked M7 10-row prediction set                                   (L1/L4)
  exam_brief.md         # the student's brief: the task, the inputs, the rubric, "compose not rebuild" (L1)
  tests/test_smoke.py   # pytest wrapper: the offline BUILD->TEST gate                           (L4)
  outputs/skill-integrated-exam.md   # the portfolio skill write-up                             (L4)
```

`pipeline.py` shape (composes; does not rebuild):

```
@dataclass ExamRun        # report_path, n_clean, metrics: list[ClassMetrics], composed_modules, version
def load_artifacts() -> tuple[wrangle_mod, eval_mod]   # via artifact_adapter (off disk)        (L2)
def run_pipeline(config) -> ExamRun                    # wrangle.run -> eval_engine.run -> report.md (L2)
if __name__ == "__main__": run_pipeline(default_config)   # exits 0
```

## The locked oracle (so the gate is deterministic)

`sample_corpus.jsonl` (12 raw rows) → wrangle drops **1 exact duplicate + 1 null-label row** → **10 clean
rows** whose `(id, label)` match the M7 sample. `sample_predictions.csv` = the locked M7 set. After the
chain, per-class metrics are the **already-verified M7 oracle**:

```
cat:  P 0.750  R 0.750  F1 0.750  support 4
dog:  P 0.667  R 0.500  F1 0.571  support 4
bird: P 0.667  R 1.000  F1 0.800  support 2
macro avg: P 0.694  R 0.750  F1 0.707  support 10
headline finding: dog is the weakest class (recall 0.500)
```

The report frames that finding. The conductor verifies these exact values + `n_clean == 10` before ship.

## The six acceptance criteria (rubric.py == prose; the single source of truth)

| id | criterion | passes when | fails (the deficient case) |
|----|-----------|-------------|----------------------------|
| R1 | **RUNS** | the pipeline ran end to end and wrote `report.md` (exit 0) | a stage raised; no report |
| R2 | **SCHEMA-VALID** | the wrangle stage validated: `n_clean == 10`, no null labels, dtypes correct | skip clean → wrong row count / null leak |
| R3 | **METRICS-CORRECT** | per-class P/R/F1 match the locked oracle within 1e-3 | a corrupted prediction shifts a metric |
| R4 | **COMPOSED** | the adapter imported the real `wrangle.py` + `eval_engine.py` off disk (no reimplementation) | a stage was re-coded inline, not imported |
| R5 | **PROBLEM-FRAMED** | the report names the dataset, the metric, and the headline finding (weakest class) | report is a bare number dump |
| R6 | **TESTED+VERSIONED** | the run declares a version + the smoke gate is green incl. the negative case | no version / negative case not tested |

`grade(ExamRun) -> RubricReport` reads only the captured `ExamRun` (graded from the record, never by
re-running). `passed` is True only when all six pass.

## Proposed M8 split (5 lessons; capstone arc, not four build-stages)

| # | Lesson (slug) | One idea | Kind | Composes |
|---|---------------|----------|------|----------|
| 0 | `00-overview` | The integrated exam: chain M6 + M7 into one graded pipeline; the terminal node of the throughline. What a hiring manager runs. | concept | — |
| 1 | `the-exam` | What the exam is: the take-home. Given a raw corpus + a prediction batch, produce an integrated, graded report. "Compose, do not rebuild." Bundles the sample inputs + `exam_brief.md`. | concept/build | — |
| 2 | `compose-the-pipeline` | Build `pipeline.py` + `artifact_adapter.py`: import `wrangle.py` + `eval_engine.py` off disk and chain ingest → clean → evaluate → report. The off-disk composition pattern. | build | M6, M7 |
| 3 | `the-rubric-and-grading` | Build `rubric.py`: the six criteria in code, matching the prose; grade by code not opinion; why a deficient run must fail. | build | all |
| 4 | `run-test-and-ship` | Run the worked example, write the `pytest` smoke gate (green run + deficient run fails), ship `skill-integrated-exam.md` and the portfolio repo. Just Python is complete. | build | all |

Each lesson ends in a Claude Code exercise building its part of the harness to the locked structure. L4
produces `smoke.py` + `tests/test_smoke.py` + `outputs/skill-integrated-exam.md`.

## The compounding throughline (STANDARDS Part 3 — the terminal node)

`pipeline.py` is the capstone artifact and the proof of the whole arc: `measure.py` (M1–M3) →
`vectorization_report.py` (M4, first composition) → `wrangle.py` (M6) → `eval_engine.py` (M7) → **`pipeline.py`
(M8) imports the last two off disk and chains them**. This is the exact pattern STANDARDS Part 3 reserves for
the capstone ("composes the prior artifacts, imports them off disk, does not rebuild them") and that Sans
Python M8 set with `fleet_adapter.py`. The skill write-up is the portfolio surface; the three runnable scripts
(`wrangle.py`, `eval_engine.py`, `pipeline.py`) are the GitHub repo the blueprint promises.

## Sources (three-source rule, non-negotiable)

1. **Ingredient:** the reader's own M6 `wrangle.py` + M7 `eval_engine.py` + the blueprint's M8 spec, and the
   Sans Python M8 harness as the structural exemplar (`run_exam.py`/`rubric.py`/`fleet_adapter.py`/`smoke.py`).
   No new vault ore.
2. **Microsoft Learn** via the connector — **Haiku fetchers pull the candidate pages; the Sonnet authors
   cite the verified URLs.** Real pages exist for the metric definitions (the Evaluate Model reference, cited
   in M3/M7) and for model-evaluation reporting; ground where a page fits, **state plainly where none does**
   (the M5/L1 rule), never fabricate.
3. **Editorial seam framing** — "this is the take-home you ship": one repo, three scripts, a graded report;
   the link back to Sans Python M8 (operate-and-judge) shows the lineage of the capstone idea.

## The fleet plan (conductor-direct; Sonnet authors, Haiku fetchers)

- **Conductor (Opus, this session):** locks the plan; dispatches **Haiku fetchers** to pull + verify the
  MS-Learn pages (metrics + evaluation reporting) and return real URLs + quotes; dispatches **4 Sonnet
  workers** (lessons 1–4) with those verified URLs folded into their briefs; authors `00-overview`;
  **assembles + runs the reference harness** (reference `wrangle.py` + `eval_engine.py` + the M8 files) as
  BUILD/TEST — the green run grades PASS, the deficient run grades FAIL, metrics match the oracle, `n_clean
  == 10`; runs the STYLE/STANDARDS (Part 2 + the Capstone Rubric) review on every draft; folds
  `SUMMARY.md` + `exercises/CLAUDE.md`.
- **Workers (Sonnet, parallel):** lessons 1–4, one writer per lesson file + its exercise README, each
  building its part **to the locked harness structure**. Briefs carry AUTHORING + STANDARDS (esp. Part 2 +
  Capstone Rubric) + STYLE + the M1–M7 exemplars + the Sans Python M8 exemplar + the Haiku-verified MS-Learn
  URLs + the locked oracle. Workers never touch `SUMMARY.md` or `exercises/CLAUDE.md` (conductor-folded).
- **Fetchers (Haiku, parallel, up front):** query the MS-Learn connector for the classification-metrics and
  model-evaluation-reporting pages; return verified URLs + short quotes; flag where no real page fits.

## Open decisions to pressure-test (lock these with Ray)

1. **Granularity / shape.** 5 lessons: overview / the-exam / compose-the-pipeline / the-rubric-and-grading /
   run-test-and-ship (proposed). Recommendation: **5** — the capstone arc (frame the exam → compose → grade →
   ship), consistent with the JP overview+4 shape, ending in the green gate + book completion.
2. **The canonical harness + `pipeline.py` shape + the six criteria + the locked oracle** (above). Confirm,
   so the four workers build one verified design (the M6/M7 fix). Recommendation: **lock as drafted.**
3. **Reuse the M7 oracle as the M8 oracle.** The sample corpus wrangles to the M7 10-row sample so the
   integrated metrics are the already-verified M7 values (one oracle, whole chain). Recommendation: **yes** —
   it makes the gate deterministic and proves M6 + M7 compose.
4. **Skill write-up + Haiku fetchers + conductor reference run.** Confirm M8 ships
   `outputs/skill-integrated-exam.md`, Haiku agents do the connector fetches feeding Sonnet authors, and the
   conductor assembles + runs the reference harness (PASS + deficient-FAIL) as BUILD/TEST.
   Recommendation: **yes.**

On lock: the fleet authors M8, VERIFY gates it against STYLE + the live connector (Haiku-fetched URLs),
BUILD/TEST assembles and runs the reference harness (the green run grades PASS, the deficient run grades FAIL,
metrics match the oracle) plus `mdbook build`, and the stage stops at `GATE-APPROVE-SHIP` before folding into
`src/`. On ship, **Just Python is complete (8/8)** and moves toward `library/completed/`.
