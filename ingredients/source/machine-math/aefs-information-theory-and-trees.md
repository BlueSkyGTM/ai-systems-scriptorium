# AEFS Information Theory and Decision Trees Distillation

**Provenance:** Extracted from vault source:
- `vault/ai-engineering-from-scratch/phases/01-math-foundations/09-information-theory/docs/en.md` (Learn module, ~60 min)
- `vault/ai-engineering-from-scratch/phases/02-ml-fundamentals/04-decision-trees/docs/en.md` (Build module, ~90 min)
- Associated code: `information_theory.py`, `trees.py`

**Target scope:** Classic ML module pairing information theory (the foundation) with decision trees (the application). Covers Shannon entropy, Gini impurity, information gain, and the greedy split algorithm.

---

## Information Theory

### Shannon Entropy (Disorder/Uncertainty of a Label Set)

**Formula:** `H(y) = -sum(p_i * log2(p_i))` for each class i with proportion p_i.

- Base-2 logarithm yields bits (ML traditionally uses natural log for nats, but the source lesson uses log2).
- **Range:** [0, log2(k)] where k is the number of classes.
- **H = 0** when the set is pure (all samples belong to one class; p_i = 1 for one class, 0 for others, so only one term survives: 1 * log2(1) = 0).
- **Maximum** occurs when classes are equally balanced. For a binary split, max H = 1 bit (two classes, 50/50).

**Numeric example (6 cats, 4 dogs):**
- p_cat = 0.6, p_dog = 0.4
- H = -(0.6 * log2(0.6) + 0.4 * log2(0.4)) = -(0.6 * -0.737 + 0.4 * -1.322) = 0.442 + 0.529 = 0.971 bits

**Intuition:** Entropy measures irreducible uncertainty. A pure node tells you nothing; a balanced node is maximally uncertain. [Lesson 09 Information Theory, The Concept: Entropy section]

### Gini Impurity (Probability of Misclassification at a Node)

**Formula:** `Gini(S) = 1 - sum(p_k^2)` for each class k with proportion p_k.

- **Range:** [0, 1 - 1/k] where k is number of classes. For binary classification, max Gini = 0.5.
- **Gini = 0** when the set is pure (one p_k = 1, all others = 0, so sum of squares = 1).
- **Maximum** when classes are equally mixed.

**Numeric example (6 cats, 4 dogs):**
- Gini = 1 - (0.6^2 + 0.4^2) = 1 - (0.36 + 0.16) = 0.48

**Intuition:** If you randomly select a sample from the node and label it according to the class distribution, Gini is the probability you get it wrong. Lower is better (purer). [Lesson 04 Decision Trees, The Concept: Split Criteria section]

### Information Gain (Reduction in Impurity After a Split)

**Formula:** `IG(S, feature, threshold) = Impurity(S) - weighted_avg(Impurity(S_left), Impurity(S_right))`

where weights are the proportions of samples in left and right children.

Equivalently (for Gini or entropy):
- `IG = parent_impurity - (n_left/n * child_left_impurity + n_right/n * child_right_impurity)`

**Numeric example:** Parent has Gini = 0.48 (6 cats, 4 dogs). Split into:
- Left: 5 cats, 1 dog (Gini = 1 - (5/6)^2 - (1/6)^2 = 0.278)
- Right: 1 cat, 3 dogs (Gini = 1 - (1/4)^2 - (3/4)^2 = 0.375)
- IG = 0.48 - (6/10 * 0.278 + 4/10 * 0.375) = 0.48 - 0.317 = 0.163 bits (or Gini units)

**Intuition:** Information gain measures how much a split reduces disorder. The tree splits recursively on the (feature, threshold) pair with the highest gain. [Lesson 04 Decision Trees, The Concept: Information Gain and How Splitting Works sections]

### Cross-Entropy (Loss Function Context, One-Line Note)

**Formula:** `H(P, Q) = -sum(p(x) * log(q(x)))` where P is the true distribution, Q is the model's predictions.

Relationship: `H(P, Q) = H(P) + KL(P || Q)`. In classification, minimizing cross-entropy loss is equivalent to minimizing KL divergence (the true distribution entropy is constant during training). The source ties this to decision trees only indirectly: trees minimize impurity (entropy-based or Gini-based), which indirectly shapes predictions toward the empirical class distribution. [Lesson 09 Information Theory, The Concept: Cross-Entropy section]

---

## Decision Trees

### The Greedy Recursive Algorithm

**High-level:** Build the tree top-down by repeatedly selecting the best split at each node until stopping conditions are met.

**Split search (at each node with n features and m samples):**
1. For each feature j (j = 1 to n):
   - Sort samples by feature j values.
   - Try every midpoint between consecutive distinct values as a candidate threshold.
   - Compute information gain (or Gini/entropy) for each threshold.
2. Select the (feature, threshold) pair with the highest information gain.
3. Partition data into left (feature <= threshold) and right (feature > threshold).
4. Recurse on each child.

**Greedy guarantee:** This approach does not find the globally optimal tree (finding it is NP-hard), but it works well in practice due to the structure of real data. [Lesson 04 Decision Trees, The Concept: How Splitting Works section]

### Stopping Rules (Pre-Pruning Controls)

Stop tree growth early to prevent overfitting:

- **Max depth:** Stop if tree reaches a specified depth (e.g., max_depth=5).
- **Min samples to split:** Stop if a node has fewer than k samples (e.g., min_samples_split=2).
- **Min samples per leaf:** Stop if a split would create a child with fewer than k samples (e.g., min_samples_leaf=1).
- **Min information gain:** Stop if the best split improves impurity by less than a threshold (e.g., min_gain=0.01).
- **Max leaf nodes:** Limit the total number of leaves.

Post-pruning (grow full tree, then trim subtrees that fail validation) is also possible but slower. [Lesson 04 Decision Trees, The Concept: Stopping Conditions section]

### Leaf Prediction

- **Classification:** Predict the majority class (the label with the highest count) in the leaf.
- **Regression:** Predict the mean of target values in the leaf.

[Lesson 04 Decision Trees, code: `_make_leaf()` method; `majority_vote()` and `_mean()` functions]

### Overfitting via Depth

A tree grown to full depth (one sample per leaf) perfectly memorizes training data but generalizes terribly. The depth hyperparameter controls the bias-variance tradeoff:

- **Shallow trees:** High bias, low variance. Underfit.
- **Deep trees:** Low bias, high variance. Overfit.
- **Optimal depth:** Found via cross-validation on a validation set.

Code demo (Lesson 04 Decision Trees, demo_decision_tree): Shows test accuracy plateaus around depth 2-3, then degrades as overfitting occurs. [Lesson 04 Decision Trees, code section]

---

## Decision Trees: Random Forests Extension

### Ensemble via Bagging + Feature Randomization

Random forests reduce the high variance of single trees by training many decorrelated trees and averaging predictions.

**Bagging (Bootstrap Aggregating):**
- For each tree, sample n observations with replacement (a bootstrap sample) from the training data.
- About 63% of the original samples appear in each bootstrap (out-of-bag samples can be used for validation).

**Feature randomization:**
- At each split, only a random subset of features is considered.
- Default for classification: sqrt(n_features). For regression: n_features / 3.

**Prediction:**
- Classification: Majority vote across all trees.
- Regression: Average predictions across all trees.

**Key insight:** Averaging many decorrelated trees reduces variance without increasing bias. Each individual tree may be mediocre; the ensemble is strong. [Lesson 04 Decision Trees, The Concept: Random Forests section]

### Feature Importance (Mean Decrease in Impurity)

**Computation:** For each feature, sum the total reduction in impurity (Gini or entropy) across all nodes where that feature is used, weighted by the proportion of samples at each node:

```
importance(feature_j) = sum over all nodes where feature_j is used:
    (n_samples_at_node / n_total_samples) * impurity_decrease
```

Average across all trees in the forest. Normalize to sum to 1.

**Bias:** MDI is biased toward high-cardinality features and features with many split points (they have more opportunities to appear in the tree). Permutation importance (shuffle a feature's values and measure accuracy drop) is more reliable but slower. [Lesson 04 Decision Trees, The Concept: Feature Importance section; code: `feature_importances()` method]

---

## Source Code Shape

### Information Theory Module (`information_theory.py`)

**Functions provided:**
- `information_content(p, base=2)`: Return -log(p) / log(base). Bits if base=2, nats if base=e.
- `entropy(probs, base=2)`: Sum of p * information_content(p, base) over all p > 0.
- `cross_entropy(p, q, base=2)`: Sum of p_i * (-log(q_i) / log(base)). Returns infinity if any q_i <= 0.
- `kl_divergence(p, q, base=2)`: cross_entropy(p, q) - entropy(p).
- `mutual_information(joint_probs, base=2)`: Computes I(X;Y) from a 2D joint distribution matrix.
- `softmax(logits)`: Exponentiate and normalize logits to a probability distribution.
- `cross_entropy_loss(true_class, logits)`: -log(softmax(logits)[true_class]). Classification loss.
- `perplexity(avg_cross_entropy, base="e")`: exp(avg_cross_entropy) (if base="e") or 2^avg_cross_entropy (if base=2).
- `conditional_entropy(joint_probs, base=2)`: H(Y|X) from joint distribution.
- `joint_entropy(joint_probs, base=2)`: H(X,Y) from joint distribution.

**Demos:** Label smoothing, feature selection via mutual information, KL divergence asymmetry, cross-entropy vs NLL equivalence.

### Decision Trees Module (`trees.py`)

**Classes:**
- `DecisionTree`: Recursive splitting, pre-pruning controls. Supports both classification and regression.
  - `__init__(max_depth, min_samples_split, min_samples_leaf, criterion="gini", max_features, task="classification")`
  - `fit(X, y)`: Build the tree via recursive `_build()`.
  - `predict(X)`: Traverse tree for each sample.
  - `_best_split()`: Search all features/thresholds, return (feature_idx, threshold, gain).
  - `print_tree()`: Debug utility to print tree structure.

- `RandomForest`: Ensemble of DecisionTrees.
  - `__init__(n_trees=100, max_depth, min_samples_split, max_features="sqrt", criterion="gini", task="classification")`
  - `fit(X, y)`: Train n_trees bootstrap samples.
  - `predict(X)`: Majority vote (classification) or average (regression).
  - `feature_importances()`: MDI scores, normalized to sum to 1.

**Utility functions:**
- `gini_impurity(labels)`: 1 - sum((c/n)^2 for c in class counts).
- `entropy(labels)`: -sum((c/n) * log2(c/n) for c > 0).
- `information_gain(parent_labels, left_labels, right_labels, criterion="gini")`: Impurity reduction.
- `variance_reduction(parent_values, left_values, right_values)`: Regression criterion.
- `majority_vote(labels)`: Return most frequent label.
- `accuracy(y_true, y_pred)`: Fraction correct.
- `generate_classification_data(n_samples, seed)`: Synthetic 2-feature, 3-class dataset.
- `generate_regression_data(n_samples, seed)`: Synthetic sin(x)*x + noise.
- `train_test_split(X, y, test_ratio=0.2, seed)`: Simple 80/20 split.

**Numeric defaults (from code):**
- `min_samples_split=2`: Do not split if fewer than 2 samples.
- `min_samples_leaf=1`: Do not split if either child would have fewer than 1 sample (effectively no constraint).
- `max_features="sqrt"` (random forest): Randomly select sqrt(n_features) features at each split.
- Threshold selection: Midpoint between consecutive distinct feature values.

### Demos in trees.py

1. `demo_split_criteria()`: Gini vs entropy on pure, balanced, imbalanced nodes. Shows they produce nearly identical values.
2. `demo_information_gain()`: Example with parent of 10 labels (cats, dogs, birds), three candidate splits, IG computation.
3. `demo_decision_tree()`: Train on synthetic 200-sample 2D dataset, vary max_depth from 1 to None, show train/test accuracy. Reveals overfitting.
4. `demo_gini_vs_entropy()`: Compare trees using Gini vs entropy criteria on same dataset. Accuracy difference is minimal.
5. `demo_random_forest()`: Vary number of trees (1, 3, 5, 10, 25, 50, 100). Show test accuracy plateaus (ensemble benefit).
6. `demo_feature_importance()`: 4-feature dataset with 2 informative, 2 noise. MDI correctly ranks the informative features higher.
7. `demo_regression_tree()`: Fit sin(x)*x + noise with varying depths. Random forest smooths piecewise predictions.
8. `demo_single_tree_vs_forest()`: Train 5 single trees and 5 forests on perturbations of the data. Forest has lower variance across runs.

---

## Worked Numeric Examples

### Entropy Example (from information_theory.py)

**Fair coin (two equiprobable outcomes):**
- p = [0.5, 0.5]
- H = -(0.5 * log2(0.5) + 0.5 * log2(0.5)) = -(0.5 * (-1) + 0.5 * (-1)) = 1.0 bit

**Biased coin (99% heads):**
- p = [0.99, 0.01]
- H = -(0.99 * log2(0.99) + 0.01 * log2(0.01))
- log2(0.99) ≈ -0.0145, log2(0.01) ≈ -6.6439
- H ≈ -(0.99 * -0.0145 + 0.01 * -6.6439) ≈ 0.08 bits

**Fair die (6 equally likely outcomes):**
- p = [1/6, 1/6, 1/6, 1/6, 1/6, 1/6]
- H = 6 * (1/6 * log2(6)) = log2(6) ≈ 2.585 bits

### Gini Example (from decision trees lesson)

**Parent node: 6 cats, 4 dogs (total 10)**
- Gini = 1 - ((6/10)^2 + (4/10)^2) = 1 - (0.36 + 0.16) = 0.48

### Information Gain Example (from demo_information_gain in trees.py)

**Parent:** [cat, cat, cat, cat, dog, dog, dog, bird, bird, bird] (4 cats, 3 dogs, 3 birds)
- Parent Gini = 1 - ((4/10)^2 + (3/10)^2 + (3/10)^2) = 1 - (0.16 + 0.09 + 0.09) = 0.66

**Feature B split:** [cat, cat, cat, cat] | [dog, dog, dog, bird, bird, bird]
- Left (4 cats, 0 others): Gini_left = 0
- Right (0 cats, 3 dogs, 3 birds): Gini_right = 1 - ((3/6)^2 + (3/6)^2) = 0.5
- IG = 0.66 - (4/10 * 0 + 6/10 * 0.5) = 0.66 - 0.3 = 0.36

**Feature A split:** [cat, cat, cat, dog] | [cat, dog, dog, bird, bird, bird]
- Left (3 cats, 1 dog): Gini_left = 1 - ((3/4)^2 + (1/4)^2) = 0.375
- Right (1 cat, 2 dogs, 3 birds): Gini_right = 1 - ((1/6)^2 + (2/6)^2 + (3/6)^2) ≈ 0.75
- IG ≈ 0.66 - (4/10 * 0.375 + 6/10 * 0.75) ≈ 0.66 - 0.6 = 0.06

Feature B achieves higher information gain and is selected.

### Cross-Entropy and NLL Equivalence (from information_theory.py)

For 1000 samples with random logits and labels:
- Cross-entropy loss and negative log-likelihood computed independently produce identical results (difference < 1e-10).
- This verifies the equivalence: minimizing CE = maximizing likelihood.

---

## Out of Scope / Hold for Later

- **Ensemble methods (Random Forests as baseline, but boosting/XGBoost/LightGBM):** Scheduled for M4 (gradual boosting, sequential error correction). Random forests are covered as the decorrelation mechanism; gradient boosting is not.
- **Evaluation metrics (precision, recall, F1, ROC-AUC, confusion matrix):** Scheduled for M5. Information gain and Gini are split criteria, not evaluation metrics.
- **Regression trees (variance reduction):** Included in the source code (both DecisionTree and RandomForest support task="regression"), but the written lesson focuses on classification. Variance reduction formula is mentioned; numeric example is provided in code demo.
- **Post-pruning and cost-complexity pruning:** Mentioned in the lesson as an alternative to pre-pruning but not implemented in detail. Pre-pruning (max_depth, min_samples) is the primary focus.
- **Feature selection via mutual information:** Covered in the information theory lesson as a standalone use case. Not tied explicitly to tree-based feature selection in the decision tree lesson.

---

## Dubious or Noteworthy Claims

1. **"63% of original samples appear in each bootstrap"** (Lesson 04, Random Forests section): This is mathematically correct for large n (approaches 1 - 1/e ≈ 0.632), but the source states it as fact without derivation. Acceptable because it is a well-known property of bootstrap sampling.

2. **"Gini and entropy produce nearly identical trees"** (Multiple demos in trees.py): Empirically true for the synthetic datasets shown, but the source does not rigorously prove this convergence. In practice, trees built with Gini vs entropy can differ slightly on real data, though differences are usually minor. The claim is practical, not theoretical.

3. **"Greedy splitting does not find the globally optimal tree"** (Lesson 04): True (NP-hard problem), but the source does not quantify how far greedy trees deviate from optimal. For practical purposes, greedy is sufficient, but this is context-dependent.

4. **Cross-entropy = NLL for one-hot labels:** Technically true and well-established, but the source does not explicitly prove it from first principles (proof requires substituting one-hot encoding into the cross-entropy formula). The code verification is empirical.

5. **Mutual information detects "any statistical dependency"** (Lesson 09, Feature Importance for Feature Selection section): Technically MI is zero if and only if X and Y are independent, but empirical MI estimation from finite samples can have high variance. The source does not address estimation stability.

All major formulas are faithfully reproduced. No calculations contradict the source.
