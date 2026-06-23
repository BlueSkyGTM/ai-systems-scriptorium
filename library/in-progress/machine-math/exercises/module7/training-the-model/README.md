# Exercise: Training the Model

A feature matrix with no model is just a spreadsheet. This exercise adds the model stage to `exercises/module7/pipeline.py`: a `GradientBoostingClassifier` with four hyperparameters, each chosen for a reason you can trace back to the bias-variance thread in Modules 2 through 4.

**Goal:** Add the model stage to `exercises/module7/pipeline.py` with the exact hyperparameters from the lesson. The gate is green when the pipeline trains and produces 200 predictions with probabilities in the unit interval.

**Why:** Choosing hyperparameters and justifying them against first principles is the difference between a tuned model and a guessed one. You built `ml.ensemble.GradientBoostingRegressor` from scratch in Module 4. Here you use sklearn's classifier version as the production tool, but every hyperparameter connects to something you derived.

## Before You Touch Code

Read the lesson at `src/module7/training-the-model.md`. Then open `exercises/module7/pipeline.py` and read its current state. You are adding one stage to an existing file, not starting from scratch. If `generate_data.py` has not been run yet, run it to produce `data.csv` before testing.

## The Stage You Add

Add the model stage immediately after the train/test split in `exercises/module7/pipeline.py`:

```python
    # ------------------------------------------------------------------
    # 4. Train
    # ------------------------------------------------------------------
    clf = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        random_state=42,
    )
    clf.fit(X_train, y_train)
```

Then add the prediction calls that the evaluation stage and tests need:

```python
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]
```

`y_pred` is a binary integer array (0 or 1); `y_proba` is a float array of positive-class probabilities. The second column of `predict_proba` is the churn probability; column 0 would be the no-churn probability. The evaluation stage sends `y_proba` to `ml.metrics.roc_auc` and `y_pred` to `ml.metrics.f1`.

The import at the top of `pipeline.py` for the classifier:

```python
from sklearn.ensemble import GradientBoostingClassifier
```

## Hyperparameter Reference

These are not magic numbers. Each connects to a prior lesson:

| Parameter | Value | Why |
|-----------|-------|-----|
| `n_estimators` | 200 | More trees at a low learning rate; the Module 4 lesson showed this lowers variance |
| `max_depth` | 4 | Shallow enough to stay a weak learner; the Module 3 overfitting lesson showed what unconstrained depth costs |
| `learning_rate` | 0.05 | Small steps regularize the fit; pairs with 200 estimators to reach the same loss as fewer trees at 0.2 |
| `subsample` | 0.8 | Stochastic boosting: 80% row sample per round diversifies trees and reduces variance |
| `random_state` | 42 | Seeds all randomness; the model card's reported numbers must be reproducible |

Do not change these values. The rubric checks AUC and F1 floors against a run with this exact configuration; a different learning rate or depth produces different numbers and may fail the gate.

## Done When

- `pipeline.run("exercises/module7/data.csv")` exits without error and returns a `PipelineResult`.
- `result.predictions` has length 200 (20% of 1,000 rows).
- `result.probabilities` has length 200, all values in [0.0, 1.0].
- `python -m pytest exercises/module7/the-dataset-and-the-feature-pipeline` still passes (the model stage must not break the composition tests).

The AUC and F1 floor tests from `test_pipeline.py` require the full evaluation stage to run, which is covered in the next exercise. At this stage the pipeline's `PipelineResult.metrics` can be populated with placeholder values; filling them with real `ml.metrics` calls is Lesson 3's work.

## Stretch

After `clf.fit`, print the training loss at the last iteration:

```python
print(f"Training loss (final iteration): {clf.train_score_[-1]:.4f}")
```

`train_score_` is a list of loss values for each boosting round, one per estimator. Plot it or print the first and last values to confirm the loss is decreasing. A flat or rising loss curve at the end means the learning rate is too high, the model overfit early, or the data has no learnable signal. This is the empirical check that the bias-variance tradeoff is working as expected.
