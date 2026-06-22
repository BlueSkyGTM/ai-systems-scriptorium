"""Acceptance gate for the logistic-regression exercise.

The from-scratch LogisticRegression must clear an accuracy floor on breast-cancer (a real
binary dataset) and agree with sklearn.linear_model.LogisticRegression's predictions at
a high rate. sklearn is the oracle; the algorithm is yours.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression as SklearnLR
from sklearn.model_selection import train_test_split

from ml.logreg import LogisticRegression
from ml.distances import zscore


def _split():
    X, y = load_breast_cancer(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)


def _accuracy(pred, truth):
    return float(np.mean(np.asarray(pred) == np.asarray(truth)))


def test_accuracy_floor_on_breast_cancer():
    X_tr, X_te, y_tr, y_te = _split()
    X_tr_s = zscore(X_tr)
    X_te_s = zscore(X_te)
    model = LogisticRegression(lr=0.1, n_iters=1000).fit(X_tr_s, y_tr)
    acc = _accuracy(model.predict(X_te_s), y_te)
    assert acc >= 0.95, f"Accuracy = {acc:.4f} below floor 0.95"


def test_agrees_with_sklearn():
    X_tr, X_te, y_tr, y_te = _split()
    X_tr_s = zscore(X_tr)
    X_te_s = zscore(X_te)

    mine = LogisticRegression(lr=0.1, n_iters=1000).fit(X_tr_s, y_tr).predict(X_te_s)
    # sklearn with high max_iter to ensure convergence on the same scaled data
    ref = SklearnLR(max_iter=1000, random_state=0).fit(X_tr_s, y_tr).predict(X_te_s)

    agreement = float(np.mean(mine == ref))
    assert agreement >= 0.95, f"Label agreement with sklearn = {agreement:.4f} below 0.95"


def test_predict_proba_is_in_unit_interval():
    X_tr, X_te, y_tr, y_te = _split()
    X_tr_s = zscore(X_tr)
    X_te_s = zscore(X_te)
    model = LogisticRegression(lr=0.1, n_iters=1000).fit(X_tr_s, y_tr)
    proba = model.predict_proba(X_te_s)
    assert np.all(proba >= 0.0) and np.all(proba <= 1.0), "predict_proba returned values outside [0, 1]"


def test_loss_history_decreases():
    X_tr, _, y_tr, _ = _split()
    X_tr_s = zscore(X_tr)
    model = LogisticRegression(lr=0.1, n_iters=500).fit(X_tr_s, y_tr)
    history = model.loss_history_
    mid = len(history) // 2
    assert np.mean(history[:mid]) > np.mean(history[mid:]), "Cross-entropy did not decrease over training"
