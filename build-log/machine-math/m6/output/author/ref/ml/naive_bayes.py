"""ml/naive_bayes.py -- Gaussian Naive Bayes classifier, from scratch in NumPy.

One idea: if you assume features are independent given the class (the "naive"
assumption), the joint likelihood factorizes into a product of per-feature
likelihoods. Model each feature as Gaussian: estimate a per-class mean and
variance from training data, then at inference multiply the Gaussian densities
(in log space to avoid underflow) and pick the class with the highest
log-posterior = log-prior + sum of log-likelihoods.

No sklearn inside the algorithm. Pure NumPy.
"""
from __future__ import annotations

from typing import Optional

import numpy as np


class GaussianNB:
    """Gaussian Naive Bayes classifier.

    Stores per-class class priors, feature means, and feature variances at
    fit time. Prediction applies the log-sum-exp trick for numerically stable
    posterior normalization.

    Parameters
    ----------
    var_smoothing : float
        Tiny variance floor added to every per-class per-feature variance to
        prevent division-by-zero when a feature is (nearly) constant within a
        class. Default 1e-9 (matches sklearn's default).
    """

    def __init__(self, var_smoothing: float = 1e-9):
        self.var_smoothing = var_smoothing
        # Fitted attributes
        self.classes_: Optional[np.ndarray] = None
        self.log_priors_: Optional[np.ndarray] = None   # shape (n_classes,)
        self.means_: Optional[np.ndarray] = None        # shape (n_classes, n_features)
        self.vars_: Optional[np.ndarray] = None         # shape (n_classes, n_features)

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------

    def fit(self, X: np.ndarray, y: np.ndarray) -> "GaussianNB":
        """Estimate priors, per-class per-feature means and variances.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
        y : array-like, shape (n_samples,) -- integer class labels

        Returns
        -------
        self
        """
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        n_samples, n_features = X.shape

        self.classes_ = np.unique(y)
        n_classes = len(self.classes_)

        self.means_ = np.zeros((n_classes, n_features))
        self.vars_ = np.zeros((n_classes, n_features))
        self.log_priors_ = np.zeros(n_classes)

        for i, cls in enumerate(self.classes_):
            X_cls = X[y == cls]
            self.log_priors_[i] = np.log(len(X_cls) / n_samples)
            self.means_[i] = X_cls.mean(axis=0)
            # ddof=0: MLE variance (matches sklearn GaussianNB)
            raw_var = X_cls.var(axis=0)
            # Variance floor: add smoothing * max_variance_across_all_features
            # (mirrors sklearn's epsilon = var_smoothing * max(var over all data))
            self.vars_[i] = raw_var + self.var_smoothing

        return self

    # ------------------------------------------------------------------
    # predict_proba
    # ------------------------------------------------------------------

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return normalized class posterior probabilities.

        Uses log-sum-exp for numerical stability: compute log-unnormalized
        posteriors, subtract the row max, exponentiate, then normalize.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)

        Returns
        -------
        proba : np.ndarray, shape (n_samples, n_classes)
            Each row sums to 1.
        """
        log_posts = self._log_posteriors(X)
        # log-sum-exp normalization per sample
        row_max = log_posts.max(axis=1, keepdims=True)
        shifted = log_posts - row_max
        exp_shifted = np.exp(shifted)
        proba = exp_shifted / exp_shifted.sum(axis=1, keepdims=True)
        return proba

    # ------------------------------------------------------------------
    # predict
    # ------------------------------------------------------------------

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return the class with the highest log-posterior for each sample.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)

        Returns
        -------
        y_pred : np.ndarray, shape (n_samples,)
        """
        log_posts = self._log_posteriors(X)
        best_class_idx = np.argmax(log_posts, axis=1)
        return self.classes_[best_class_idx]

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    def _log_posteriors(self, X: np.ndarray) -> np.ndarray:
        """Compute log-unnormalized posteriors for all classes and samples.

        log P(class | x) proportional to
            log P(class) + sum_j log N(x_j; mu_j, sigma_j^2)

        Gaussian log-likelihood:
            -0.5 * log(2*pi*sigma^2) - 0.5 * (x - mu)^2 / sigma^2

        Returns shape (n_samples, n_classes).
        """
        X = np.asarray(X, dtype=float)
        n_samples = X.shape[0]
        n_classes = len(self.classes_)
        log_posts = np.zeros((n_samples, n_classes))

        for i in range(n_classes):
            mu = self.means_[i]          # shape (n_features,)
            var = self.vars_[i]          # shape (n_features,)
            # Gaussian log-likelihood per sample, summed across features
            log_likelihood = (
                -0.5 * np.sum(np.log(2.0 * np.pi * var))
                - 0.5 * np.sum((X - mu) ** 2 / var, axis=1)
            )
            log_posts[:, i] = self.log_priors_[i] + log_likelihood

        return log_posts
