# Boosting and the Gradient

Bagging cuts variance by averaging independent trees. Boosting attacks the other side of
the tradeoff: it cuts bias by fitting the errors the ensemble keeps making. The two
methods are not competing; they fix different problems.

## The Algorithm

Start with a constant prediction: the mean of the training targets. Call it `F_0(x)`.
Compute the residuals: for every training sample `i`, the residual is `y_i - F_0(x_i)`.
Fit a shallow regression tree to those residuals. Add a fraction of that tree's
predictions to your ensemble:

```
F_1(x) = F_0(x) + learning_rate * h_1(x)
```

where `h_1` is the tree fitted to the residuals. Compute the new residuals against
`F_1`, fit another tree, add another shrunken contribution. Repeat for `n_estimators`
rounds.

The learning rate, also called shrinkage, controls how much each tree contributes. A
smaller rate requires more rounds to reach the same training error, but the ensemble
generalizes better because no single tree dominates. Typical values run from 0.01 to 0.1
in production.

## The Gradient Connection

For squared-error loss, `L(y, F) = (1/2)(y - F)^2`, the negative gradient with respect
to `F` at sample `i` is:

```
-dL/dF = y_i - F(x_i)
```

That is exactly the residual. Fitting a tree to the residuals is fitting a tree to the
negative gradient of the loss. The ensemble update rule, `F_m = F_{m-1} + lr * h_m`, is
a gradient descent step: not in the space of model weights (as in Module 2's linear
regression), but in the space of functions. You are descending the loss surface by adding
a function that locally points downhill.

Module 2 showed you gradient descent with a fixed parametric form (a line). Gradient
boosting lifts the same idea to a non-parametric setting: the model is an additive sum of
trees, and each tree is chosen to reduce the loss as much as a shallow learner can in one
step. The learning rate plays the same role as the step size in parameter-space gradient
descent; too large and you overshoot, too small and convergence is slow.

This generalization is what makes gradient boosting powerful for arbitrary loss functions.
Swap the loss and you swap only the residual formula; the tree-fitting and update
mechanics stay identical. The Azure Machine Learning designer's Boosted Decision Tree
Regression component builds on exactly this algorithm: its documentation describes how
"the algorithm learns by fitting the residual of the trees that preceded it" using the
MART gradient boosting algorithm, backed by LightGBM. The Two-Class Boosted Decision Tree
component uses the same sequential residual-fitting mechanics for classification by
reducing it to regression with a suitable loss. See the
[Boosted Decision Tree Regression component reference](https://learn.microsoft.com/azure/machine-learning/component-reference/boosted-decision-tree-regression?view=azureml-api-2)
and the
[Two-Class Boosted Decision Tree component reference](https://learn.microsoft.com/azure/machine-learning/component-reference/two-class-boosted-decision-tree?view=azureml-api-2)
for the designer-level knobs (number of trees, learning rate, leaves per tree), which map
one-to-one onto `n_estimators`, `learning_rate`, and `max_depth` in the code below.

## The Code

Two classes go in. First, add `DecisionTreeRegressor` to `exercises/ml/tree.py`. This is
the M4 addition to that file: a regressor that splits on variance reduction and predicts
the mean of the target values in each leaf. The impurity functions from Module 3 already
handle classification; `DecisionTreeRegressor` uses the same greedy axis-aligned split
search, but the gain criterion is weighted MSE, not Gini or entropy.

```python
# ---------------------------------------------------------------------------
# Regressor node + tree (added M4)
# ---------------------------------------------------------------------------

@dataclass
class _NodeReg:
    """A node in a regression tree. Either an internal split or a leaf."""
    feature: Optional[int] = None
    threshold: Optional[float] = None
    left: Optional["_NodeReg"] = None
    right: Optional["_NodeReg"] = None
    # Leaf value: mean of target in the region
    value: Optional[float] = None

    @property
    def is_leaf(self) -> bool:
        return self.value is not None


class DecisionTreeRegressor:
    """Greedy, axis-aligned decision tree regressor.

    Split criterion: variance reduction (weighted MSE). A leaf predicts the mean
    of the training targets that fell into it.

    Parameters
    ----------
    max_depth : int or None
        Maximum depth of the tree. None means grow until too few samples remain.
    min_samples_split : int
        Do not split a node that has fewer than this many samples.
    """

    def __init__(
        self,
        max_depth: Optional[int] = None,
        min_samples_split: int = 2,
    ):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root_: Optional[_NodeReg] = None

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DecisionTreeRegressor":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        self.root_ = self._grow(X, y, depth=0)
        return self

    def _grow(self, X: np.ndarray, y: np.ndarray, depth: int) -> _NodeReg:
        n_samples, n_features = X.shape

        # Stopping conditions -> leaf
        too_small = n_samples < self.min_samples_split
        at_max = (self.max_depth is not None) and (depth >= self.max_depth)

        if too_small or at_max:
            return _NodeReg(value=float(np.mean(y)))

        # Find the best split by maximum variance reduction
        parent_var = float(np.var(y)) * n_samples   # proportional to MSE * n

        best_reduction = -1.0
        best_feat: Optional[int] = None
        best_thresh: Optional[float] = None

        for feat in range(n_features):
            col = X[:, feat]
            unique_vals = np.unique(col)
            if len(unique_vals) < 2:
                continue
            thresholds = (unique_vals[:-1] + unique_vals[1:]) / 2.0

            for thresh in thresholds:
                mask = col <= thresh
                left_y, right_y = y[mask], y[~mask]
                if len(left_y) == 0 or len(right_y) == 0:
                    continue
                # Weighted MSE of children
                child_var = (
                    float(np.var(left_y)) * len(left_y)
                    + float(np.var(right_y)) * len(right_y)
                )
                reduction = parent_var - child_var
                if reduction > best_reduction:
                    best_reduction = reduction
                    best_feat = feat
                    best_thresh = thresh

        # No beneficial split -> leaf
        if best_feat is None or best_reduction <= 0.0:
            return _NodeReg(value=float(np.mean(y)))

        mask = X[:, best_feat] <= best_thresh
        left_node = self._grow(X[mask], y[mask], depth + 1)
        right_node = self._grow(X[~mask], y[~mask], depth + 1)

        return _NodeReg(
            feature=best_feat,
            threshold=best_thresh,
            left=left_node,
            right=right_node,
        )

    # ------------------------------------------------------------------
    # predict
    # ------------------------------------------------------------------

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        return np.array([self._traverse(self.root_, row) for row in X])

    def _traverse(self, node: _NodeReg, row: np.ndarray) -> float:
        if node.is_leaf:
            return node.value
        if row[node.feature] <= node.threshold:
            return self._traverse(node.left, row)
        return self._traverse(node.right, row)
```

The gain criterion is the only structural difference from `DecisionTreeClassifier`. Where
the classifier measured Gini or entropy, `_grow` here computes `parent_var - child_var`,
where each variance term is scaled by sample count. Maximum variance reduction is
equivalent to minimizing weighted child MSE: the split that explains the most variance
wins.

Second, add `GradientBoostingRegressor` to `exercises/ml/ensemble.py`. It imports
`DecisionTreeRegressor` from `ml.tree` alongside `DecisionTreeClassifier`.

```python
# ---------------------------------------------------------------------------
# GradientBoostingRegressor
# ---------------------------------------------------------------------------

class GradientBoostingRegressor:
    """Gradient boosting for regression (MSE loss), from scratch.

    Builds an additive ensemble of shallow DecisionTreeRegressors:
        F_0(x) = mean(y)
        F_m(x) = F_{m-1}(x) + learning_rate * h_m(x)
    where h_m is fit to the residuals r_m = y - F_{m-1}(x).

    Parameters
    ----------
    n_estimators : int
        Number of boosting rounds.
    learning_rate : float
        Shrinkage applied to each tree's contribution.
    max_depth : int
        Maximum depth for each weak learner.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        learning_rate: float = 0.1,
        max_depth: int = 3,
    ):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth

        self.base_: float = 0.0
        self.estimators_: List[DecisionTreeRegressor] = []
        self.train_losses_: List[float] = []

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------

    def fit(self, X: np.ndarray, y: np.ndarray) -> "GradientBoostingRegressor":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)

        # F_0: constant prediction = mean(y)
        self.base_ = float(np.mean(y))
        current = np.full_like(y, self.base_)

        self.estimators_ = []
        self.train_losses_ = []

        for _ in range(self.n_estimators):
            residuals = y - current

            tree = DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_samples_split=2,
            )
            tree.fit(X, residuals)

            current = current + self.learning_rate * tree.predict(X)

            self.estimators_.append(tree)
            mse = float(np.mean((y - current) ** 2))
            self.train_losses_.append(mse)

        return self

    # ------------------------------------------------------------------
    # predict
    # ------------------------------------------------------------------

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        result = np.full(X.shape[0], self.base_)
        for tree in self.estimators_:
            result = result + self.learning_rate * tree.predict(X)
        return result
```

The `fit` loop is the algorithm made literal. `self.base_` is `F_0`. `current` tracks
`F_m(x)` for the training set. `residuals = y - current` computes the negative gradient.
`current = current + self.learning_rate * tree.predict(X)` is the update step.
`self.train_losses_` stores the per-round training MSE so the acceptance gate can verify
that loss typically decreases each round.

## Measured Results

On the Friedman-1 regression dataset (500 samples, 10 features, `noise=1.0`), with an
80/20 split and `random_state=0`, using `n_estimators=100, learning_rate=0.1, max_depth=3`:

- From-scratch `GradientBoostingRegressor`: test R-squared `0.9038`.
- Scikit-learn `GradientBoostingRegressor` (same hyperparameters): test R-squared
  `0.9045`.
- Pearson correlation between the two on the 100 test samples: `0.9999`.

Training MSE falls monotonically across all 100 rounds. A sample of the descent:

| Round | Training MSE |
|------:|-------------:|
|     1 |        22.57 |
|    10 |         9.39 |
|    50 |         1.21 |
|   100 |         0.47 |

Each round the residuals shrink. By round 100, the training error is about 2% of what
it was at round 1. The agreement with scikit-learn (0.9999 correlation) confirms that
the residual-fitting mechanics are correct.

## What This Cost

Training loss typically decreases each round and is non-increasing in practice on
smooth data, but it is not a strict per-step mathematical guarantee: a round with
shallow trees and a nonzero learning rate can occasionally overshoot before later
rounds correct it. Test error is a different story. Run too many rounds with a high learning rate
and the ensemble memorizes the training set: training MSE keeps falling, test MSE starts
climbing. The learning rate is a regularizer, not just a step size. A smaller rate
demands more trees for the same training error, but the ensemble stays closer to the true
function. That tension is exactly the subject of the next lesson.

## Core Concepts

- Gradient boosting builds an additive ensemble by fitting each new tree to the residuals
  of the current ensemble; for squared-error loss, residuals are the negative gradient of
  the loss with respect to the current prediction.
- The update rule `F_m = F_{m-1} + lr * h_m` is gradient descent in function space: each
  tree is a step downhill on the loss surface, with `learning_rate` playing the role of
  step size.
- Training MSE typically decreases each round and is non-increasing in practice on smooth
  data, but a strict per-step decrease is not guaranteed; test error can increase if
  learning rate is too high or rounds are too many.
- A from-scratch `GradientBoostingRegressor` and scikit-learn's equivalent agree to a
  Pearson correlation of 0.9999 on the Friedman-1 test set, confirming the residual loop
  is mechanically correct.

<div class="claude-handoff" data-exercise="exercises/module4/boosting-and-the-gradient/">

**Build It in Claude Code**: Read the current state of `exercises/ml/tree.py` and
`exercises/ml/ensemble.py` before touching anything. Module 3 placed
`DecisionTreeClassifier` in `ml/tree.py`; the previous M4 lesson placed
`RandomForestClassifier` in `ml/ensemble.py`. You are adding two things: append
`_NodeReg` and `DecisionTreeRegressor` to `exercises/ml/tree.py`, then add
`GradientBoostingRegressor` to `exercises/ml/ensemble.py`. The regressor imports
`DecisionTreeRegressor` from `ml.tree`; do not copy the class. Implement both exactly as
shown above. Then verify with the locked acceptance gate at
`exercises/module4/boosting-and-the-gradient/test_boosting.py`. Note: the gate runs
several hundred from-scratch trees; expect a minute or two. Done when
`python -m pytest exercises/module4/boosting-and-the-gradient` is green.

</div>
