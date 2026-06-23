"""Acceptance gate: GaussianNB on Iris.

Tests
-----
1. GaussianNB on Iris (stratified 80/20, random_state=0) clears 0.90 test accuracy.
2. GaussianNB label agreement with sklearn.naive_bayes.GaussianNB >= 0.93.
3. predict_proba rows sum to 1 and shape is (n_samples, n_classes).
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB as SklearnGNB

from ml.naive_bayes import GaussianNB


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def iris_split():
    iris = load_iris()
    X, y = iris.data, iris.target
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=0
    )
    return X_train, X_test, y_train, y_test


@pytest.fixture(scope="module")
def fitted_gnb(iris_split):
    X_train, X_test, y_train, y_test = iris_split
    gnb = GaussianNB()
    gnb.fit(X_train, y_train)
    return gnb


@pytest.fixture(scope="module")
def fitted_sk_gnb(iris_split):
    X_train, _, y_train, _ = iris_split
    sk = SklearnGNB()
    sk.fit(X_train, y_train)
    return sk


# ---------------------------------------------------------------------------
# 1. Accuracy floor
# ---------------------------------------------------------------------------

def test_accuracy_floor(iris_split, fitted_gnb):
    _, X_test, _, y_test = iris_split
    y_pred = fitted_gnb.predict(X_test)
    acc = float(np.mean(y_pred == y_test))
    assert acc >= 0.90, f"Expected accuracy >= 0.90, got {acc:.4f}"


# ---------------------------------------------------------------------------
# 2. Label agreement with sklearn
# ---------------------------------------------------------------------------

def test_label_agreement_sklearn(iris_split, fitted_gnb, fitted_sk_gnb):
    _, X_test, _, _ = iris_split
    our_pred = fitted_gnb.predict(X_test)
    sk_pred = fitted_sk_gnb.predict(X_test)
    agreement = float(np.mean(our_pred == sk_pred))
    assert agreement >= 0.93, (
        f"Expected label agreement with sklearn >= 0.93, got {agreement:.4f}"
    )


# ---------------------------------------------------------------------------
# 3. predict_proba shape and row-sum
# ---------------------------------------------------------------------------

def test_predict_proba_shape(iris_split, fitted_gnb):
    _, X_test, _, _ = iris_split
    proba = fitted_gnb.predict_proba(X_test)
    assert proba.shape == (X_test.shape[0], 3), (
        f"Expected shape ({X_test.shape[0]}, 3), got {proba.shape}"
    )


def test_predict_proba_sums_to_one(iris_split, fitted_gnb):
    _, X_test, _, _ = iris_split
    proba = fitted_gnb.predict_proba(X_test)
    row_sums = proba.sum(axis=1)
    np.testing.assert_allclose(row_sums, np.ones(len(row_sums)), atol=1e-9)
