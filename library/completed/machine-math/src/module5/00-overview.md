# Module 5: What "Good" Means

Modules 1 through 4 taught you to build models. Module 5 asks whether a model is good,
and good at what. Those are different questions, and the difference matters more than
most practitioners realize until their first production incident.

## The Problem With a Single Number

A model that predicts the majority class on a 95/5 imbalanced dataset scores 95% accuracy
while correctly classifying zero positive examples. Accuracy looked fine. The model was
useless. A single accuracy number does not tell you which mistakes the model is making,
how costly those mistakes are, or whether moving the decision threshold would trade one
kind of error for another. The three lessons in this module replace that single number
with a complete picture.

## Three Lessons

**The Confusion Matrix and Thresholds** starts where every classifier ends: a probability.
A threshold on that probability produces a hard prediction and a confusion matrix with
four cells. Those four cells contain everything: true positives, true negatives, false
positives, and false negatives. Precision reads one tradeoff from the matrix; recall reads
another. F1 balances them. The lesson shows exactly how the matrix changes as the threshold
moves and why accuracy lies when classes are imbalanced.

**AUC-ROC: The Math of Ranking** lifts the question above any single threshold. Instead
of asking "did the model predict the right label at tau = 0.5?", it asks "does the model
rank positives above negatives?" AUC measures that ranking quality across all possible
thresholds in a single number. The lesson derives the rank-based Mann-Whitney form, which
is the exact equivalent of the trapezoidal area under the ROC curve.

**Regression Error and Slicing** closes the module for continuous targets. MAE, RMSE, and
R-squared each ask a different question about prediction error. Slicing breaks those
aggregate numbers open: a model with fine aggregate RMSE can still fail on a minority
subgroup, and you will only find the failure if you compute the metric per slice.

## The Shared Artifact

All three lessons extend a single file: `exercises/ml/metrics.py`. This is the
from-scratch evaluation library you will build incrementally across the module. By the
end, it contains classification metrics, ROC utilities, regression metrics, and a
`slice_metric` function that composes any metric over arbitrary data subgroups. The M7
capstone imports `ml.metrics` directly to grade a real model against a rubric expressed
in code: what you build here is what grades you later.

## What Is Given

Scikit-learn is the oracle. Every acceptance gate compares your from-scratch metric to
scikit-learn's equivalent on the same data; they must agree to floating-point or near
floating-point tolerance. NumPy handles all array arithmetic. No other dependencies are
introduced.

## What Is Deliberately Out of Scope

**Feature engineering** is held for Module 6. All inputs here are clean numeric features.
Multi-class averaging (macro, micro, weighted) is deferred; the module covers binary
classification and scalar regression. Calibration curves and probability calibration are
out of scope.
