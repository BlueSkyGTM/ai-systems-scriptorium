"""Distance metrics and feature scaling, from scratch in NumPy.

The three metrics answer three different "how far apart?" questions; the two scalers put every
feature on a common footing so the metric is not hijacked by the largest-range column. These are the
geometry primitives every later algorithm in the package reuses.
"""
import numpy as np


def euclidean(a, b):
    """Straight-line (L2) distance. Use when magnitude matters and features are comparably scaled."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(np.sqrt(np.sum((a - b) ** 2)))


def manhattan(a, b):
    """Sum of absolute per-axis differences (L1). More robust to a single outlier dimension."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(np.sum(np.abs(a - b)))


def cosine_distance(a, b):
    """1 - cosine similarity. Use when direction (proportional pattern) matters and magnitude is noise."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0.0:
        raise ValueError("cosine distance is undefined for a zero-magnitude vector")
    return float(1.0 - np.dot(a, b) / denom)


def minmax_scale(X):
    """Linearly rescale each column to [0, 1]. Constant columns map to 0 (no range to stretch)."""
    X = np.asarray(X, dtype=float)
    lo = X.min(axis=0)
    hi = X.max(axis=0)
    span = np.where(hi - lo == 0.0, 1.0, hi - lo)
    return (X - lo) / span


def zscore(X):
    """Center each column at mean 0, scale to unit standard deviation. Constant columns map to 0."""
    X = np.asarray(X, dtype=float)
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd = np.where(sd == 0.0, 1.0, sd)
    return (X - mu) / sd


# Name -> function, so an algorithm can take a metric by string (a hypothesis about the data).
METRICS = {
    "euclidean": euclidean,
    "manhattan": manhattan,
    "cosine": cosine_distance,
}
