"""ml/features.py -- feature engineering utilities, from scratch in NumPy.

Six tools housed here:

1. one_hot_encode      -- nominal -> binary indicator columns
2. ordinal_encode      -- ordered categorical -> integer codes
3. random_oversample   -- balance classes by upsampling the minority
4. random_undersample  -- balance classes by downsampling the majority
5. class_weights       -- inverse-frequency weights for cost-sensitive learning
6. select_by_variance  -- drop near-constant columns
7. select_by_importance -- keep top-k features ranked by forest split frequency

Scaling (zscore / minmax_scale) is imported from ml.distances; no reimplementation.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np

from ml.distances import zscore, minmax_scale  # re-export so callers can import from here too


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Resampling
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Class weights
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Feature selection
# ---------------------------------------------------------------------------

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
