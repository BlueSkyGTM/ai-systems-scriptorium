# Naive Bayes for Classification

**Provenance:** vault/ai-engineering-from-scratch/phases/02-ml-fundamentals/14-naive-bayes/docs/en.md (+ code/naive_bayes.py)

**Scope:** Distilled from the AEFS "Naive Bayes" lesson (75-minute build). Covers Bayes for classification, the independence assumption, Gaussian and multinomial variants, Laplace smoothing, and the fast log-space prediction pipeline.

## Bayes for Classification

Bayes' theorem in classification form:

```
P(class | features) = P(features | class) * P(class) / P(features)
```

Rearranged for ranking (since P(features) is constant across classes):

```
P(class | features) proportional to P(features | class) * P(class)
```

Terms:
- P(class | features): posterior, what we predict
- P(features | class): likelihood, how common these features are in this class
- P(class): prior, base rate of the class
- P(features): evidence (omitted in ranking)

The class with the highest posterior wins. No probability calibration required; ranking is sufficient.

## The Naive Assumption

The core trick: computing the joint likelihood P(features | class) exactly is intractable. With n features, there are 2^n possible combinations.

**The independence assumption:** all features are conditionally independent given the class.

```
P(w1, w2, ..., wn | class) = P(w1 | class) * P(w2 | class) * ... * P(wn | class)
```

Instead of one impossible joint, estimate n simple per-feature distributions.

**Why the assumption is wrong:** feature correlations are real. "Machine" and "learning" are not independent in any natural corpus.

**Why it works anyway:** three mechanisms:

1. **Ranking over calibration.** NB produces wrong probabilities but correct orderings. P(spam) = 0.99999 when true is 0.7 still ranks spam first. Classification needs the top rank, not accuracy on the probability scale.

2. **High bias, low variance.** The independence prior constrains the model heavily, preventing overfitting on small datasets. A slightly wrong stable model beats a theoretically correct volatile one; this is the bias-variance tradeoff in action.

3. **Redundancy cancels out.** Correlated features provide overlapping evidence. NB double-counts them (once per feature), but counts them twice for the correct class too. The systematic error does not change the ranking.

**Practical win:** NB trains in one pass through the data (just counts), scales to millions of features, and predicts via matrix multiplication. Iteration is fast enough to offset theoretical disadvantages.

## Gaussian Naive Bayes

For continuous features, assume each feature follows a Gaussian distribution within each class.

**Fit phase (per class, per feature):** estimate mean and variance from training data.

```
mu_c_i = mean of feature i in class c
sigma_sq_c_i = variance of feature i in class c
```

**Likelihood formula (Gaussian PDF):**

```
P(x_i | class) = (1 / sqrt(2 * pi * sigma_sq)) * exp(-(x_i - mu)^2 / (2 * sigma_sq))
```

**Prediction in log space (avoids underflow):** for a new sample, compute log-posterior for each class:

```
log P(class | sample) = log P(class) + sum_i log P(x_i | class)

where log P(x_i | class) = -0.5 * log(2 * pi * sigma_sq) - 0.5 * (x_i - mu)^2 / sigma_sq
```

Sum the log-prior and log-likelihoods. Argmax over classes.

**Smoothing for zero variance:** add a small constant (typically 1e-9) to all variances. Without it, zero-variance features (all samples identical) divide by zero.

## Variants and Smoothing

### Multinomial Naive Bayes

For count or frequency data (bag-of-words, TF-IDF, word counts).

```
P(word_i | class) = (count(word_i, class) + alpha) / (total_words_in_class + alpha * vocab_size)
```

Alpha is Laplace smoothing. Predicts via log matrix multiplication: `X @ log_feature_probs.T + log_priors`.

**When to use:** text classification, email spam detection, topic modeling.

### Bernoulli Naive Bayes

For binary features (word present/absent), explicitly penalizes absence.

```
P(word_i | class) = (docs in class with word_i + alpha) / (total docs in class + 2 * alpha)
```

Unlike Multinomial, word absence contributes negative evidence. If "free" typically appears in spam but is absent here, Bernoulli counts that as evidence against spam.

**When to use:** short text (SMS, tweets), binary feature vectors.

### Laplace Smoothing

**Problem:** if a feature never appeared in training for a class, its raw probability is 0. One zero in the product wipes out all other evidence.

**Solution:** add a small count alpha (usually 1) to every feature count.

```
P(feature | class) = (count + alpha) / (total + alpha * n_features)
```

Every feature gets a nonzero floor probability. Unseen features no longer destroy predictions.

**Tuning:** alpha is a hyperparameter.
- alpha=0.001: minimal smoothing, trust the data (large training sets)
- alpha=0.1: light smoothing
- alpha=1.0: standard Laplace (default)
- alpha=10.0: heavy smoothing (very small datasets, many unseen features expected)

Higher alpha flattens the distributions toward uniform.

## Source Code Shape

**File:** vault/ai-engineering-from-scratch/phases/02-ml-fundamentals/14-naive-bayes/code/naive_bayes.py

**MultinomialNB class:**
- `fit(X, y)`: for each class, sum feature counts with Laplace smoothing; store log-priors and log-feature-probabilities
- `predict_log_proba(X)`: matrix multiply X by transposed log-feature-probs, add log-priors (the core operation)
- `predict(X)`: argmax of log-posteriors
- `score(X, y)`: accuracy on held-out data

**GaussianNB class:**
- `fit(X, y)`: for each class, compute per-feature mean, variance (+ 1e-9 smoothing), and class prior
- `_log_likelihood(X)`: vectorized Gaussian PDF evaluation; for each sample and class, sum log-likelihoods across features, add log-prior
- `predict(X)`: argmax of log-likelihoods
- `predict_proba(X)`: normalize likelihoods to probabilities using log-sum-exp trick

Both classes accept sklearn-style (n_samples, n_features) input and output (n_samples,) or (n_samples, n_classes) predictions.

**Demo functions:** generate synthetic text (bag-of-words with Poisson counts) and continuous (Iris-like Gaussian clusters) data. Run train-test split, fit both variants, measure accuracy, compare alpha values, and compute per-class precision/recall/F1.

## Worked Numeric Examples

**Multinomial NB text example (from lesson):**

Training data: 3-word vocabulary ("free", "money", "meeting"), 2 classes (spam, not-spam).

Counts:
- Spam: "free" 80, "money" 60, "meeting" 10 (150 words total); 40% class prior
- Not-spam: "free" 5, "money" 10, "meeting" 100 (115 words total); 60% class prior

With Laplace smoothing (alpha=1):

```
P(free | spam) = (80 + 1) / (150 + 3) = 81/153 = 0.529
P(money | spam) = (60 + 1) / (150 + 3) = 61/153 = 0.399
P(meeting | spam) = (10 + 1) / (150 + 3) = 11/153 = 0.072

P(free | not-spam) = (5 + 1) / (115 + 3) = 6/118 = 0.051
P(money | not-spam) = (10 + 1) / (115 + 3) = 11/118 = 0.093
P(meeting | not-spam) = (100 + 1) / (115 + 3) = 101/118 = 0.856
```

Test email: "free" (2 times), "money" (1 time), "meeting" (0 times).

Log-posteriors:

```
log P(spam | email) = log(0.4) + 2*log(0.529) + 1*log(0.399) + 0*log(0.072)
                    = -0.916 + 2*(-0.637) + (-0.919) + 0
                    = -3.109

log P(not-spam | email) = log(0.6) + 2*log(0.051) + 1*log(0.093) + 0*log(0.856)
                        = -0.511 + 2*(-2.976) + (-2.375) + 0
                        = -8.838
```

Prediction: spam (higher log-posterior by 5.729 nats). Word "free" appearing twice is strong class-specific evidence. Word "meeting" absent contributes zero (0 * log(P)) in multinomial.

**Gaussian NB numeric details (from code demo):**

Code generates 450 continuous samples, 3 classes, 4 features (Iris-like).

Class 0: mean [5.0, 3.4, 1.4, 0.2], variance diag [0.12, 0.14, 0.03, 0.01]
Class 1: mean [5.9, 2.8, 4.3, 1.3], variance diag [0.27, 0.10, 0.22, 0.04]
Class 2: mean [6.6, 3.0, 5.6, 2.0], variance diag [0.40, 0.10, 0.30, 0.08]

Each class gets distinct cluster center and spread. For prediction, Gaussian PDF is evaluated at each (sample, feature, class) triple, summed in log space, and argmaxed. No calibration; ranking determines class.

Typical achieved accuracy on 80/20 train-test split: 0.95+.

## Connection to Feature Engineering and Speed

**Why NB is fast:**

Training is a single pass: accumulate counts (or means/variances). No optimization, no iteration. Time: O(n_samples * n_features).

Prediction is matrix multiplication (multinomial) or vectorized Gaussian PDF evaluation (Gaussian). Both are linear in every dimension: O(n_test * n_features * n_classes). Compare to KNN (O(n_test * n_train * n_features)) or SVM with nonlinear kernel (O(n_test * n_support_vectors * n_features)).

**Sensitivity to feature quality and correlation:**

NB assumes independence but does not verify it. If features are highly correlated but evidence is opposing, NB sees conflicting signals where there is none. Example: features A and B always agree in reality, but the model learns to favor A for one class and B for another. The double-counting of redundant evidence can hurt rankings.

However, text features (thousands of weak, individual words) rarely trigger this failure mode. Redundant words provide overlapping evidence that cancels in the ranking. NB shines when features are numerous, individually weak, and feature engineering is cheap (tokenization + vocabulary are O(n)).

The bias-variance tradeoff shifts with data volume: NB wins on small datasets (strong prior); logistic regression wins on large datasets (flexible boundary).

## Out of Scope / Hold for Later

- Feature selection and dimensionality reduction for NB (not covered; assume features are pre-selected)
- Probability calibration methods (CalibratedClassifierCV mentioned but not detailed)
- Mixture of Gaussians (multimodal within-class distributions)
- Kernel density estimation (continuous feature likelihood alternative to Gaussian assumption)
- Comparing NB to logistic regression on the same data (cross-model analysis; see lesson for rule-of-thumb)
- Handling missing values in NB
- Online / streaming learning (incremental NB fit)
- Negative feature values in multinomial variant and workarounds
