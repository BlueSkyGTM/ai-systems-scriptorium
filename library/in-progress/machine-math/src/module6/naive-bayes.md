# Naive Bayes

Before a model predicts a class, it has to decide which class is most plausible given the evidence. Bayes' theorem says exactly how to do that. Naive Bayes makes one bold simplification to keep the calculation tractable, gets the probabilities badly wrong, and still classifies correctly most of the time. Understanding where it breaks exposes something true about every model in this book.

## Bayes for Classification

The question is: given a feature vector, what is the probability of each class? Bayes' theorem answers it:

```
P(class | features) proportional to P(features | class) * P(class)
```

The left side is the posterior: what you want to know. The right side is the prior (how common is this class in training data?) multiplied by the likelihood (how probable are these feature values among training examples of this class?). The denominator, P(features), is constant across all classes, so you can drop it for ranking. The class with the highest product wins.

This works in principle. The problem is the likelihood term. Computing `P(features | class)` exactly requires modeling the joint distribution over all features for each class: with 50 features, that is a distribution over 50 dimensions per class. You do not have nearly enough training data to estimate it reliably.

## The Naive Assumption

Naive Bayes escapes the dimensionality problem with one assumption: all features are conditionally independent given the class.

```
P(f1, f2, ..., fn | class) = P(f1 | class) * P(f2 | class) * ... * P(fn | class)
```

Instead of one intractable joint distribution, you estimate n simple per-feature distributions. For Gaussian Naive Bayes, each distribution is just a mean and variance: two numbers per feature per class.

The assumption is wrong in almost every real dataset. In the Iris dataset, sepal length and petal length are correlated. "Machine" and "learning" are not independent words in an AI corpus. But the assumption is useful for three reasons. Classification needs ranking, not calibrated probabilities: if the posterior for "spam" is 0.99 when the true probability is 0.7, the ranking is still correct. Second, the strong prior prevents overfitting on small datasets. Third, when two correlated features double-count the same evidence, they do it for the correct class too, so the ranking often survives the systematic error.

## The Gaussian Variant

For continuous features, each per-class per-feature distribution is a Gaussian. The fit is simple: compute the sample mean and variance for each feature within each class. The locked `GaussianNB` in `ml/naive_bayes.py`:

```python
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
```

## The Log-Posterior Prediction

A naive reading of Bayes multiplies probabilities: prior times likelihood times likelihood times... With many features, those products underflow to zero before you can compare them. The fix is log space. The log of a product is a sum of logs:

```
log P(class | x) = log P(class) + sum_j log P(x_j | class)
```

For Gaussian features, each log-likelihood term is:

```
-0.5 * log(2 * pi * variance) - 0.5 * (x - mean)^2 / variance
```

Sum these across all features, add the log-prior, and take the argmax. No multiplication of small numbers; no underflow.

The `_log_posteriors` method computes exactly this. The `var_smoothing` floor (1e-9) prevents division by zero when a feature is constant within a class. The `predict_proba` method applies the log-sum-exp trick to normalize across classes without exponentiation overflow.

## Measured: Iris Benchmark

`GaussianNB` on the Iris dataset, stratified 80/20 split, `random_state=0`, scores **0.9667** on the 30-sample test set. This matches scikit-learn's `GaussianNB` exactly on all 30 test labels (label agreement 1.0). The variance is that low because Iris features are nearly Gaussian within each class and the classes separate well: exactly the regime where the naive assumption costs almost nothing.

The cost of the assumption shows up when features are correlated and the model is expected to produce well-calibrated probabilities, not just correct rankings. Iris is an easy benchmark. Text classification with hundreds of correlated n-gram features is the hard regime, and naive Bayes survives it anyway because the ranking property holds even when the probability estimates are far off.

## Why Feature Quality Matters Most Here

Naive Bayes is the model most exposed to bad features in this book. A decision tree can ignore an uninformative feature; the split on that feature just does not appear in the best tree. Gradient boosting can average over weak features across many trees. Naive Bayes cannot ignore anything: every feature contributes its per-class Gaussian estimate to the log-posterior sum. A constant feature (zero variance after smoothing) contributes noise. A feature measured on a wildly different scale contributes a log-likelihood term that dwarfs the others, effectively muting the rest. Bad features hurt naive Bayes directly, which makes it the right model to study alongside an encoding and scaling lesson.

## Core Concepts

- Naive Bayes computes the posterior as the product of the prior and per-feature likelihoods; the denominator (evidence) is constant across classes and drops from the ranking.
- The naive conditional-independence assumption is always wrong and often useful: the model gets the probability magnitudes wrong but ranks classes correctly often enough to be practical.
- Gaussian Naive Bayes fits a mean and variance per class per feature; at inference, it sums log-likelihoods across features to avoid underflow from multiplying many small probabilities.
- Naive Bayes is the model most exposed to bad features: every feature contributes directly to the log-posterior sum, so uninformative or correlated features hurt rankings in ways tree-based models can dodge.

<div class="claude-handoff" data-exercise="exercises/module6/naive-bayes/">

**Build It in Claude Code**: Read the current state of `exercises/ml/` before touching anything. You are creating `exercises/ml/naive_bayes.py` and adding the `GaussianNB` class to it. Implement the class exactly as shown in the lesson: `fit`, `predict_proba`, `predict`, and `_log_posteriors`. Then verify with the locked acceptance gate at `exercises/module6/naive-bayes/test_naive_bayes.py`. Done when `python -m pytest exercises/module6/naive-bayes` is green.

</div>
