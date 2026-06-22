# Machine Math — Build Progress

Per-stage authoring status. One row per module.

| Module | Title | Status | Shipped | Notes |
|--------|-------|--------|---------|-------|
| M1 | The Shape of Data | ✅ Shipped | 2026-06-21 | Overview + 2 lessons (feature-vectors, knn-voting) + 2 exercises. Installs the book's core reframing (a row is a point in feature space) by pairing the linear-algebra primitives (vectors, the dot product, Euclidean/cosine/Manhattan distance, min-max + z-score scaling) with k-nearest neighbors, the first algorithm that is pure geometry. Seeds the **from-scratch `exercises/ml/` package** throughline: `ml/distances.py` (three metrics + two scalers + the `METRICS` dispatch table) and `ml/knn.py` (the lazy `KNNClassifier` that imports `METRICS`, real reuse). Each exercise ships a `pytest` acceptance gate; the negative case is tested (a feature blown up by 1000x sinks an unscaled vote, z-scoring recovers it: 0.800 -> 1.000). Ships `exercises/CLAUDE.md`. First module of this book, so it also distilled the book's first ingredients from raw `aefs` ore (`ingredients/source/machine-math/`) and stood up the mdBook scaffold. Plan: `m1/PLAN.md`. |
| M2 | Fitting a Line (and Its Limits) | 📋 Planned | — | Derivatives, gradient descent, the convex loss surface; paired with linear + logistic regression and the bias-variance tradeoff. Adds `ml/linreg.py` + `ml/gradient_descent.py`. |
| M3 | Splitting and Branching | 📋 Planned | — | Information theory (entropy, Gini, information gain); paired with decision trees + recursive partitioning. Cross-validation and overfitting enter. Adds `ml/tree.py`. |
| M4 | Ensembles and the Gradient | 📋 Planned | — | Bagging vs boosting; the chain rule on residuals; random forests + gradient boosting (XGBoost/LightGBM). Adds `ml/ensemble.py` (reuses `tree.py`). |
| M5 | What "Good" Means | 📋 Planned | — | Probability, distributions, threshold reasoning; AUC-ROC, F1/precision-recall, MAE/RMSE, slice metrics. Adds `ml/metrics.py` (from scratch). |
| M6 | Feature Reality | 📋 Planned | — | Scaling, encoding, selection, imbalanced data; paired with the feature pipeline + naive Bayes. Adds `ml/features.py` + `ml/naive_bayes.py`. |
| M7 | The Portfolio Artifact | 📋 Planned | — | The capstone: a real tabular pipeline (manual features + gradient-boosted classifier) graded by the from-scratch `ml/metrics.py`, with a model card that maps each result to its math. **Composes M5 + M6 off disk.** |

## Provenance

M1 graduated the book through `GATE-NAME-BOOK` (title **Machine Math**, slug `machine-math`, chosen
2026-06-21 from the blueprint's lead candidate) and ran the full AUTHOR → VERIFY → BUILD/TEST → SHIP
cycle. `GATE-LOCK-PLAN` was cleared by Ray's "go" against the pre-vetted Module 1 draft (low
wasted-work risk); `GATE-APPROVE-SHIP` was presented and approved before the commit. Ray also approved
self-clearing `GATE-APPROVE-SHIP` for M2–M7 to run the book straight through.

Authored under the standing division of labor (Ray's 2026-06-21 mandate, corrected mid-M1): **Haiku
fetch tier → Sonnet authors → Opus conducts and gates.** Two Haiku workers distilled the raw `aefs`
math/ML ore (`vault/ai-engineering-from-scratch/phases/01-math-foundations` + `02-ml-fundamentals`)
into `ingredients/source/machine-math/`. Three Sonnet workers authored the two lessons and finished the
overview, exercises, and coaching contract, using their coding tools. Opus locked the M1 plan and the
artifact contract (the `ml/` package signatures + the `pytest` gate shape), dispatched, reviewed every
draft against STYLE + STANDARDS, and ran the gate. (Opus also hand-built the initial `ml/` reference
harness before Ray's "no excessive coding on your part" correction; that tested reference now lives in
`m1/output/author/ref/` as the answer key, and code authoring moved to the Sonnets thereafter.)

VERIFY + BUILD/TEST results at ship: `mdbook build` clean; the reference `pytest` harness 10/10 green;
zero em-dashes book-wide; 7 Microsoft Learn citations live-fetched and verified (4 in feature-vectors,
3 in knn-voting); `route-lint` green. The from-scratch dependency policy held: NumPy for all algorithms,
scikit-learn only as the dataset source and the test oracle.
