# Feature Engineering, Imbalanced Data, and Feature Selection

**Provenance:** Distilled from vault/ai-engineering-from-scratch/phases/02-ml-fundamentals:
- Lesson 08: Feature Engineering & Selection
- Lesson 17: Handling Imbalanced Data
- Lesson 18: Feature Selection

**Module:** Feature Reality (Classic ML)

## Encoding categorical features

*Source: Lesson 08, "Categorical Features" section*

Models need numeric input. Categories must be encoded.

**One-hot encoding**: Creates a binary column for each category. If a feature is color = red/blue/green, one-hot encoding produces three columns: is_red, is_blue, is_green. Exactly one column is 1 per sample; all others are 0. Works well for low-cardinality features but explodes with many categories.

Example from lesson code (neighborhoods: downtown, rural, suburbs):
- downtown -> [1, 0, 0]
- rural -> [0, 1, 0]
- suburbs -> [0, 0, 1]

Result shape: n_samples x n_categories

**Dummy-variable note**: One-hot creates multicollinearity (the n columns are linearly dependent: sum always equals 1). Some pipelines drop one column as a baseline to avoid this. Decision trees do not care; linear models often benefit.

**Label encoding**: Maps each category to an integer: red=0, blue=1, green=2. Introduces false ordering (the model might think green > blue > red). Use only for tree-based models that split on individual values, not for distance-based or linear models.

**Ordinal/label encoding when order matters**: For truly ordered categories (small < medium < large), label encoding with correct order (small=1, medium=2, large=3) preserves the relationship and can improve model performance.

Target encoding is covered separately (Lesson 08, data leakage risk noted).

## Scaling: when and why models need it

*Source: Lesson 08, "Scaling" section*

Scaling puts features on the same range so distance-based algorithms (K-Means, KNN, SVM) treat all features equally.

**Min-max scaling**: Maps to [0, 1]. Formula: (x - min) / (max - min).

**Standardization (z-score)**: Maps to mean=0, std=1. Formula: (x - mean) / std. More robust to outliers than min-max when data has extreme values.

**Which models need scaling**: Distance-based and regularized models (KNN, K-Means, SVM, Lasso, Ridge). Tree-based models (decision trees, random forests, gradient boosting) do not care about scale; they split on values, not distances.

## Imbalanced data: why accuracy misleads

*Source: Lesson 17, "Why Accuracy Fails" section*

Consider a dataset with 1000 samples: 990 negative, 10 positive. A model that always predicts negative:

| Outcome | Predicted Positive | Predicted Negative |
|---------|-------------------|--------------------|
| Actually Positive | 0 (TP) | 10 (FN) |
| Actually Negative | 0 (FP) | 990 (TN) |

Accuracy = (0 + 990) / 1000 = 99.0%

The model catches zero of the minority class. Accuracy is useless here.

**Metrics that matter for imbalanced data**:

- **Precision** = TP / (TP + FP): Of everything flagged as positive, how many actually are?
- **Recall** = TP / (TP + FN): Of everything actually positive, how many did we catch?
- **F1 Score** = 2 * precision * recall / (precision + recall): Harmonic mean, penalizes extreme imbalance.
- **AUPRC** (Area Under Precision-Recall Curve): Like AUC-ROC but more informative for imbalanced data. A random classifier has AUPRC equal to the positive class rate (not 0.5).
- **Matthews Correlation Coefficient (MCC)** = (TP * TN - FP * FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)): Ranges -1 to +1. Only gives high scores when the model does well on both classes, regardless of class size.

For the "always predict negative" example: F1 = 0, MCC = 0, AUPRC = 0.01 (assuming 1% positive rate).

## Resampling strategies for imbalanced data

*Source: Lesson 17, "Sampling Strategies Compared" section*

**Random oversampling**: Duplicate minority samples to match majority count.
- Pros: simple, no information loss
- Cons: exact duplicates cause overfitting, increases training time

**Random undersampling**: Remove majority samples to match minority count.
- Pros: fast training, simple
- Cons: throws away potentially useful majority data, higher variance

**SMOTE (Synthetic Minority Oversampling Technique)**: Create synthetic minority samples via interpolation. Algorithm:
1. For each minority sample x, find its k nearest neighbors among other minority samples
2. Pick one neighbor at random
3. Create a new sample on the line segment between x and that neighbor

Formula: new_sample = x + random(0, 1) * (neighbor - x)

This interpolates between real minority points, creating samples in the same feature space without just copying.

- Pros: generates new data points, reduces overfitting compared to random oversampling
- Cons: can create noisy samples near the decision boundary, does not account for majority class distribution

| Strategy | Data Changed | Risk | When to Use |
|----------|-------------|------|-------------|
| Oversample | Minority duplicated | Overfitting | Small datasets, moderate imbalance |
| Undersample | Majority removed | Information loss | Large datasets, want fast training |
| SMOTE | Synthetic minority added | Boundary noise | Moderate imbalance, enough minority samples for k-NN |

## Class weights

*Source: Lesson 17, "Class Weights" section*

Instead of changing the data, change how the model treats errors. Assign higher weight to misclassifying the minority class.

For a binary problem with 950 negative and 50 positive samples:
- Weight for negative class = n_samples / (2 * n_negative) = 1000 / (2 * 950) = 0.526
- Weight for positive class = n_samples / (2 * n_positive) = 1000 / (2 * 50) = 10.0

The positive class gets 19x the weight. Misclassifying one positive sample costs as much as misclassifying 19 negative samples. The model is forced to pay attention to the minority class.

In logistic regression, this modifies the loss function:

weighted_loss = -sum(w_i * [y_i * log(p_i) + (1-y_i) * log(1-p_i)])

where w_i depends on the class of sample i.

Class weights are mathematically equivalent to oversampling in expectation, but without creating new data points. This makes them faster and avoids the overfitting risk of duplicated samples.

## Feature selection: why more is not better

*Source: Lesson 18, "The Problem" section*

As the number of features grows, the volume of the feature space explodes. Data points become sparse. Distances between points converge. The model needs exponentially more data to find real patterns. Noise features drown out signal features. Overfitting becomes the default.

This is the **curse of dimensionality**.

The goal is not to use all available information. It is to use the right information.

## Filter methods: variance threshold and correlation

*Source: Lesson 18, "Variance Threshold" and "Correlation Filtering" sections*

**Variance Threshold**: The simplest filter. If a feature barely varies across samples, it carries almost no information.

variance(x) = mean((x - mean(x))^2)

Set a threshold (e.g., 0.01). Drop every feature with variance below it. This removes constant or near-constant features without looking at the target variable at all.

When to use: as a preprocessing step before other methods. It catches obviously useless features at near-zero cost.

Limitation: a feature can have high variance and still be pure noise. Variance threshold is necessary but not sufficient.

**Correlation Filtering**: Remove features highly correlated with each other (redundant). Compute pairwise correlation; if abs(correlation) >= threshold (e.g., 0.9), remove one of the pair.

Limitation: only captures linear relationships. Does not detect nonlinear redundancy.

**Mutual Information**: Measures how much knowing feature X reduces uncertainty about target Y.

I(X; Y) = sum_x sum_y p(x, y) * log(p(x, y) / (p(x) * p(y)))

If X and Y are independent, I(X; Y) = 0. The more X tells you about Y, the higher the mutual information.

Key advantage over correlation: captures nonlinear relationships. A feature might have zero correlation with the target but high mutual information because the relationship is quadratic or periodic.

For continuous features, discretize into bins first (e.g., sqrt(n) bins). The number of bins affects the estimate.

## Wrapper and embedded methods

*Source: Lesson 18, "Recursive Feature Elimination (RFE)" and "L1 (Lasso) Regularization" sections*

**Recursive Feature Elimination (RFE)**: A wrapper method using the model's own feature importance.
1. Train the model with all features
2. Rank features by importance (coefficients for linear models, impurity reduction for trees)
3. Remove the least important feature(s)
4. Repeat until the desired number of features remains

RFE considers feature interactions because the model sees all remaining features together. Removing one feature changes the importance of others. More thorough than filter methods.

Cost: you train the model N - target times. With 500 features and target of 10, that is 490 training runs. Speed it up by removing multiple features per step (e.g., remove bottom 10% each round).

**L1 (Lasso) Regularization**: An embedded method. Adds the absolute value of weights to the loss function:

loss = prediction_error + alpha * sum(|w_i|)

The alpha parameter controls how aggressively features are pruned. Higher alpha means more weights go to exactly zero.

Why exactly zero? The L1 penalty creates a diamond-shaped constraint region in weight space. The optimal solution tends to land at a corner where one or more weights are zero. L2 regularization (ridge) creates a circular constraint where weights shrink but rarely hit zero.

Advantages: single training run, handles correlated features (picks one and zeros the others), built into most linear model implementations.

Limitation: only works for linear models. Cannot capture nonlinear feature importance.

**Tree-Based Importance**: Decision trees and ensembles (random forests, gradient boosting) naturally rank features. Every split reduces impurity (Gini or entropy). Features that produce larger impurity reductions are more important.

importance(feature_j) = (1/T) * sum over all trees of
    sum over all nodes splitting on feature_j of
        (n_samples * impurity_decrease)

Handles nonlinear relationships and feature interactions automatically.

Caution: biased toward features with many unique values (high cardinality). Use permutation importance as a sanity check.

## Method comparison table

*Source: Lesson 18, "Comparison Table" section*

| Method | Type | Speed | Nonlinear | Feature Interactions |
|--------|------|-------|-----------|---------------------|
| Variance threshold | Filter | Very fast | No | No |
| Mutual information | Filter | Fast | Yes | No |
| Correlation filter | Filter | Fast | No | No |
| RFE | Wrapper | Slow | Depends on model | Yes |
| L1 / Lasso | Embedded | Fast | No (linear) | No |
| Tree importance | Embedded | Medium | Yes | Yes |
| Permutation importance | Model-agnostic | Slow | Yes | Yes |

## Source code shape

*From vault/.../08-feature-engineering/code/features.py, 17-imbalanced-data/code/imbalanced.py, 18-feature-selection/code/feature_selection.py*

**features.py** (~392 lines): Implements categorical encoding (one_hot_encode, label_encode, target_encode), numerical transforms (min_max_scale, standardize, log_transform, bin_values), text features (count_vectorize, tfidf), imputation (impute_mean, impute_median, impute_mode), missing indicators, correlation, mutual information, variance threshold, and correlation filtering. Includes a full demo on synthetic housing data (n=200, price prediction) showing categorical encoding outputs and feature selection results.

**imbalanced.py** (~353 lines): Generates imbalanced data (950 majority, 50 minority, 2D features), implements SMOTE with k-NN interpolation, random oversampling/undersampling, logistic regression with sample weights, class weight computation, threshold tuning (sweep 0.05 to 0.95 in 0.01 steps), confusion matrix extraction, and metric computation (accuracy, precision, recall, F1, MCC). Runs 8 experiments: baseline, no treatment, oversampling, undersampling, SMOTE, class weights, threshold tuning, and weighted loss comparison. Prints confusion matrices and metrics for each.

**feature_selection.py** (~354 lines): Generates synthetic data with 5 informative, 5 correlated, 10 noise features (500 samples, binary target). Implements variance threshold, mutual information (discretized, n_bins=10), RFE with logistic regression importance, L1 Lasso with soft-thresholding, tree-based importance (50 trees, max_depth=5), and accuracy evaluation. Compares all five methods on agreement and validates performance. Prints ranked scores for each method and accuracy on selected vs. all features.

## Worked numeric examples

*From code outputs in lesson demos*

**One-hot encoding example** (features.py, neighborhoods):
- Neighborhood values: [downtown, suburbs, rural]
- downstream -> [1, 0, 0] (one column per category)
- Result: 3 columns added for 3 categories

**Imbalanced data example** (imbalanced.py, default run):
- Dataset: 1000 samples, 50 positive (5%), 950 negative (95%)
- Train/test split: 80/20 -> 800 train, 200 test
- Always-negative baseline: accuracy 95.0%, F1 0.0, MCC 0.0
- Class weights: positive weight = 1000 / (2 * 50) = 10.0; negative weight = 1000 / (2 * 950) = 0.526
- Threshold tuning on class-weighted model: optimal threshold found ~0.15 (F1 improved)

**SMOTE example** (imbalanced.py):
- Original minority: 50 samples
- SMOTE generates 750 synthetic samples (to match 950 majority)
- Result: 1750 total training samples, 50% class balance

**Feature selection example** (feature_selection.py):
- Starting features: 20 (5 info, 5 corr, 10 noise)
- Variance threshold (0.01): all 20 survive (all have variance > 0.01)
- MI top-5: selects info_0, info_1, info_2, corr_0, corr_1 (highest MI with target)
- RFE to 5 features: selects info_0, info_1, info_2, info_3, info_4 (purely informative)
- L1 (alpha=0.05): typically selects 5-8 features, mostly informative
- Tree importance: ranks informative > correlated > noise
- Accuracy comparison: all features 0.85, info-only 0.87, selected (MI) 0.86, RFE 0.88

## Out of scope / hold for later

- **Deep-learning embeddings**: Word2Vec, GloVe, FastText for text (more powerful than TF-IDF, requires neural architecture)
- **Full portfolio pipeline**: Cross-validation, hyperparameter tuning, ensemble stacking (M7 scope)
- **Advanced sampling**: Borderline-SMOTE, ADASYN, combined SMOTE+Tomek links (beyond core SMOTE)
- **Domain-specific feature engineering**: Time-series lags, geographic clustering, business rules (applied per problem)
- **Dimensionality reduction**: PCA, t-SNE, autoencoders (separate from feature selection; loses interpretability)
