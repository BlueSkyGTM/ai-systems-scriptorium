# Module 7 — The Portfolio Artifact — Build Plan (the capstone)

Status: **PLAN SELF-LOCKED 2026-06-21** (M2–M7 straight-through). Inherits all locked decisions. This is
the capstone: it COMPOSES the from-scratch `exercises/ml/` package (built across M1–M6) into one runnable,
reviewable ML system, graded by code against a rubric, in the Sans Python M6/M7/M8 mold.

## The stage in one line

The reader has built a from-scratch ML library across six modules. M7 makes it earn its keep: a complete
tabular pipeline on a real dataset that engineers features with `ml/features.py`, trains a gradient-boosted
classifier, evaluates it honestly with `ml/metrics.py` (AUC-ROC, F1, precision/recall, and per-subgroup
slice metrics), and writes a model card that maps every number back to the math that produced it. A
`rubric.py` grades the run against six criteria in code; the same six are in the lesson prose. The math is
not hidden in a library call: the reader's own metrics grade a real model.

## Composition (STANDARDS Part 3: the capstone composes prior artifacts off disk)

`pipeline.py` imports `ml.features` (encode + scale) and `ml.metrics` (evaluate + slice) OFF DISK and uses
them on a real model. The MODEL may be scikit-learn's `GradientBoostingClassifier` (the realistic production
choice, per the blueprint's "scikit-learn + LightGBM"); the FEATURE ENGINEERING and the EVALUATION are the
reader's own from-scratch code. That is the proof: the reader's library does the engineering and the
grading; sklearn supplies only the model.

## Ore

Supporting: a Haiku distills `made-with-ml` (`vault/made-with-ml`) `data.py` / `evaluate.py` / `predict.py`
and the notebook's data-and-eval sections -> `ingredients/source/machine-math/mwml-pipeline-and-evaluation.md`
(the shape of a real eval pipeline + model-card/evaluation framing; training internals stay antilibrary).

## Locked split (overview + 4 lessons, one idea each)

| # | Lesson (slug) | One idea | Builds |
|---|---------------|----------|--------|
| 0 | `00-overview` | Assemble the six modules into one graded ML system; the math is visible in every result. | — |
| 1 | `the-dataset-and-the-feature-pipeline` | Load a real tabular dataset and engineer it with your own ml/features.py: encode categoricals, scale numerics, hold out a test set. | `pipeline.py` data + feature stage (composes `ml.features`) + the dataset |
| 2 | `training-the-model` | Train a gradient-boosted classifier and justify each hyperparameter against the bias-variance thread. | `pipeline.py` model stage |
| 3 | `honest-evaluation-and-slicing` | Grade the model with your own ml/metrics.py: AUC and F1 overall, then slice by subgroup to find where it fails. | `pipeline.py` eval stage (composes `ml.metrics`) |
| 4 | `the-model-card-and-the-rubric` | A model card maps each metric to its math; rubric.py grades the run on six criteria in code, and a deficient run fails the criterion it offends. | `rubric.py` + `MODEL_CARD.md` |

## Artifact contract (Opus locks; Sonnet builds + tests)

- A real, OFFLINE, DETERMINISTIC tabular dataset bundled as a committed CSV (`data.csv`): at least 2 numeric
  + at least 1 categorical feature, a binary target, and a subgroup column for slicing. Prefer a real public
  source (e.g. a bundled/real dataset); if synthetic is necessary for offline determinism, generate it
  seeded and document its provenance honestly in the model card. Several hundred rows minimum.
- `pipeline.py`: `run(data_path) -> PipelineResult` (a small dataclass: predictions, probabilities,
  metrics dict, slice dict, model-card path/string, composed_modules list, version). Stages: load -> engineer
  features via `ml.features` (one_hot_encode categoricals, zscore numerics) -> train a
  `sklearn.ensemble.GradientBoostingClassifier` (seeded) -> evaluate via `ml.metrics` (roc_auc, f1,
  precision, recall on the held-out set) -> slice via `ml.metrics.slice_metric` over the subgroup column ->
  write `MODEL_CARD.md`. Imports `ml.features` + `ml.metrics` OFF DISK (real composition).
- `rubric.py`: `CRITERIA` tuple of six (id, description) + `grade(result) -> dict id->bool` + a `main` that
  prints the scorecard and exits 0 iff all pass. The six: R1 RUNS, R2 FEATURES-ENGINEERED (categoricals
  encoded + numerics scaled via ml.features), R3 EVALUATED (AUC + F1 + P/R via ml.metrics clear a floor),
  R4 SLICED (per-subgroup metrics computed; worst slice identified), R5 COMPOSED (imports ml.features +
  ml.metrics off disk), R6 MODEL-CARD (card exists with the required sections). The CRITERIA tuple and the
  lesson-4 prose table are ONE rubric in two forms.
- `MODEL_CARD.md`: sections mapping each result to its math (the AUC, the F1, the slice table, the
  hyperparameters), in the style the lesson teaches.

## Acceptance gate (Sonnet writes, Opus runs)

- `pipeline.run(data.csv)` produces predictions + metrics; `rubric.grade` returns 6/6 True on the good run;
  AUC and F1 clear a sane floor; the slice dict has one entry per subgroup and identifies the worst.
- COMPOSITION test: pipeline actually imports ml.features + ml.metrics off disk (not reimplemented).
- DEFICIENT RUN (the negative case, STANDARDS): a deliberately broken run (e.g. skip feature scaling/encoding,
  or omit slicing, or a stub model card) fails exactly the rubric criterion it offends; `rubric.main` exits
  nonzero. Proven by measurement.

## Grounding + fleet

Three-source: distilled mwml ingredient + Microsoft Learn (Azure ML Responsible AI model card / scorecard,
AUC as the primary AutoML metric, error-analysis cohorts for slicing; verified live) + the seam framing (the
artifact an interviewer can see on GitHub). One Haiku distills the mwml ingredient; one Sonnet builds + tests
`pipeline.py` + `rubric.py` + the dataset + the model card in the m7 ref harness and captures real numbers
(the model's AUC/F1, the slice table, the 6/6 grade, the deficient-run failure); two Sonnet authors write the
overview + 4 lessons + 4 exercise READMEs (embedding the tested code + the rubric table). Opus reviews, runs
`pytest` + `mdbook build`, ships. On ship, Machine Math is content-complete (7/7).
