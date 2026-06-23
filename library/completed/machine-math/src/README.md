# Machine Math

Classic machine learning, paired with the math each fundamental requires.

Most ML courses split into two failure modes. One teaches algorithms as library calls: import the
classifier, fit it, read the accuracy, never see the machinery. The other teaches the math as a
sequence of proofs with no algorithm attached, abstraction for its own sake. The first leaves you
with a black box you cannot reason about. The second leaves you with notation you cannot apply.

This book refuses both. Every mathematical idea here arrives bolted to the classic-ML algorithm that
needs it. You learn the dot product when k-nearest-neighbors needs it to measure similarity. You
learn the derivative and the convex loss surface when gradient descent needs them to fit a line. You
learn entropy and information gain when a decision tree needs them to choose a split. You learn the
log-likelihood when logistic regression needs it, and the math of ranking when AUC-ROC needs it. The
math and the fundamental complete each other, and the title names that pairing directly.

## Who This Is For

A reader who has finished Sans Python has production AI engineering covered: LLM applications, agents,
retrieval, fleets, deploy. This book adds the layer the ML-system-design interview tests and that
production feature work quietly assumes: the classic-ML intuition and the math fluency an interviewer
expects you to have. It is not a prerequisite for Sans Python. It is the complement for the engineer
who wants the full surface area of the AI Engineer screen.

The depth is applied, not academic. The goal is conceptual fluency: the ability to reason about what
an algorithm does, why a metric behaves the way it does, and what assumptions break on a given
dataset. From-scratch derivation for its own sake is out of scope. So is the neural network. PyTorch,
deep-model training, and fine-tuning belong to a separate book ("Weights and Measures"); this one ends
where the neural network begins.

## What You Will Build

The book closes on a portfolio artifact that makes the math visible: a complete classic-ML pipeline on
a real tabular dataset. You write the feature engineering by hand, train a gradient-boosted classifier,
and evaluate it honestly with AUC-ROC, F1, and slice metrics across subgroups. Then you write a model
card that maps each result back to the math that explains it. The math is not hidden in a library call;
you annotate the loss curve, plot the decision boundary, and read the confusion matrix against the AUC.
It is a runnable, reviewable, GitHub-postable proof, in the mold of the Sans Python capstones.

## How to Read This Book

Work the modules in order. Each one pairs a cluster of fundamentals with the math it requires, and each
ends with a "Build It in Claude Code" exercise that turns the lesson into runnable code. The exercises
compound: the geometry you build in Module 1 is the same geometry the evaluation metrics measure in
Module 5 and the portfolio artifact reports in the finale.
