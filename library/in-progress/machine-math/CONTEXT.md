# CONTEXT — Machine Math (IN PROGRESS)

Classic ML fundamentals (regression, trees, boosting, AUC-ROC, feature engineering) paired with the
math each one requires (linear algebra / calculus / probability / information theory), at applied
depth. The thesis: math arrives bolted to the fundamental that needs it. Neither half is taught alone.
Fills antilibrary gap rows 3 + 6 from `build-log/sans-python/antilibrary-gap-report.md`.

**Graduated 2026-06-21; CONTENT-COMPLETE (7/7 modules shipped same day).** `GATE-NAME-BOOK` cleared
(title **Machine Math**, slug `machine-math`). All seven modules shipped: M1 The Shape of Data (k-NN +
distance), M2 Fitting a Line (gradient descent + linear/logistic regression + bias-variance), M3
Splitting and Branching (information theory + decision trees + cross-validation), M4 Ensembles and the
Gradient (bagging/random forests + gradient boosting), M5 What "Good" Means (the from-scratch evaluation
library), M6 Feature Reality (encoding/naive Bayes/imbalance/selection), M7 The Portfolio Artifact (the
capstone). The book builds one **from-scratch `exercises/ml/` package** across M1-M6 (distances, knn,
gradient_descent, linreg, logreg, tree, ensemble, metrics, features, naive_bayes), and the M7 capstone
`pipeline.py` + `rubric.py` **composes `ml.features` + `ml.metrics` off disk** to build, evaluate, and
grade a real model with a model card. 23 lessons + 7 overviews + 23 exercises, every code artifact
`pytest`-gated with a negative case, every external claim grounded in a live Microsoft Learn citation,
`mdbook build` clean, zero em-dashes book-wide. Authored under the Haiku-fetch / Sonnet-build+author /
Opus-conduct+gate division of labor. See `build-log/machine-math/build-progress.md` for per-module
detail. Next: a public copy is the separate `GATE-PUBLISH`; relocation to `library/completed/` is the
cataloguing move once confirmed.

**Scope boundary (recorded):** PyTorch, deep-model training, fine-tuning, and neural-network math are
OUT of scope. They are split into a separate planned book ("Weights and Measures"). This book ends
where the neural network begins. Classic ML only; the math it requires only.

**Post-Sans-Python positioning:** Sans Python is the core roadmap (LLM engineering, agents, fleet,
deploy). Machine Math branches from it for readers who need the MLE-adjacent layer: the ML-system-design
interview, feature work, and the math the interviewer assumes fluency in.

## Ore (in the vault — not yet distilled)

- `ai-engineering-from-scratch` (`aefs`) Phase 01 (Math Foundations) + Phase 02 (ML Fundamentals): the
  primary ore for both halves of this book.
- `made-with-ml` (`mwml`) classic-ML notebook and evaluation pipeline (`data.py`, `evaluate.py`,
  `predict.py`, holdout dataset): evaluation and artifact ore. Training internals (`train.py`,
  `models.py`, `tune.py`) are antilibrary for mwml (PyTorch / deep-training seam) and remain excluded.
- Survey both at process-ore time via `vault/MANIFEST.md` and `ingredients/source/_repos/`.

## Dual-use

Written to be **read by a human learner and ingested by an LLM** — dense, linked, plain markdown. An
LLM using this book as context for an ML-system-design question should be able to cite the relevant
math and the relevant fundamental in the same sentence, because the book stores them adjacent.

## Load / don't-load

- **Load:** this folder's `README.md` and `draft/`, the named vault ore via `vault/MANIFEST.md`,
  `ingredients`, `platform/conventions` (AUTHORING + STANDARDS + STYLE), `platform/pipeline`.
- **Do NOT load:** the shipped Sans Python book; other books; any `made-with-ml` training internals
  (`train.py`, `models.py`, `tune.py`); anything under `skills/` or `gstack/`.

## Handoff & gates

`GATE-NAME-BOOK` cleared; **all 7 modules shipped** (`GATE-LOCK-PLAN` + `GATE-APPROVE-SHIP` cleared per
module 2026-06-21; Ray approved self-clearing `GATE-APPROVE-SHIP` for M2-M7 to run the book straight
through). The book is content-complete. Remaining gates: **`GATE-PUBLISH`** for a public copy (private-first
is the default), and the cataloguing move to `library/completed/machine-math` once Ray confirms (a
git-tracked relocation + route-manifest/router/CATALOG update + `route-lint` green, as Just Python and
Local Metal did). See `platform/HUMAN-GATES.md` and `build-log/machine-math/build-progress.md`.
