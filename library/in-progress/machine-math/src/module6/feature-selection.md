# Feature Selection

Adding more features does not make a model smarter; it makes the feature space larger and
the data sparser. M1 named this the curse of dimensionality. Here you learn to fight it.

## Why More Features Can Hurt

When you add a feature column, every sample gains one more coordinate. The volume of the
space grows exponentially with dimension. Real data does not. Points spread thin, distances
between neighbors converge, and the patterns you are trying to find get harder to see.

Noise features compound the problem. A column with no relationship to the target still
occupies a dimension the model must search. The model can find spurious correlations in
training data that do not hold on new data. Overfitting becomes the default outcome.

The goal is not to feed the model all available information. It is to feed the model the
right information.

## Measured: What Selection Changes

On a binary classification dataset with 8 features, where column 0 carries the signal and
columns 1 through 7 are pure noise, the measured accuracy difference is small but
directional.

| Features Used | Accuracy |
|---------------|----------|
| All 8 (signal + 7 noise) | 0.975 |
| Top-1 by `select_by_importance` (col 0) | 0.983 |

The noise columns did not help the decision tree; they hurt it slightly. Selecting the
signal column before training removes the search space the model would waste on noise.

For a simpler case: injecting a constant column (variance zero) into a 5-column dataset
and running `select_by_variance` at threshold 0.0 keeps indices [0, 1, 3, 4] and drops
index 2. A column that never varies tells the model nothing.

## Two Selection Functions

### Filter by Variance

A near-constant column carries almost no information. Drop every column whose variance
falls at or below a threshold before the model ever sees the data.

```python
def select_by_variance(
    X: np.ndarray,
    threshold: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Drop columns whose variance is <= threshold.

    A column with zero (or near-zero) variance carries no information;
    dropping it reduces noise for distance- and coefficient-based learners.

    Parameters
    ----------
    X : np.ndarray, shape (n, p)
    threshold : float
        Columns with var <= threshold are removed.

    Returns
    -------
    X_selected : np.ndarray, shape (n, k)  where k <= p
    kept_indices : np.ndarray of int, shape (k,)
    """
    X = np.asarray(X, dtype=float)
    variances = X.var(axis=0)
    kept = np.where(variances > threshold)[0]
    return X[:, kept], kept
```

This is a filter method: it looks at the feature itself, not at the target. Azure Machine
Learning's Filter Based Feature Selection component formalizes the same idea, describing
filter-based selection as using "statistical tests to inputs" to "filter out redundant
columns" before building a model. See
[Filter Based Feature Selection component reference](https://learn.microsoft.com/en-us/azure/machine-learning/component-reference/filter-based-feature-selection?view=azureml-api-2).

Variance filtering is fast and cheap, but a column can have high variance and still be
pure noise. It is a preprocessing step, not a complete strategy.

### Filter by Importance

Variance tells you nothing about how a feature relates to the target. Permutation
importance does. Fit a random forest on an 80% split, then, for each feature, shuffle
its values on the held-out 20% and measure the drop in accuracy. A large drop means the
model relied on that feature. A drop near zero means the feature is noise.

```python
def select_by_importance(
    X: np.ndarray,
    y: np.ndarray,
    k: int,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Keep the top-k features by permutation importance.

    Importance proxy: permutation importance
    ----------------------------------------
    A random forest is fit on an 80% training split. Each feature's importance
    is measured as the accuracy drop on the held-out 20% when that feature's
    values are randomly shuffled. Shuffling breaks the association between that
    feature and the label; a large accuracy drop means the model relied on that
    feature heavily. Features with near-zero (or negative) drop are noise.

    This proxy is straightforward and signal-based: noise features that happen
    to appear in many trees (due to random subsampling) don't get inflated
    counts -- they simply don't hurt accuracy when shuffled.

    The RandomForestClassifier from ml.ensemble is used.

    Parameters
    ----------
    X : np.ndarray, shape (n, p)
    y : np.ndarray, shape (n,)
    k : int
        Number of features to keep.
    random_state : int or None

    Returns
    -------
    X_selected : np.ndarray, shape (n, k)
    kept_indices : np.ndarray of int, shape (k,)
        Original column indices, sorted ascending.
    """
    from ml.ensemble import RandomForestClassifier

    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    n_samples, n_features = X.shape

    # Split 80/20 to get an honest evaluation set for permutation
    rng = np.random.default_rng(random_state)
    idx = rng.permutation(n_samples)
    n_train = int(n_samples * 0.8)
    train_idx, test_idx = idx[:n_train], idx[n_train:]

    forest = RandomForestClassifier(
        n_estimators=50,
        max_depth=None,
        max_features="sqrt",
        random_state=random_state,
    )
    forest.fit(X[train_idx], y[train_idx])

    X_test = X[test_idx]
    y_test = y[test_idx]
    baseline = float(np.mean(forest.predict(X_test) == y_test))

    # Permutation importance: accuracy drop when feature f is shuffled
    rng_perm = np.random.default_rng((random_state or 0) + 1)
    importance = np.zeros(n_features, dtype=float)
    for f in range(n_features):
        X_perm = X_test.copy()
        X_perm[:, f] = rng_perm.permutation(X_test[:, f])
        perm_acc = float(np.mean(forest.predict(X_perm) == y_test))
        importance[f] = baseline - perm_acc  # positive = feature mattered

    # Rank descending by importance; keep top-k
    ranked = np.argsort(importance)[::-1]
    kept = np.sort(ranked[:k])
    return X[:, kept], kept
```

This function uses the `RandomForestClassifier` from `ml.ensemble`, the M4 artifact. The
random forest fits, then each feature is shuffled in isolation on the test set. The
accuracy drop is the importance score.

The MS Learn Permutation Feature Importance component works exactly this way: "feature
values are randomly shuffled, one column at a time. The performance of the model is
measured before and after." It adds that "important features are usually more sensitive to
the shuffling process, so they'll result in higher importance scores." See
[Permutation Feature Importance component reference](https://learn.microsoft.com/en-us/azure/machine-learning/component-reference/permutation-feature-importance?view=azureml-api-2).

The key distinction from filter methods: permutation importance measures how much a
feature influences a trained model's predictions, not just how it correlates with the
target. A filter like Pearson correlation calculates scores before a model exists.

## The Method Landscape

Three families of selection methods cover most real problems.

**Filter methods** score each feature independently of the model. Variance threshold and
correlation filters are the cheapest options: they look only at the feature itself or its
relationship to the target, without training. Fast but blind to feature interactions.

**Embedded methods** fold selection into the training process. Tree importance (the
split-frequency score produced naturally by the M4 random forest) ranks features based on
how much impurity they reduce across all trees. L1 regularization drives linear model
weights exactly to zero, effectively removing features during training. These methods
capture some interaction effects but are tied to a specific model family.

**Wrapper methods** like Recursive Feature Elimination (RFE) retrain the model many times,
removing the least important feature at each round. More thorough, proportionally slower.
Permutation importance is a model-agnostic variant: it perturbs one feature at a time on
a trained model, which is cheaper than full retraining but still considers the model's
actual behavior.

| Method | Type | Nonlinear | Feature Interactions |
|--------|------|-----------|---------------------|
| Variance threshold | Filter | No | No |
| Correlation | Filter | No | No |
| L1 / Lasso | Embedded | No | No |
| Tree importance | Embedded | Yes | Yes |
| Permutation importance | Model-agnostic | Yes | Partial |
| RFE | Wrapper | Depends on model | Yes |

Choose filter methods as a first pass to cut obvious noise. Use embedded or permutation
methods to rank the survivors. The M1 curse of dimensionality tells you why this matters:
every column you keep is a dimension the model must search.

## Core Concepts

- The curse of dimensionality (M1) means that adding features grows the search space
  exponentially; noise features crowd out signal and push models toward overfitting.
- `select_by_variance` removes near-constant columns before the model trains; a column
  with variance at or below the threshold carries no useful information.
- `select_by_importance` fits the M4 random forest, then shuffles each feature in
  isolation on a held-out set; the accuracy drop is the importance score, and the top-k
  features are returned.
- Permutation importance measures a feature's influence on a trained model's predictions;
  filter methods like variance threshold score features before any model exists.

<div class="claude-handoff" data-exercise="exercises/module6/feature-selection/">

**Build It in Claude Code**: Read `exercises/CLAUDE.md` first, then read the current
state of `exercises/ml/features.py` to see what is already there. Your task is to add
`select_by_variance` and `select_by_importance` to `exercises/ml/features.py` exactly as
shown above. Note that `select_by_importance` imports `ml.ensemble.RandomForestClassifier`
(the M4 throughline artifact): read `exercises/ml/ensemble.py` to confirm the class
exists and its `fit` and `predict` signatures before writing anything. Then place the
locked acceptance gate verbatim at
`exercises/module6/feature-selection/test_selection.py` (the full test file is in the
exercise README). Done when
`python -m pytest exercises/module6/feature-selection` is green.

</div>
