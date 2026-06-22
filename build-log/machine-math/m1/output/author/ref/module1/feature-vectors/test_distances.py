"""Acceptance gate for the feature-vectors exercise.

The from-scratch metrics must agree with scikit-learn's reference implementations, and the two scalers
must do what they claim. scikit-learn is the oracle only; the math under test is yours, in ml/distances.py.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from sklearn.metrics.pairwise import (
    euclidean_distances,
    manhattan_distances,
    cosine_distances,
)

from ml.distances import euclidean, manhattan, cosine_distance, minmax_scale, zscore

A = np.array([5.1, 3.5, 1.4, 0.2])
B = np.array([6.7, 3.0, 5.2, 2.3])


def test_euclidean_matches_sklearn():
    assert np.isclose(euclidean(A, B), euclidean_distances([A], [B])[0, 0])


def test_manhattan_matches_sklearn():
    assert np.isclose(manhattan(A, B), manhattan_distances([A], [B])[0, 0])


def test_cosine_matches_sklearn():
    assert np.isclose(cosine_distance(A, B), cosine_distances([A], [B])[0, 0])


def test_cosine_zero_vector_raises():
    try:
        cosine_distance(np.zeros(4), B)
    except ValueError:
        return
    raise AssertionError("cosine_distance must raise ValueError on a zero-magnitude vector")


def test_minmax_scale_hits_unit_interval():
    X = np.array([[20.0, 20000.0], [80.0, 200000.0], [50.0, 110000.0]])
    Xs = minmax_scale(X)
    assert np.allclose(Xs.min(axis=0), 0.0)
    assert np.allclose(Xs.max(axis=0), 1.0)


def test_zscore_standardizes():
    X = np.random.RandomState(0).rand(64, 3) * 100.0
    Xs = zscore(X)
    assert np.allclose(Xs.mean(axis=0), 0.0, atol=1e-9)
    assert np.allclose(Xs.std(axis=0), 1.0, atol=1e-9)
