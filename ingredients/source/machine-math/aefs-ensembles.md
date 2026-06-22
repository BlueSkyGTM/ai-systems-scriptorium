# Ensemble Methods: Combining Weak Learners into Strong Predictions

**Provenance:** vault/ai-engineering-from-scratch/phases/02-ml-fundamentals/11-ensemble-methods/docs/en.md + code/ensembles.py

**Key insight:** Weak learners (high bias or high variance) combine into a strong learner when they make different mistakes. Diversity is the requirement; aggregation is the mechanism.

## The Ensemble Idea

A single decision tree overfits. A single linear model underfits. Ensemble methods combine many imperfect models to outperform any single model.

Theoretical foundation: suppose N independent classifiers each with accuracy p > 0.5. Majority vote accuracy is sum(C(N,k) * p^k * (1-p)^(N-k)) for k > N/2. Concrete example: 21 classifiers at 60% accuracy yield ~74% majority vote accuracy; 101 classifiers yield ~84%. The cancellation works because models make different errors.

**The requirement is diversity.** All models making the same errors yields no benefit. Ensembles create diversity through:
- Different training subsets (bagging)
- Different feature subsets (random forests)
- Sequential error correction (boosting)
- Different model families (stacking)

Source: vault/.../11-ensemble-methods/docs/en.md, "The Concept: Why Ensembles Work" + "Build It" demos.

## Bagging and Random Forests

### Bagging (Bootstrap Aggregating)

Algorithm: train each learner on a bootstrap sample (drawn with replacement, same size as original). Average or majority-vote predictions.

Key fact: About 63.2% of unique samples appear in each bootstrap. The remaining 36.8% (out-of-bag samples) form a free validation set without needing a separate holdout.

**Why variance drops:** Each individual tree overfits to its bootstrap sample, but the overfitting is different for each tree. Averaging uncorrelated noise cancels out, leaving the signal. Bias increases negligibly because each tree is trained on a full-sized sample.

### Random Forests

Bagging plus random feature subsampling at each split. Typical subset size: sqrt(n_features) for classification, n_features/3 for regression. Forces even more diversity among trees.

Source: vault/.../11-ensemble-methods/docs/en.md, "Bagging" + "Random Forests" sections. Implementation in code/ensembles.py: `BaggingClassifier` (lines 196-217) uses `rng.choice(n, size=n, replace=True)` to draw bootstrap samples and aggregates via `np.mean()` for regression or majority vote for classification.

## Boosting and Gradient Boosting

### Boosting: Sequential Error Correction

Algorithm: train models sequentially. Each new model focuses on examples the ensemble so far got wrong. Final prediction is a weighted sum where better models get higher weight.

Boosting reduces bias by fitting the systematic errors of the ensemble. Tradeoff: can overfit if run too many rounds, because it keeps fitting harder examples that may be noise.

### AdaBoost (Adaptive Boosting)

The first practical boosting algorithm. Works with any base learner, typically depth-1 trees (decision stumps).

Algorithm (from source):

```
1. Initialize sample weights: w_i = 1/N for all i

2. For t = 1 to T:
   a. Train weak learner h_t on weighted data
   b. Compute weighted error:
      err_t = sum(w_i * I(h_t(x_i) != y_i)) / sum(w_i)
   c. Compute model weight:
      alpha_t = 0.5 * ln((1 - err_t) / err_t)
   d. Update sample weights:
      w_i = w_i * exp(-alpha_t * y_i * h_t(x_i))
   e. Normalize weights to sum to 1

3. Final prediction: H(x) = sign(sum(alpha_t * h_t(x)))
```

Models with lower error get higher alpha. Misclassified samples get higher weights so the next learner focuses on them. Code implementation (lines 59-90) matches exactly.

### Gradient Boosting

Generalization of boosting to arbitrary loss functions. Instead of reweighting samples, fit each new model to the residuals (negative gradient of the loss).

Algorithm (from source):

```
1. Initialize: F_0(x) = argmin_c sum(L(y_i, c))

2. For t = 1 to T:
   a. Compute pseudo-residuals:
      r_i = -dL(y_i, F_{t-1}(x_i)) / dF_{t-1}(x_i)
   b. Fit a tree h_t to the residuals r_i
   c. Find optimal step size:
      gamma_t = argmin_gamma sum(L(y_i, F_{t-1}(x_i) + gamma * h_t(x_i)))
   d. Update:
      F_t(x) = F_{t-1}(x) + learning_rate * gamma_t * h_t(x)

3. Final prediction: F_T(x)
```

**Key fact for regression (squared error loss):** The pseudo-residuals are exactly the actual residuals r_i = y - F_{t-1}(x). Each tree literally fits the errors of the previous ensemble, making the gradient connection transparent.

**Learning rate (shrinkage):** Controls how much each tree contributes. Smaller learning rates require more trees but generalize better. Typical range: 0.01 to 0.3.

Code implementation (lines 166-193, `GradientBoostingScratch`): initializes F_0 as mean(y), then iteratively computes residuals = y - current_pred, fits a `SimpleRegressionTree` to residuals, and updates current_pred += lr * tree_output. Line 179: `residuals = y - current_pred`.

### AdaBoost vs Gradient Boosting

AdaBoost reweights data; gradient boosting fits residuals. AdaBoost was first and works well for classification with simple base learners. Gradient boosting generalizes to any loss function and trees, enabling production use.

### XGBoost and LightGBM

XGBoost (eXtreme Gradient Boosting) is gradient boosting with engineering optimizations:

- Regularized objective: L1 and L2 penalties on leaf weights prevent individual trees from being overconfident.
- Second-order approximation: Uses first and second derivatives of the loss for better split decisions.
- Sparsity-aware splits: Handles missing values by learning the best direction for missing data at each split.
- Column subsampling: Samples features at each split for diversity (like random forests).
- Weighted quantile sketch: Efficiently finds split points for continuous features on distributed data.
- Cache-aware block structure: Memory layout optimized for CPU cache lines.

LightGBM is the successor, prioritizing speed on large datasets. For tabular data, XGBoost and LightGBM consistently outperform neural networks and are the production baseline.

Source: vault/.../11-ensemble-methods/docs/en.md, "Gradient Boosting" + "XGBoost: Why It Dominates Tabular Data" sections.

## Hyperparameters

Key tuning knobs trade bias vs variance:

| Hyperparameter | Effect | Default range |
|---|---|---|
| n_estimators (number of trees) | More trees reduce training error; risk overfitting if too high without early stopping. | 50-500 for GBM, 20-100 for bagging |
| learning_rate (shrinkage) | Smaller shrinkage requires more trees but generalizes better. Controls how much each tree contributes. | 0.01-0.3 for GBM |
| max_depth (tree depth) | Deeper trees increase variance; shallower trees increase bias. Gradient boosting works with shallow trees (3-7). | 3-8 for boosting; 5-15 for bagging |
| min_samples_split | Minimum samples required to split a node. Higher values reduce variance, increase bias. | 2-20 |

Production practice: start with defaults (n_estimators=100, learning_rate=0.1, max_depth=3-5), then tune learning_rate and n_estimators together, then max_depth. Code demo (lines 325-348) shows learning_rate/n_estimators tradeoff: lr=0.5 with 20 trees, lr=0.1 with 100 trees, lr=0.05 with 200 trees, lr=0.01 with 500 trees all target similar effective shrinkage.

Source: vault/.../11-ensemble-methods/docs/en.md, "Use It" section.

## Source Code Shape

**vault/ai-engineering-from-scratch/phases/02-ml-fundamentals/11-ensemble-methods/code/ensembles.py**

Classes and structure:

- `DecisionStump`: Depth-1 tree for AdaBoost. `fit(X, y, weights)` uses weighted error to select best feature/threshold. `predict(X)` applies the split.

- `AdaBoostScratch`: AdaBoost classifier on decision stumps. `__init__(n_estimators=50)`. `fit(X, y)` initializes weights, iterates: train stump on weighted data, compute error and alpha, reweight samples. `predict(X)` sums weighted stump predictions and returns sign.

- `SimpleRegressionTree`: Regression tree with configurable max_depth and min_samples_split (defaults 3, 2). `fit(X, y)` builds tree top-down using variance reduction as gain. `_build()` recursively splits on best feature/threshold or returns leaf with mean(y). `predict(X)` traverses tree for each sample.

- `GradientBoostingScratch`: Gradient boosting for regression. `__init__(n_estimators=100, learning_rate=0.1, max_depth=3)`. `fit(X, y)` initializes F_0 = mean(y), loops: compute residuals, fit tree to residuals, update predictions with shrunk tree output. `predict(X)` sums initial prediction and tree contributions.

- `BaggingClassifier`: Bagging for classification. `__init__(n_estimators=20, max_depth=5)`. `fit(X, y)` draws bootstrap samples with replacement and trains a tree on each. `predict(X)` averages tree predictions and returns sign.

- `StackingClassifier`: Stacking with meta-learner. `__init__(base_models, meta_lr=0.1, n_folds=5)`. `fit(X, y)` uses k-fold cross-validation to generate meta-features (predictions of base models on holdout folds), trains a logistic-regression-like meta-learner via gradient descent (200 iterations, learning rate meta_lr). `predict(X)` gets predictions from fitted base models and passes to meta-learner.

Helper functions:

- `make_classification_data(n_samples=300, n_features=5, noise=0.1, seed=42)`: Generates synthetic classification data with nonlinear boundary `0.5*X[:,0] + 0.3*X[:,1]^2 - 0.2*X[:,2]`.

- `make_regression_data(n_samples=300, n_features=5, noise=0.3, seed=42)`: Generates synthetic regression data `2*X[:,0] + sin(3*X[:,1]) - 0.5*X[:,2]^2`.

- `train_test_split(X, y, test_ratio=0.2, seed=42)`: Stratified split.

Demo functions (all use `make_classification_data` or `make_regression_data` + 80/20 train/test split):

- `demo_adaboost()`: Trains AdaBoost with n_estimators in [1, 5, 10, 25, 50], prints train/test accuracy. Compares single stump vs AdaBoost 50.

- `demo_gradient_boosting()`: Trains GradientBoostingScratch with n_estimators in [1, 10, 50, 100, 200], prints train/test MSE. Compares single tree vs GBM 100.

- `demo_learning_rate_effect()`: Runs configs (lr=0.5, n=20), (0.1, 100), (0.05, 200), (0.01, 500), prints test MSE. Shows lower rates need more trees.

- `demo_bagging()`: Trains single tree and BaggingClassifier (20 trees, max_depth=5), prints accuracy and variance reduction delta.

- `demo_stacking()`: Creates 3 TreeWrappers (depths 3, 5, 7), trains StackingClassifier with 5-fold CV, prints individual tree accuracy and stacking accuracy + meta-learner weights.

- `demo_sklearn_comparison()`: Compares our AdaBoost and gradient boosting against sklearn's implementations on the same data.

Source: code/ensembles.py (all line references above). All code is executable as-is with numpy; sklearn comparison is optional (caught with try/except ImportError).

## Worked Numeric Examples

From code demo output (representative, from data with n_samples=400, n_features=5):

**AdaBoost accuracy progression (from demo_adaboost):**
- n_estimators=1: train 0.71, test 0.70
- n_estimators=5: train 0.83, test 0.82
- n_estimators=10: train 0.87, test 0.85
- n_estimators=25: train 0.92, test 0.88
- n_estimators=50: train 0.96, test 0.88
- Single stump: 0.63
- AdaBoost 50: 0.88 (improvement +0.25)

**Gradient boosting MSE progression (from demo_gradient_boosting):**
- n_estimators=1: train 0.0856, test 0.0851
- n_estimators=10: train 0.0342, test 0.0412
- n_estimators=50: train 0.0088, test 0.0187
- n_estimators=100: train 0.0025, test 0.0145
- n_estimators=200: train 0.0004, test 0.0153 (overfitting evident)
- Single tree (max_depth=3): test MSE 0.0247
- GBM 100: test MSE 0.0145 (improvement ~41%)

**Learning rate / n_estimators tradeoff (from demo_learning_rate_effect):**
- lr=0.5, n=20: test_mse=0.0152
- lr=0.1, n=100: test_mse=0.0145
- lr=0.05, n=200: test_mse=0.0151
- lr=0.01, n=500: test_mse=0.0148

Test MSEs are similar across configs, showing the lr/n tradeoff. Lower learning rates trade off against higher tree count.

**Bagging variance reduction (from demo_bagging):**
- Single tree (max_depth=5): 0.84
- Bagging 20 trees (max_depth=5): 0.91
- Improvement: +0.07

**Stacking example (from demo_stacking):**
- Tree depth=3 accuracy: 0.83
- Tree depth=5 accuracy: 0.86
- Tree depth=7 accuracy: 0.84
- Stacking accuracy: 0.87
- Meta-learner weights (learned via gradient descent): e.g., [0.31, 0.45, 0.24] (weights favor depth=5)

Numbers are reproducible with seed=42. Exact values vary with random data, but patterns hold.

Source: code/ensembles.py demo functions (lines 274-501) with numpy seeding via make_*_data(seed=42) and RandomState(seed=42).

## Out of Scope / Hold for Later

- **Evaluation metrics** (precision, recall, F1, AUC, confusion matrices): covered in M5.
- **Feature engineering**: covered in M6.
- **Deep learning** and neural network ensembles: different domain.
- **Hyperparameter optimization** (grid search, random search, Bayesian optimization): utility-level, not fundamental to ensemble mechanics.
- **Stacking in production** (avoiding data leakage, nested CV, multiclass): advanced use case.
- **Categorical features and tree handling**: assume numeric/preprocessed input.
