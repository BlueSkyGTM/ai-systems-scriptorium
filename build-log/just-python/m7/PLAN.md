# Module 7 — Evaluation Engine — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared — Ray locked as drafted: all 4 decisions
accepted — 5 lessons, canonical eval_engine.py + locked sample/expected metrics, zero-division=0.0, skill
write-up + connector + conductor smoke).** **SHIPPED 2026-06-21 (`GATE-APPROVE-SHIP` cleared).** Seventh authoring stage for Just
Python, the **second portfolio module** (Composition phase). M1–M6 shipped. M7 turns the blueprint's seventh module into a
finished mdBook chapter + a runnable portfolio artifact, under AUTHOR → VERIFY → BUILD/TEST → SHIP. Do not
author until Ray locks.

## The stage in one line

M6 produced a clean dataset; M7 judges a model against one. The reader builds `eval_engine.py`: it reads a
batch-prediction file (`id, prediction, label`), computes **per-class precision, recall, and F1 with NumPy
(no sklearn)**, and emits a Markdown evaluation table. Seam: a single accuracy number hides which class the
model fails; the per-class table is what an engineer actually reports, and computing it by hand with boolean
masks is the M2 vectorization payoff made concrete.

## Settled decisions (from the blueprint + the contracts)

1. **Portfolio shape (STANDARDS Part 2 is the bar).** Same rubric as M6: real entry point
   (`python exercises/module7/eval_engine.py` exits 0), README frames the business problem, a `pytest` smoke
   gate with a negative case, clean layout/no secrets, and a shipped skill write-up
   (`exercises/module7/outputs/skill-evaluation-engine.md`).
2. **Composition (STANDARDS Part 3).** `eval_engine.py` composes the book: **M2** (boolean masks + reductions
   for the TP/FP/FN counts), **M3** (Pandas to read the prediction file), **M5** (a `@dataclass ClassMetrics`
   record, type hints). It pairs with M6 in the data layer: M6 emits a validated dataset, M7 evaluates
   predictions over that kind of data. It links editorially back to the Sans Python M7 evaluation tables.
3. **No sklearn.** The metric math is written by hand in NumPy. That is the point: the reader proves they
   understand precision/recall/F1 as counts, not as an import. (sklearn is the antilibrary here.)
4. **Pre-specified artifact structure (the M6 lesson).** M6 showed one shared artifact across four cold
   workers drifts without a locked contract. This PLAN fixes `eval_engine.py`'s structure, the sample
   prediction set, and the **expected metric values** (below), so workers build to one verified design and
   the conductor assembles + runs the reference as BUILD/TEST.
5. **Learner-built, not committed.** Exercises build `eval_engine.py` / `smoke.py` / the skill write-up; the
   conductor verifies a reference build runs, then discards it. Ore = M2/M3/M5 + the blueprint; no new vault
   ore (the metric definitions are grounded via the MS-Learn connector, which has real precision/recall/F1
   pages — verified earlier this session at `azure/machine-learning/component-reference/evaluate-model`).

## The canonical `eval_engine.py` structure (locked so workers build one design)

```
@dataclass(frozen=True) EvalConfig    # input_path, output_path (.md), pred_col="prediction", label_col="label"
@dataclass ClassMetrics               # cls: str, precision: float, recall: float, f1: float, support: int  (M5)
def load_predictions(path, config) -> pd.DataFrame         # read CSV (id, prediction, label), typed        (L1)
def confusion_counts(df, cls, config) -> tuple[int,int,int]  # (tp, fp, fn) for one class, NumPy masks       (L2)
def per_class_metrics(df, config) -> list[ClassMetrics]    # P/R/F1/support per class; safe zero-division    (L3)
def to_markdown_table(metrics) -> str                      # Markdown eval table (+ macro avg row)            (L3)
def run(config) -> list[ClassMetrics]                      # compose; write the .md table; return metrics     (L4)
if __name__ == "__main__": run(default_config)             # exits 0
```

## The locked sample + expected metrics (so the gate is deterministic and hand-verifiable)

Sample `predictions.csv` (10 rows), and the per-class results the smoke asserts:

```
id,prediction,label        per class (TP/FP/FN -> P / R / F1, support):
1,cat,cat                  cat:  TP3 FP1 FN1 -> 0.750 / 0.750 / 0.750, support 4
2,cat,dog                  dog:  TP2 FP1 FN2 -> 0.667 / 0.500 / 0.571, support 4
3,dog,dog                  bird: TP2 FP1 FN0 -> 0.667 / 1.000 / 0.800, support 2
4,bird,bird
5,cat,cat                  (predictions: 1cat 2cat 3dog 4bird 5cat 6dog 7bird 8dog 9cat 10bird)
6,dog,cat                  (labels:      1cat 2dog 3dog 4bird 5cat 6cat 7bird 8dog 9cat 10dog)
7,bird,bird
8,dog,dog
9,cat,cat
10,bird,dog
```

Conductor verifies these exact values before ship. Zero-division rule: if a class has no predictions,
precision = 0.0; if it has no true instances, recall = 0.0 (the sklearn convention, stated in prose), never
a `ZeroDivisionError`.

## Proposed M7 split (5 lessons; each builds one stage of the one artifact)

| # | Lesson (slug) | One idea / stage | Kind | Composes |
|---|---------------|------------------|------|----------|
| 0 | `00-overview` | M6 cleaned the data; M7 judges a model on it. Per-class P/R/F1 from scratch, the metric an engineer reports. | concept | — |
| 1 | `load-the-predictions` | Read the `id, prediction, label` file into a typed DataFrame; an `EvalConfig` frozen dataclass names the columns. | build | M3, M5 |
| 2 | `confusion-counts-with-numpy` | Per class, the TP/FP/FN are three boolean masks and a sum; this is the M2 vectorization lesson applied to a real metric, no sklearn. | build | M2 |
| 3 | `precision-recall-f1` | Turn the counts into precision, recall, and F1 per class into a `ClassMetrics` record, handling zero-division the way production code must. | build | M2, M5 |
| 4 | `emit-test-and-ship` | Render the Markdown table (with a macro-average row), compose the stages in `run`, write the `pytest` smoke gate (incl. negative case) and the skill write-up. | build | all |

Each lesson ends in a Claude Code exercise building its stage of `eval_engine.py` to the locked structure;
the L4 exercise also produces `smoke.py` + `outputs/skill-evaluation-engine.md`.

## The compounding throughline (STANDARDS Part 3)

`eval_engine.py` is the M7 portfolio artifact: it composes M2 (the mask-and-reduce metric math), M3 (the
read), and M5 (the `ClassMetrics` dataclass + type hints), and sits beside M6 in the data layer (M6 makes the
dataset; M7 evaluates predictions over it). The skill write-up is the portfolio surface. M8 (the capstone)
then chains M6 + M7: ingest a corpus, wrangle it, evaluate predictions, emit a report, under a graded rubric.

## Sources (three-source rule, non-negotiable)

1. **Ingredient:** the reader's own M2/M3/M5 work + the blueprint's M7 spec. No new vault ore; the metric
   math is standard.
2. **Microsoft Learn** via the connector — workers ground the precision/recall/F1 definitions in a real page
   with a real URL (the Evaluate Model metrics reference is confirmed real and was cited in M3). No bare
   markers; never fabricate.
3. **Editorial seam framing** — "accuracy hides the failing class": the per-class table is what you put in a
   model card / a PR description, and the link back to the Sans Python M7 evaluation tables shows the lineage.

## The fleet plan (conductor-direct; shared artifact pre-specified)

- **Conductor (Opus, this session):** locks the plan (with the canonical structure + sample + expected
  values), dispatches 4 Sonnet workers, authors `00-overview`, **assembles + runs the reference
  `eval_engine.py` + `smoke.py`** (verifying the expected metric values + the negative case) as BUILD/TEST,
  and runs the STYLE/STANDARDS (Part 2) review on every draft.
- **Workers (Sonnet, parallel):** lessons 1–4, one per stage, one writer per lesson + its exercise README,
  each building its stage **to the locked structure**. Briefs carry AUTHORING + STANDARDS + STYLE + the
  M1–M6 exemplars + the MS-Learn connector instruction + the locked sample/expected-metrics. Workers never
  touch `SUMMARY.md` or `exercises/CLAUDE.md` (conductor-folded).

## Open decisions to pressure-test (lock these with Ray)

1. **Granularity / stages.** 5 lessons: load / confusion-counts / P-R-F1 / emit-test-ship (proposed).
   Recommendation: **5** — four artifact stages + overview, ending in the green gate.
2. **The canonical `eval_engine.py` structure + the locked sample/expected metrics** (above). Confirm, so the
   four workers build one verified design (the M6 fix). Recommendation: **lock as drafted.**
3. **Zero-division convention.** precision = 0.0 when no predictions; recall = 0.0 when no support; never
   raise. Recommendation: **yes** (the sklearn convention; document it in prose).
4. **Skill write-up + connector + conductor smoke.** Confirm M7 ships `outputs/skill-evaluation-engine.md`,
   workers use the connector, and the conductor assembles + runs the reference `eval_engine.py` + `smoke.py`.
   Recommendation: **yes.**

On lock: the fleet authors M7, VERIFY gates it against STYLE + the live connector, BUILD/TEST assembles and
runs the reference `eval_engine.py` + `smoke.py` (asserting the locked metric values + the negative case) plus
`mdbook build`, and the stage stops at `GATE-APPROVE-SHIP` before folding into `src/`.
