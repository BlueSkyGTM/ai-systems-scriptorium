"""k-nearest neighbors, from scratch in NumPy.

A lazy learner: "training" is storing the data; all the work is at prediction time. Every line maps
to one of three steps -- measure distance to every training point, rank, vote. The metric is pluggable
because choosing it is a modeling decision, not a default.
"""
import numpy as np
from collections import Counter

from ml.distances import METRICS


class KNNClassifier:
    def __init__(self, k=5, metric="euclidean"):
        if metric not in METRICS:
            raise ValueError(f"Unknown metric: {metric!r}; choose one of {sorted(METRICS)}")
        self.k = k
        self.metric = metric

    def fit(self, X, y):
        """Store the labeled training set. No parameters are fit; this is the whole 'training' phase."""
        self.X_train = np.asarray(X, dtype=float)
        self.y_train = np.asarray(y)
        return self

    def predict(self, X):
        X = np.asarray(X, dtype=float)
        return np.array([self._predict_one(x) for x in X])

    def _predict_one(self, x):
        distance = METRICS[self.metric]
        distances = [distance(x, row) for row in self.X_train]
        k_idx = np.argsort(distances)[: self.k]
        votes = Counter(self.y_train[i] for i in k_idx)
        return votes.most_common(1)[0][0]
