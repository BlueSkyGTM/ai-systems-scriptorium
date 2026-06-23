# Scaling and Encoding

A model is a function that maps numbers to numbers. Every model in this book takes a numeric array as input. Your raw data has a column labeled "neighborhood" with values like "downtown" and "suburbs," and a column labeled "income" with values like 85,000. Neither is ready. Encoding turns the category column into numbers. Scaling puts the income column on the same footing as every other numeric column. Do both before the model sees the data.

## Why Models Cannot Read Raw Categories

The KNN classifier you built in Module 1 computes Euclidean distance. Distance requires subtraction. You cannot subtract "downtown" from "suburbs." The distance-based models, the gradient-based models, and the linear models all make the same demand: give me numbers. Categories must be encoded before training, and the encoding must match the structure of the category.

Two cases exist. Either the categories have no inherent order (nominal), or they do (ordinal). The right encoding depends on which case you have.

## One-Hot Encoding for Nominal Categories

Color is nominal. There is no ranking between red, blue, and green. One-hot encoding creates one binary column per category. Exactly one column is 1 for each row; all others are 0.

The locked `one_hot_encode` function in `ml/features.py` implements this:

```python
def one_hot_encode(
    col: np.ndarray,
) -> Tuple[np.ndarray, list]:
    """One-hot encode a 1-D categorical column.

    Each unique category gets its own binary column. Category order is
    sorted-unique (lexicographic for strings, numeric for numbers), so the
    mapping is deterministic regardless of data order.

    Parameters
    ----------
    col : array-like, shape (n,)
        Raw categorical values (strings or integers).

    Returns
    -------
    encoded : np.ndarray, shape (n, n_categories)
        Binary matrix; encoded[i, j] == 1 iff col[i] == categories[j].
    categories : list
        The sorted unique categories, one per column of encoded.
    """
    col = np.asarray(col)
    categories = sorted(set(col.tolist()))   # stable sorted order
    n = len(col)
    k = len(categories)
    cat_to_idx = {c: i for i, c in enumerate(categories)}
    encoded = np.zeros((n, k), dtype=int)
    for i, val in enumerate(col):
        encoded[i, cat_to_idx[val]] = 1
    return encoded, categories
```

The categories are sorted, so the mapping is deterministic regardless of the order rows appear in the data. Azure Machine Learning AutoML applies the same approach automatically: its featurization pipeline uses one-hot encoding for low-cardinality categorical features and a hashing variant for high-cardinality ones, as documented in the [Data featurization in AutoML reference](https://learn.microsoft.com/azure/machine-learning/how-to-configure-auto-features?view=azureml-api-1#automatic-featurization).

**Measured:** `one_hot_encode(['red', 'blue', 'green', 'blue', 'red', 'green', 'red'])` produces shape `(7, 3)` with categories `['blue', 'green', 'red']`. The row for 'red' is `[0, 0, 1]`. The row for 'blue' is `[1, 0, 0]`.

**The dummy-variable note:** n categories produce n columns that are linearly dependent (each row sums to 1). Linear models and regularized models sometimes benefit from dropping one column as a baseline to avoid multicollinearity. Decision trees do not care; the split logic is not affected by linear dependence between features.

## Ordinal Encoding for Ordered Categories

Size ratings like "low," "med," "high" have a real ordering. One-hot encoding throws that away. Ordinal encoding preserves it by mapping each category to an integer that respects the rank.

The locked `ordinal_encode` function in `ml/features.py`:

```python
def ordinal_encode(
    col: np.ndarray,
    order: Optional[list] = None,
) -> Tuple[np.ndarray, list]:
    """Encode an ordinal categorical column as integer codes.

    Parameters
    ----------
    col : array-like, shape (n,)
        Raw categorical values.
    order : list or None
        Explicit ordered category list, e.g. ["low", "med", "high"].
        If None, uses sorted-unique order (ties go to lexicographic rank).

    Returns
    -------
    codes : np.ndarray, shape (n,), dtype int
        Integer codes aligned with order_used.
    order_used : list
        The category ordering that was applied.
    """
    col = np.asarray(col)
    if order is None:
        order_used = sorted(set(col.tolist()))
    else:
        order_used = list(order)
    cat_to_code = {c: i for i, c in enumerate(order_used)}
    codes = np.array([cat_to_code[v] for v in col], dtype=int)
    return codes, order_used
```

**Measured:** `ordinal_encode(['high', 'low', 'med', 'low', 'high'], order=['low', 'med', 'high'])` gives `[2, 0, 1, 0, 2]`. "low" maps to 0, "med" to 1, "high" to 2, preserving the ordering you specified.

Use ordinal encoding only when the order is genuine and understood. Assigning integers to nominal categories with ordinal encoding introduces false ordering: if you encode red=0, blue=1, green=2, a linear model learns that green is twice as far from red as blue is. That relationship does not exist.

## Scaling: Putting Columns on the Same Range

Encoding solves the category problem. Scaling solves the magnitude problem. A feature with values from 0 to 100,000 will dominate any distance calculation against a feature with values from 0 to 1. The model does not know that 100,000 and 1 describe equally important quantities in different units. It just sees a number one hundred thousand times larger.

Two scalers were built in Module 1 and live in `ml.distances`. They are re-exported from `ml.features` so callers can import from either location:

```python
from ml.distances import zscore, minmax_scale  # re-export so callers can import from here too
```

Z-score standardization (subtract mean, divide by standard deviation) produces a column with mean 0 and standard deviation 1. Min-max scaling maps every value to the interval [0, 1]. The Azure Machine Learning Normalize Data component applies both as named options in its designer: Zscore and MinMax, with the same formulas as your `ml.distances` implementation. See the [Normalize Data component reference](https://learn.microsoft.com/azure/machine-learning/component-reference/normalize-data?view=azureml-api-2) for the exact formulas in their visual pipeline.

**Which models need scaling:** distance-based models (KNN from Module 1) and gradient-based models (gradient descent from Module 2, logistic regression) are sensitive to feature scale. A feature with large magnitude will dominate distance or gradient updates. Tree-based models (Module 3 decision trees, Module 4 ensembles) are not sensitive to scale; they split on individual feature values and are invariant to monotone transformations of any single feature. Naive Bayes (this module) estimates per-feature distributions independently and does not require scaling.

## Core Concepts

- Models read numbers; encoding turns raw categories into numeric columns before training.
- One-hot encoding suits nominal categories with no ordering: each category becomes its own binary column, and one column is 1 per row.
- Ordinal encoding suits ordered categories: an explicit rank order maps each category to an integer that preserves the ordering.
- Distance-based and gradient-based models require scaling to prevent high-magnitude features from dominating; tree-based models do not.

<div class="claude-handoff" data-exercise="exercises/module6/scaling-and-encoding/">

**Build It in Claude Code**: Read the current state of `exercises/ml/` before touching anything. Earlier modules placed `distances.py`, `knn.py`, `tree.py`, and `ensemble.py` in that package. You are creating `exercises/ml/features.py` and adding `one_hot_encode` and `ordinal_encode` to it. Import `zscore` and `minmax_scale` from `ml.distances` at the top of the file (do not reimplement them). Add the two functions exactly as shown in the lesson. Then verify with the locked acceptance gate at `exercises/module6/scaling-and-encoding/test_encoding.py`. Done when `python -m pytest exercises/module6/scaling-and-encoding` is green.

</div>
