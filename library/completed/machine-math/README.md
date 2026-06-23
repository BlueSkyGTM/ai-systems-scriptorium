# Machine Math — Blueprint

## Positioning

Sans Python covers the AI engineering stack from first LLM call through governed multi-agent fleets.
It does this deliberately without making classical ML or its underlying math the subject. Two rows of
the antilibrary gap report mark the result: row 3 (classic ML fundamentals, part of the ML-system-design
48% screen) and row 6 (ML math depth, the linear algebra / calculus / probability layer). This book fills
both rows together, because they belong together.

This book sits one step beyond Sans Python on the ML-adjacent track: a reader who finishes Sans Python
has production AI engineering covered; this book adds the classic-ML intuition and math fluency that the
ML-system-design interview tests and that production feature work quietly assumes. It is not a
prerequisite for Sans Python. It is the complement for the engineer who wants the full surface area of
the 2026 AI Engineer screen.

PyTorch, deep-model training, and fine-tuning are out of scope. They belong to a separate planned book
("Tasteful Tuning"). The split is intentional: conflating classic-ML fundamentals with deep-learning
training blurs the seam and makes both weaker. This book ends where the neural network begins.

## Thesis

Math bolted to the fundamental that needs it. Every mathematical idea in this book arrives in the
context of the classic-ML algorithm or concept that requires it: you learn the dot product when you need
it for linear regression, the chain rule when you need it for gradient descent, the log-likelihood when
you need it for logistic regression, the Gini impurity when you need it for decision trees. Math taught
without a fundamental attached is pure abstraction; a fundamental taught without its math is a black box.
This book refuses both: the two halves complete each other, and the title "Machine Math" names that
pairing directly.

The depth is applied, not academic. The goal is conceptual fluency for the ML-system-design interview
and for production feature work: the ability to reason about what an algorithm does, why a metric
behaves a certain way, and what assumptions break in a given dataset. From-scratch derivation for its
own sake is out of scope.

## Scope

**In scope:**

- Classic supervised learning: linear regression, logistic regression, decision trees, SVMs, k-NN,
  naive Bayes, ensemble methods (random forests, gradient boosting / XGBoost / LightGBM)
- Classic unsupervised learning: k-means clustering, dimensionality reduction (PCA, SVD), anomaly
  detection
- Feature engineering: encoding, scaling, selection, imbalanced-data handling
- Model evaluation: bias-variance tradeoff, cross-validation, AUC-ROC, precision-recall, F1,
  MAE / RMSE, slicing metrics
- ML pipelines: train / eval / serve loop, hyperparameter tuning (the concept, not the deep-learning
  variant), time-series fundamentals
- The math each fundamental requires: vectors and matrices (regression, PCA), derivatives and the chain
  rule (gradient descent), probability and Bayes (logistic regression, naive Bayes), information theory
  (decision trees, entropy / Gini), optimization (convex loss surfaces), distributions and sampling
  (evaluation, imbalanced data)

**Deliberately out of scope:**

- PyTorch / TensorFlow, neural network training, fine-tuning, LoRA: that is the "Tasteful Tuning" book
- From-scratch deep-learning math (backpropagation through layers, attention math): same
- Pure math chapters with no fundamental attached (e.g., a Fourier transform lesson with no ML hook)
- Model-from-scratch distributed training, pre-training at scale
- Generative media, computer vision, speech: wrong seam entirely

[MS-Learn: Azure ML designer ships every classic algorithm (linear regression, boosted decision tree,
decision forest, logistic regression, SVM, k-means) as a named component with documented hyperparameters,
loss functions, and evaluation metrics. AUC is the primary classification metric across Azure AutoML.
Sources: component-reference, how-to-understand-automated-ml, optimize-model-performance-roc-auc module.]

## Ore

Two source repos carry the raw material. Both are in `vault/` (not yet distilled) and surveyed at
process-ore time via `vault/MANIFEST.md`.

| Ore repo | Prefix | What it holds for this book |
|---|---|---|
| `ai-engineering-from-scratch` | `aefs` | Phase 01 (Math Foundations: linear algebra, calculus, probability, optimization, statistics for ML, dimensionality reduction, SVD) + Phase 02 (ML Fundamentals: regression, trees, SVMs, k-NN, feature engineering, model evaluation, ensemble methods, pipelines) |
| `made-with-ml` | `mwml` | Classic-ML notebook and evaluation pipeline (data, evaluate.py, predict.py); the antilibrary for mwml (train.py, models.py, tune.py) is PyTorch-training internals, correctly excluded |

### Ore to module map

| Phase / file | Module feed |
|---|---|
| `aefs` Phase 01 lessons 01-08 (linear algebra through optimization) | M1, M2, M3 (math paired with each fundamental) |
| `aefs` Phase 01 lessons 09-18 (info theory, dimensionality reduction, SVD, statistics for ML, sampling) | M3, M4, M5 |
| `aefs` Phase 02 lessons 01-10 (what-is-ML through bias-variance) | M1, M2, M3 |
| `aefs` Phase 02 lessons 11-18 (ensemble methods through feature selection) | M4, M5, M6 |
| `mwml` evaluate.py, data.py, holdout dataset | M5 (evaluation), M7 (portfolio artifact) |
| `mwml` notebook (data → eval sections; training sections are antilibrary) | M6, M7 |

## Curriculum Arc

Six content modules plus a portfolio artifact module. Each module pairs one cluster of fundamentals
with the math it requires.

**Module 1: The Shape of Data**
Vectors, matrices, and distance. The math of "what does a feature space look like?" Paired with: k-NN,
basic classification, and the geometry of similarity.

**Module 2: Fitting a Line (and Its Limits)**
Derivatives, gradient descent, and the convex loss surface. Paired with: linear regression, logistic
regression, and the bias-variance tradeoff.

**Module 3: Splitting and Branching**
Information theory: entropy, Gini impurity, information gain. Paired with: decision trees and the
intuition behind recursive partitioning. Cross-validation and overfitting enter here.

**Module 4: Ensembles and the Gradient**
The ensemble idea: bagging vs. boosting. The chain rule applied to residuals. Paired with: random
forests, gradient boosting (XGBoost / LightGBM), and hyperparameter tradeoffs.
[MS-Learn: Azure ML Boosted Decision Tree Regression is LightGBM-backed; MART gradient boosting
algorithm documented in component reference.]

**Module 5: What "Good" Means**
Probability, distributions, and threshold reasoning. Paired with: AUC-ROC (the math of ranking), F1
and precision-recall (the math of class imbalance), MAE / RMSE (the math of regression error), and
slicing metrics (the math of failure modes).
[MS-Learn: AUC_macro / AUC_micro / AUC_weighted / AUC_binary all documented in Azure AutoML evaluation
reference. ROC curve module on MS Learn: optimize-model-performance-roc-auc.]

**Module 6: Feature Reality**
Scaling, encoding, selection, and the imbalanced-data problem. The math of normalization, one-hot
encoding, and sampling strategies. Paired with: end-to-end feature engineering pipeline and naive Bayes
(the probability model that breaks without good features).

**Module 7: The Portfolio Artifact**
Build a from-the-fundamentals ML system: a real dataset, manual feature engineering, a gradient
boosted classifier, honest evaluation (AUC-ROC, F1, slicing metrics by subgroup), and a written
"model card" explaining the math visible in each result. The math is not hidden in a library call: the
reader annotates the loss curve, plots the decision boundary, and reads the confusion matrix against
the AUC. Mirrors Sans Python M6/7/8: a runnable, reviewable, GitHub-postable artifact that proves the
skill.

## Portfolio Artifact Strategy

Sans Python M6/7/8 are the benchmark. Each artifact there is a production-grade runnable system
(terminal coding agent, production RAG chatbot, governed multi-agent fleet) that proves skills an
interviewer can see on GitHub.

The Machine Math equivalent: a complete ML pipeline that makes the math visible. The target is a real
tabular dataset (public, non-trivial: e.g., the UCI Adult Income or Titanic variant), with:

- Manual feature engineering (the reader writes the pipeline, not AutoML)
- A gradient boosted classifier (scikit-learn + LightGBM) with annotated hyperparameter choices
- AUC-ROC plot with interpretation written into a markdown cell: "the curve dips here because..."
- Slice evaluation across at least two subgroups
- A model card (markdown) that maps each metric back to the math introduced in M5

The artifact is a Jupyter notebook or structured Python + markdown package, runnable end-to-end with
one command. The Claude Code exercise at the end of M7 is: "reproduce the evaluation, add a third
slice, and update the model card."

This is the proof. Not a description of gradient boosting: a gradient boosted model, evaluated
honestly, with the math annotated by the reader.

## Dual-Use Note

Like every book in this library, Machine Math is written to be read by a human learner and ingested by
an LLM. Prose is dense and precise; every claim is specific; no padding. An LLM using this book as
context for answering ML-system-design questions should be able to cite the relevant math and the
relevant fundamental in the same sentence, because this book stores them adjacent to each other.

## Candidate Names (GATE-NAME-BOOK)

Propose the real title at the GATE-NAME-BOOK gate. Three candidates; lead is listed first.

**Machine Math** (lead candidate) — the explicit pairing of the two halves: classic machine learning
("machine") and the math it requires ("math"). Short, memorable, and precise. An interviewer who hears
"I worked through a book called Machine Math" knows immediately what it covers. No jargon, no hedge.

**The Math in the Middle** — foregrounds the thesis: the math sits in the middle of the fundamental,
not before it and not after it. Slightly more poetic; less googleable.

**Proportional ML** — references the original working-title framing ("in proportion") and signals
applied, calibrated coverage rather than academic depth. Accurate but softer; less distinctive than
Machine Math.
