# Module 2 — Fitting a Line (and Its Limits) — Build Plan

Status: **PLAN SELF-LOCKED 2026-06-21** (Ray approved running M2–M7 straight through, self-locking plans
and self-clearing `GATE-APPROVE-SHIP` per module). Inherits every locked decision from M1's PLAN: stage =
module; held to AUTHORING + STANDARDS + STYLE; from-scratch NumPy with scikit-learn only as dataset source
+ test oracle; the growing `exercises/ml/` package gated by `pytest`; Haiku fetch tier -> Sonnet authors
(who build + test the code with their tools) -> Opus conducts, reviews, and runs the gate. Opus does NOT
hand-write the implementations (Ray's correction); Opus locks the artifact contract below and the Sonnet
builds to it.

## The stage in one line

M2 is where the model starts to learn. M1's k-NN had no parameters; M2 introduces the first algorithms
that fit parameters by minimizing a loss, and the calculus that drives the fit: the derivative points
downhill, gradient descent follows it, and a convex loss guarantees the bottom is the global best. Paired
fundamentals: linear regression, logistic regression, and the bias-variance tradeoff that says a better
fit on training data is not the goal.

## Ore (distill first, into ingredients/source/machine-math/)

Haiku fetch tier distills these `aefs` lessons (each has docs/en.md + code/):
- Phase 01: `04-calculus-for-ml`, `05-chain-rule-and-autodiff`, `08-optimization`, `18-convex-optimization`
  -> `ingredients/source/machine-math/aefs-calculus-and-optimization.md`
- Phase 02: `02-linear-regression`, `03-logistic-regression`, `10-bias-variance`
  -> `ingredients/source/machine-math/aefs-regression-and-bias-variance.md`

## Locked split (overview + 4 lessons, one idea each)

| # | Lesson (slug) | One idea | Builds |
|---|---------------|----------|--------|
| 0 | `00-overview` | From storing data (M1) to fitting parameters: loss, gradient, descent, and the limit (overfitting). | — |
| 1 | `gradient-descent` | The derivative points uphill; step the opposite way, scaled by a learning rate; a convex loss has one bottom. | `ml/gradient_descent.py` (generic `gradient_descent(grad_fn, theta0, lr, n_iters)` returning params + loss history) |
| 2 | `linear-regression` | Fit a line by minimizing mean squared error; the MSE gradient is the descent signal; the normal equation is the closed form. | `ml/linreg.py` (`LinearRegression.fit/predict`, GD-based, reuses `gradient_descent`) |
| 3 | `logistic-regression` | The sigmoid squashes a linear score to a probability; cross-entropy loss; the gradient has the same shape as linear regression's. | `ml/logreg.py` (`LogisticRegression.fit/predict/predict_proba`, reuses `gradient_descent`) |
| 4 | `bias-variance` | A lower training error is not the goal; underfit vs overfit is a tradeoff you read from the gap between train and test error. | concept; demonstrated by fitting polynomial-featured `linreg` at rising degree and plotting train vs test error |

## Artifact contract (Opus locks; Sonnet builds + tests to this)

- `ml/gradient_descent.py`: `gradient_descent(grad_fn, theta0, lr=0.1, n_iters=1000)` -> `(theta, history)` where
  `history` is the list of loss values; pure NumPy; deterministic.
- `ml/linreg.py`: `class LinearRegression` with `fit(X, y)` (GD on MSE via `gradient_descent`, fits intercept),
  `predict(X)`. A `normal_equation(X, y)` helper for the closed-form cross-check.
- `ml/logreg.py`: `class LogisticRegression` with `fit`, `predict_proba`, `predict` (threshold 0.5); binary;
  numerically stable sigmoid.
- Each reuses earlier package code where real (logreg/linreg share `gradient_descent`; scaling via M1
  `ml/distances.zscore` where features need it). No duplication.

## Acceptance gate (the `pytest` done-when per exercise; Sonnet writes, Opus runs)

- gradient-descent: descent on a known convex function (e.g. `(theta-3)**2`) converges to the minimum; loss
  history is monotonically non-increasing.
- linear-regression: GD coefficients match `normal_equation` and `sklearn.linear_model.LinearRegression` on a
  fixed synthetic/`load_diabetes` slice within tolerance; R^2 clears a floor.
- logistic-regression: accuracy on a scaled binary set (e.g. two Iris classes, or `load_breast_cancer`) clears
  a floor and agrees with `sklearn.linear_model.LogisticRegression` within tolerance.
- bias-variance (negative case): test error rises while train error keeps falling as polynomial degree grows
  (overfitting demonstrated by code, not asserted by opinion).

## Grounding + fleet

Three-source rule: distilled ingredient + Microsoft Learn (Azure ML linear/logistic regression components,
gradient-based training; verified live, real URLs, no bare markers) + the seam framing ("a Production AI
Engineer reasons about why a model overfits"). Conductor-direct, no handler tier. Haiku x2 distill the two
ingredients; Sonnet author tier builds + tests `ml/gradient_descent.py`/`linreg.py`/`logreg.py` in the m2
ref harness, captures real numbers (loss curves, R^2, accuracy, the train/test gap), and authors the
overview + 4 lessons + 4 exercise READMEs (embedding the tested code). Opus reviews against STYLE/STANDARDS,
runs the ref `pytest` + `mdbook build`, then ships (commit + push machine-math paths).
