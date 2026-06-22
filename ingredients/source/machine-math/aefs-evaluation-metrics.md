# Evaluation Metrics for Classification and Regression

Provenance: vault/ai-engineering-from-scratch/phases/02-ml-fundamentals/09-model-evaluation/docs/en.md and vault/ai-engineering-from-scratch/phases/01-math-foundations/06-probability-and-distributions/docs/en.md.

Source lesson 09 (Model Evaluation) and lesson 06 (Probability and Distributions) for a classic-ML module pairing probability/threshold reasoning with metrics that measure model quality.

## The confusion matrix and the threshold

A classifier outputs a probability p in [0, 1] for each example. The decision threshold tau converts this to a label: if p >= tau, predict 1; else predict 0. Different thresholds produce different confusion matrices.

The confusion matrix for binary classification, given true labels y_true and predicted labels y_pred:

|  | Predicted 1 | Predicted 0 |
|---|---|---|
| Actually 1 | True Positive (TP) | False Negative (FN) |
| Actually 0 | False Positive (FP) | True Negative (TN) |

Definitions:
- TP: model predicted 1, ground truth is 1
- FN: model predicted 0, ground truth is 1 (missed positive)
- FP: model predicted 1, ground truth is 0 (false alarm)
- TN: model predicted 0, ground truth is 0

The threshold tau controls the TP/FP tradeoff. Lowering tau catches more positives (higher TP, higher FN) but also raises more false alarms (higher FP). Raising tau reduces false alarms but misses positives.

Source: vault/.../09-model-evaluation/docs/en.md, "The Concept: Classification Metrics" section.

## Classification metrics

### Accuracy
accuracy = (TP + TN) / (TP + TN + FP + FN)

Fraction of all predictions that were correct. Misleading when classes are imbalanced. If 95% of samples are negative, a classifier that always predicts 0 gets 95% accuracy while being useless. Do not use on imbalanced data; use precision, recall, F1, or AUC instead.

Source: vault/.../09-model-evaluation/docs/en.md, "Classification Metrics: Accuracy" section.

### Precision and Recall
precision = TP / (TP + FP)

Of all things we predicted as positive, how many actually were positive? Use when false positives are costly (e.g., spam filter incorrectly marking real email as spam).

recall (also called sensitivity) = TP / (TP + FN)

Of all actual positives in the data, how many did we correctly identify? Use when false negatives are costly (e.g., cancer screening missing a tumor).

Specificity = TN / (TN + FP)

Of all actual negatives, how many did we correctly identify? Often paired with sensitivity/recall in medical/diagnostic contexts.

Precision-recall tradeoff: as the threshold tau decreases, recall increases (we catch more positives) but precision often decreases (we make more false positive predictions). As tau increases, precision improves but recall drops. Neither dominates universally; the right choice depends on cost of FP vs. FN.

Source: vault/.../09-model-evaluation/docs/en.md, "Classification Metrics: Precision, Recall, Specificity" sections.

### F1 Score
F1 = 2 * precision * recall / (precision + recall)

Harmonic mean of precision and recall. Balances both when the cost of FP and FN are roughly equal. Single metric useful when you want to avoid choosing between precision and recall. F1 ranges from 0 (worst) to 1 (perfect). It is symmetric: swapping precision and recall does not change F1.

Source: vault/.../09-model-evaluation/docs/en.md, "Classification Metrics: F1 score" section.

## ROC and AUC

### ROC Curve
The ROC (Receiver Operating Characteristic) curve plots true positive rate (TPR) on the y-axis against false positive rate (FPR) on the x-axis, for all possible decision thresholds tau.

TPR = TP / (TP + FN) = recall = sensitivity
FPR = FP / (FP + TN) = 1 - specificity

Algorithm: sort examples by predicted probability (descending). At each unique predicted score, threshold there and compute TP, FP, TPR, FPR. Plot (FPR, TPR) for each threshold. The curve starts at (0, 0) when tau is very high (predict almost no positives) and reaches (1, 1) when tau is very low (predict almost all positives).

### AUC-ROC
AUC (Area Under the Curve) is the area under the ROC curve. It ranges from 0.5 to 1.0:
- AUC = 0.5: random classifier, no discrimination ability
- AUC = 1.0: perfect classifier, all positives ranked above all negatives
- AUC = 0.7 to 0.8: good discrimination
- AUC < 0.5: classifier is worse than random (inverted labels)

Interpretation: AUC is the probability that the model assigns a higher predicted probability to a random positive example than to a random negative example. It is threshold-independent; it measures how well the model ranks positives above negatives regardless of where you set tau.

Computation from scratch: sort predicted scores in descending order. For each threshold, compute TPR and FPR. Use trapezoidal rule to integrate: area += (FPR[i] - FPR[i-1]) * (TPR[i] + TPR[i-1]) / 2 for each pair of consecutive points.

Source: vault/.../09-model-evaluation/docs/en.md, "Classification Metrics: AUC-ROC" section.

### Precision-Recall Curve
For imbalanced data, ROC can be misleading because it plots against FPR (which involves TN, the majority class). The PR curve plots precision (y-axis) against recall (x-axis), both of which involve only the positive class and the predictions.

Algorithm: same sorting and threshold sweep as ROC. At each threshold, compute precision = TP/(TP+FP) and recall = TP/(TP+FN). Plot (recall, precision). The curve is more sensitive to imbalance because it focuses on positives only.

Use PR curve when: the positive class is rare (imbalanced), or when you care much more about the minority class than the majority.

Source: vault/.../09-model-evaluation/docs/en.md, discussion of imbalanced data and class imbalance problem.

## Regression metrics

### Mean Squared Error (MSE) and Root Mean Squared Error (RMSE)
MSE = mean((y_true - y_pred)^2) = sum((y_true - y_pred)^2) / n

Penalizes large errors quadratically. A single error of magnitude 2 contributes (2^2) = 4 to the sum; two errors of magnitude 1 each contribute 1 + 1 = 2. MSE is sensitive to outliers because the squared term amplifies large deviations.

RMSE = sqrt(MSE)

Same units as the target variable, making it more interpretable than MSE. RMSE also penalizes large errors more than small ones (quadratic penalty), just like MSE.

Source: vault/.../09-model-evaluation/docs/en.md, "Regression Metrics: MSE, RMSE" section.

### Mean Absolute Error (MAE)
MAE = mean(|y_true - y_pred|) = sum(|y_true - y_pred|) / n

Treats all errors linearly. An error of magnitude 2 contributes 2, and two errors of magnitude 1 contribute 1 + 1 = 2. More robust to outliers than MSE/RMSE because large deviations are not squared. Use when you want each unit of error to count equally, or when data contains outliers you do not want to over-emphasize.

Source: vault/.../09-model-evaluation/docs/en.md, "Regression Metrics: MAE" section.

### R-squared (Coefficient of Determination)
R^2 = 1 - SS_res / SS_tot

where SS_res = sum((y_true - y_pred)^2) and SS_tot = sum((y_true - mean_y)^2), with mean_y = sum(y_true) / n.

R^2 is the fraction of variance in the target that the model explains. Ranges from negative infinity to 1.0:
- R^2 = 1.0: perfect fit, model explains all variance
- R^2 = 0.0: model is no better than always predicting the training mean
- R^2 < 0.0: model is worse than predicting the mean (negative = very bad fit)

Interpretation: if R^2 = 0.75, the model explains 75% of the variance in the target; 25% remains unexplained by this model.

Source: vault/.../09-model-evaluation/docs/en.md, "Regression Metrics: R-squared" section.

## Probability and threshold framing

From lesson 06 (Probability and Distributions), the connection between predicted probability and decision threshold:

A classifier outputs a probability p = P(y=1|x), the probability that x belongs to the positive class, given the model's learned weights. This is a Bernoulli distribution: P(y=1) = p, P(y=0) = 1-p.

The decision threshold tau is arbitrary. Standard convention is tau = 0.5. Changing tau shifts the FP/FN tradeoff:
- tau = 0.0: predict 1 for all examples (maximum recall, minimum precision, maximum FP)
- tau = 0.5: standard, balanced threshold
- tau = 1.0: predict 1 for almost no examples (minimum recall, maximum precision, minimum FP)

On imbalanced data (base rate imbalance), the optimal tau is often not 0.5. If 5% of examples are positive, a model trained with equal weights for FP and FN may benefit from raising tau to avoid majority-class predictions dominating the loss. Conversely, if FN is much more costly (e.g., medical diagnosis), lower tau to catch more positives even if FP increases.

Source: vault/.../06-probability-and-distributions/docs/en.md, "Bernoulli" distribution and softmax sections; vault/.../09-model-evaluation/docs/en.md, "Class imbalance" discussion.

## Source code shape

vault/.../09-model-evaluation/code/evaluation.py implements:
- confusion_matrix(y_true, y_pred): returns TP, TN, FP, FN by counting matches
- accuracy, precision, recall, f1_score: each computed from confusion matrix
- roc_curve(y_true, y_scores): returns FPR list, TPR list, threshold list by sweeping thresholds
- auc_roc(y_true, y_scores): computes area under ROC curve using trapezoidal integration
- mse, rmse, mae, r_squared: compute regression metrics by summing squared/absolute errors
- learning_curve: plots training and validation scores across increasing dataset sizes
- SimpleLogistic and SimpleLinearRegression classes with fit/predict methods
- Data generators: make_classification_data, make_imbalanced_data, make_regression_data
- Full demo in __main__: trains on balanced and imbalanced data, reports all metrics

vault/.../06-probability-and-distributions/code/probability.py implements:
- bernoulli_pmf, categorical_pmf, poisson_pmf, uniform_pdf, normal_pdf: PDFs/PMFs from scratch
- softmax, log_softmax, cross_entropy_loss for classification
- Sampling functions: sample_bernoulli, sample_categorical, sample_normal_box_muller
- Central Limit Theorem demonstration
- Expected value and variance computation

## Worked numeric examples

From vault/.../09-model-evaluation/docs/en.md, line 504-609:

Balanced classification (300 examples, ~50% positive):
- Train/val/test split: train 180, val 60, test 60 examples
- SimpleLogistic trained on train set
- Test results on 60 test examples:
  - Confusion matrix example: TP=27, TN=28, FP=3, FN=2 (illustrative; exact values depend on seed)
  - Accuracy = (27+28)/(27+28+3+2) = 55/60 = 0.9167
  - Precision = 27/(27+3) = 27/30 = 0.9000
  - Recall = 27/(27+2) = 27/29 = 0.9310
  - F1 = 2*0.9*0.9310/(0.9+0.9310) = 0.9150 (approx)
  - AUC-ROC computed from predicted probabilities (not hard predictions)

Imbalanced classification (300 examples, 5% positive, 95% negative):
- Class distribution: 15 positive, 285 negative
- Baseline (always predict 0): accuracy = 285/300 = 0.95, precision = 0/0 (undefined or 0), recall = 0/15 = 0.0, F1 = 0.0
- This illustrates why accuracy lies on imbalanced data
- A trained model that correctly identifies some positives will have much lower accuracy than the baseline but positive precision, recall, and F1

Regression (200 examples):
- SimpleLinearRegression trained on training data, evaluated on test data (40 examples typical)
- Example metrics (illustrative):
  - MSE = 4.5 (mean squared error in target units squared)
  - RMSE = 2.12 (same units as target)
  - MAE = 1.8 (mean absolute error)
  - R^2 = 0.82 (model explains 82% of variance)
- Baseline (always predict training mean): typically R^2 = 0.0, RMSE approximately the target std

K-fold cross-validation (k=5, 300 balanced examples):
- Fold scores on SimpleLogistic: [0.9167, 0.9000, 0.9500, 0.8833, 0.9333] (illustrative)
- Mean = 0.9167 (+/- 0.0228)

Stratified K-fold cross-validation (k=5, same data):
- Fold scores typically closer together than non-stratified, especially on imbalanced data
- Preserves class ratio (50% positive in each fold)

Source: vault/.../09-model-evaluation/docs/en.md, lines 504-629 (full demo code with concrete values).

## Out of scope / hold for later

Feature engineering, feature selection, and feature importance (belong to module M6 or later).
Portfolio evaluation, model comparison, and production monitoring (belong to module M7 or later).
Deep probability theory, Bayes' theorem, inference, and conjugate priors (covered in lesson 06, not scope here; this module uses only Bernoulli and threshold reasoning).
Advanced resampling techniques (SMOTE, class weights) for imbalance (mentioned but not detailed; focus is on threshold and metric choice as primary tools).
Multi-class metrics (one-vs-rest, macro/micro averaging) and ranking metrics (NDCG, MAP) for ranking problems (beyond binary scope).
