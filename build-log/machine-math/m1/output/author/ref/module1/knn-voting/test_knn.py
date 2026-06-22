"""Acceptance gate for the knn-voting exercise.

The from-scratch KNNClassifier must agree with scikit-learn on the same split, clear an accuracy floor
on scaled Iris, and -- the point of the module -- show that scaling is not optional: a distorted feature
sinks an unscaled model, and z-scoring recovers it. scikit-learn is the oracle; the algorithm is yours.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

from ml.knn import KNNClassifier
from ml.distances import zscore


def _split():
    X, y = load_iris(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)


def _accuracy(pred, truth):
    return float(np.mean(np.asarray(pred) == np.asarray(truth)))


def test_matches_sklearn_on_iris():
    X_tr, X_te, y_tr, y_te = _split()
    X_tr_s, X_te_s = zscore(X_tr), zscore(X_te)
    mine = KNNClassifier(k=5, metric="euclidean").fit(X_tr_s, y_tr).predict(X_te_s)
    ref = KNeighborsClassifier(n_neighbors=5, metric="euclidean").fit(X_tr_s, y_tr).predict(X_te_s)
    assert np.mean(mine == ref) >= 0.95


def test_accuracy_floor_on_scaled_iris():
    X_tr, X_te, y_tr, y_te = _split()
    pred = KNNClassifier(k=5, metric="euclidean").fit(zscore(X_tr), y_tr).predict(zscore(X_te))
    assert _accuracy(pred, y_te) >= 0.90


def test_scaling_makes_the_vote_fair():
    # Multiply a weak feature (sepal width) by 1000 so raw Euclidean distance is hijacked by it.
    X_tr, X_te, y_tr, y_te = _split()
    distort = np.array([1.0, 1000.0, 1.0, 1.0])
    X_tr_d, X_te_d = X_tr * distort, X_te * distort
    knn = KNNClassifier(k=5, metric="euclidean")
    unscaled = _accuracy(knn.fit(X_tr_d, y_tr).predict(X_te_d), y_te)
    scaled = _accuracy(knn.fit(zscore(X_tr_d), y_tr).predict(zscore(X_te_d)), y_te)
    assert scaled > unscaled


def test_unknown_metric_rejected():
    try:
        KNNClassifier(k=3, metric="hamming")
    except ValueError:
        return
    raise AssertionError("an unknown metric must raise ValueError")
