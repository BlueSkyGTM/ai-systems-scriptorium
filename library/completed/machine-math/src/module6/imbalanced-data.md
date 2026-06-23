# Imbalanced Data

A model that scores 0.95 accuracy on a fraud-detection dataset may catch zero fraudulent
transactions. This is not a bug in the training code; it is accuracy lying to you.

## The Accuracy Trap

When a dataset splits 95% majority and 5% minority, a model can achieve 95% accuracy by
predicting "majority" on every single sample. The minority class is invisible to the
loss function. The model learned the one move that minimizes its training signal: ignore
the rare class entirely.

This is the same trap M5 introduced with the confusion matrix. Recall measures what the
accuracy trap hides: of every sample that actually belongs to the minority class, how
many did the model find?

```
recall = TP / (TP + FN)
```

On a 95/5 dataset, a model that predicts all-majority gets recall 0.0. Accuracy: 0.95.
Those two numbers describe the same model.

## Measured: What Imbalance Does

On a binary dataset of 1,000 samples with 95% majority and 5% minority (overlapping
distributions, mean separation 0.5), logistic regression trained on the raw data
converges to all-majority predictions. The training split holds 761 majority samples
and 39 minority samples.

| Training Data | Minority Recall |
|---------------|-----------------|
| Raw (761 maj / 39 min) | 0.0 |
| After `random_oversample` (761 / 761) | 0.4545 |

The model trained on raw data achieves roughly 0.95 accuracy and 0.0 minority recall.
After oversampling balances the training classes, minority recall rises to 0.4545. The
decision boundary now has a reason to move.

## Three Tools for the Training Signal

### Oversampling

Duplicate minority-class rows at random until every class has the same count as the
majority.

```python
def random_oversample(
    X: np.ndarray,
    y: np.ndarray,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Duplicate minority-class rows (with replacement) until classes are balanced.

    All majority-class samples are kept. The minority class is upsampled
    (bootstrap draw) to match the majority count. If more than two classes
    are present, every class below the maximum count is oversampled to the
    maximum count.

    Parameters
    ----------
    X : np.ndarray, shape (n, p)
    y : np.ndarray, shape (n,)
    random_state : int or None

    Returns
    -------
    X_res, y_res : balanced arrays (order: original rows first, then synthetic)
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    rng = np.random.default_rng(random_state)

    classes, counts = np.unique(y, return_counts=True)
    max_count = int(counts.max())

    X_parts = [X]
    y_parts = [y]

    for cls, cnt in zip(classes, counts):
        deficit = max_count - cnt
        if deficit > 0:
            idx = np.where(y == cls)[0]
            extra = rng.choice(idx, size=deficit, replace=True)
            X_parts.append(X[extra])
            y_parts.append(y[extra])

    return np.vstack(X_parts), np.concatenate(y_parts)
```

The cost is exact duplicates. The model sees the same minority samples many times, which
can cause overfitting on those specific rows. It also inflates the training set and slows
each epoch.

### Undersampling

Drop majority-class rows at random until every class is as small as the minority.

```python
def random_undersample(
    X: np.ndarray,
    y: np.ndarray,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Drop majority-class rows until all classes have the minority count.

    Parameters
    ----------
    X : np.ndarray, shape (n, p)
    y : np.ndarray, shape (n,)
    random_state : int or None

    Returns
    -------
    X_res, y_res : balanced arrays (row order not guaranteed)
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    rng = np.random.default_rng(random_state)

    classes, counts = np.unique(y, return_counts=True)
    min_count = int(counts.min())

    keep_idx = []
    for cls in classes:
        idx = np.where(y == cls)[0]
        chosen = rng.choice(idx, size=min_count, replace=False)
        keep_idx.append(chosen)

    keep = np.concatenate(keep_idx)
    keep.sort()          # consistent ordering
    return X[keep], y[keep]
```

Undersampling is fast and avoids duplicates. The cost is discarded majority data. On a
95/5 split with 1,000 samples, you train on 78 samples total (39 per class). Information
loss is real and can raise variance.

### Class Weights

Instead of resampling the data, change how much each error costs. Assign a higher weight
to misclassifying a minority sample.

```python
def class_weights(y: np.ndarray) -> dict:
    """Compute inverse-frequency class weights, normalized so they sum to n_classes.

    Weight for class c:
        w_c = n_samples / (n_classes * count_c)

    This matches sklearn's "balanced" mode and ensures the weighted loss treats
    each class equally regardless of sample count.

    Parameters
    ----------
    y : array-like, shape (n,)

    Returns
    -------
    dict mapping each unique class label to its weight (float).
    """
    y = np.asarray(y)
    classes, counts = np.unique(y, return_counts=True)
    n_samples = len(y)
    n_classes = len(classes)
    weights = {}
    for cls, cnt in zip(classes, counts):
        weights[cls] = float(n_samples / (n_classes * cnt))
    return weights
```

On a 95/5 dataset of 1,000 samples, `class_weights` returns approximately 0.526 for the
majority and 10.0 for the minority. One wrong prediction on the minority class costs as
much in the loss as nineteen wrong predictions on the majority. The data does not change;
the gradient does.

Class weights are mathematically equivalent to oversampling in expectation but without
creating duplicate rows. This makes them faster and avoids the overfitting risk of exact
copies.

## SMOTE: Synthesize, Don't Copy

SMOTE (Synthetic Minority Oversampling Technique) addresses the overfitting risk of
random oversampling by generating synthetic minority samples rather than duplicating
real ones.

For each minority sample, SMOTE finds its k nearest minority neighbors. It picks one at
random and creates a new sample at a random point on the line segment between them:

```
new_sample = x + random(0, 1) * (neighbor - x)
```

The new point sits in the same feature region as real minority samples without being
identical to any of them. Azure Machine Learning's SMOTE component implements this
directly, stating that "the algorithm takes samples of the feature space for each target
class and its nearest neighbors" and "generates new examples that combine features of the
target case with features of its neighbors." See
[SMOTE component reference](https://learn.microsoft.com/en-us/azure/machine-learning/component-reference/smote?view=azureml-api-2).

The synthetic points can be noisy near the decision boundary, where minority and majority
samples overlap. SMOTE also does not shift the majority distribution, so a severe imbalance
still requires a large percentage multiplier. Treat SMOTE as conceptually superior to
random oversampling, but verify on your data: the MS Learn documentation notes that
"increasing the number of cases by using SMOTE doesn't guarantee more accurate models."

## Which Strategy to Use

| Strategy | Data Changed | Risk | When to Reach For It |
|----------|-------------|------|----------------------|
| Oversample | Minority duplicated | Overfitting on copies | Small datasets, moderate imbalance |
| Undersample | Majority removed | Information loss | Large datasets, fast training needed |
| SMOTE | Synthetic minority added | Boundary noise | Enough minority samples for k-NN search |
| Class weights | Nothing | Slower convergence | Any size; preferred default to try first |

All four attack the same root cause: the loss function sees too few minority examples to
produce a useful gradient. Pick the strategy that fits your data size and your tolerance
for duplicates versus information loss.

## Core Concepts

- On a 95/5 imbalanced dataset, a model can reach 0.95 accuracy by predicting the
  majority class on every sample, yielding minority recall of 0.0; the M5 confusion
  matrix is the tool that surfaces this.
- Random oversampling duplicates minority rows until classes are balanced, lifting
  minority recall at the cost of exact-copy overfitting risk.
- Random undersampling drops majority rows to the minority count, which is fast but
  discards real data.
- Class weights assign inverse-frequency costs to each class, making one minority
  misclassification as expensive as many majority ones, without changing the training set.
- SMOTE synthesizes new minority samples by interpolating between real minority neighbors
  rather than copying them, reducing the overfitting risk of random oversampling.

<div class="claude-handoff" data-exercise="exercises/module6/imbalanced-data/">

**Build It in Claude Code**: Read `exercises/CLAUDE.md` first, then read the current
state of `exercises/ml/features.py` to see what is already there from earlier modules.
Your task is to add `random_oversample`, `random_undersample`, and `class_weights` to
`exercises/ml/features.py` exactly as shown above. Do not copy any function that already
exists. Then place the locked acceptance gate verbatim at
`exercises/module6/imbalanced-data/test_imbalance.py` (the full test file is in the
exercise README). Done when
`python -m pytest exercises/module6/imbalanced-data` is green.

</div>
