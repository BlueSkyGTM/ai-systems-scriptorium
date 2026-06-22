# Fitting a Line and Its Limits: Regression Fundamentals and the Bias-Variance Tradeoff

**Provenance:** Extracted from vault/ai-engineering-from-scratch/phases/02-ml-fundamentals/
  - Lesson 02-linear-regression/docs/en.md
  - Lesson 03-logistic-regression/docs/en.md
  - Lesson 10-bias-variance/docs/en.md

---

## Linear Regression

### The Model

The core linear model assumes a linear relationship between input x and output y:

```
Single feature: y = wx + b
Multiple features: y = w1*x1 + w2*x2 + ... + wn*xn + b
Vector form: y = w^T * x + b
```

Where w is the weight (or weights vector) and b is the bias/intercept term. Goal: find w and b that minimize prediction error across all training examples.

*Source: Lesson 02-linear-regression, "The Concept" section.*

### Mean Squared Error (MSE) Loss

The standard cost function for linear regression:

```
MSE = (1/n) * sum((y_predicted - y_actual)^2)
```

MSE penalizes large errors quadratically (an error of 10 is 100x worse than an error of 1). It is smooth and differentiable everywhere, enabling straightforward optimization.

*Source: Lesson 02-linear-regression, "The Cost Function" section.*

### Gradient of MSE

For the linear model y_hat = wx + b, the gradients are:

```
dMSE/dw = (2/n) * sum((y_hat - y) * x)
dMSE/db = (2/n) * sum(y_hat - y)
```

These gradients specify the direction and magnitude to move each parameter to reduce cost. The update rule in gradient descent is:

```
w = w - learning_rate * dMSE/dw
b = b - learning_rate * dMSE/db
```

Learning rate controls step size; typical values are 0.01, 0.001, or 0.0001.

*Source: Lesson 02-linear-regression, "Gradient Descent" section.*

### Normal Equation (Closed-Form Solution)

For linear regression, there exists a direct formula giving optimal weights in one step without iteration:

```
w = (X^T * X)^(-1) * X^T * y
```

This inverts a matrix to solve for w. It works well for small datasets but is O(n^3) in the number of features, so gradient descent is preferred for large datasets.

*Source: Lesson 02-linear-regression, "The Normal Equation" section.*

### R-Squared Score

A scale-independent measure of fit quality:

```
R^2 = 1 - (sum of squared residuals) / (sum of squared deviations from mean)
    = 1 - SS_res / SS_tot
```

Interpretation:
- R^2 = 1.0: perfect predictions
- R^2 = 0.0: model is no better than predicting the mean
- R^2 < 0.0: model is worse than predicting the mean

*Source: Lesson 02-linear-regression, "R-Squared Score" section.*

---

## Logistic Regression

### The Sigmoid Function

Logistic regression applies sigmoid to a linear score to map output to [0, 1]:

```
sigmoid(z) = 1 / (1 + e^(-z))
```

Properties:
- Output always between 0 and 1
- When z large and positive, sigmoid approaches 1
- When z large and negative, sigmoid approaches 0
- When z = 0, sigmoid = 0.5
- Smooth and differentiable everywhere
- Derivative: sigmoid'(z) = sigmoid(z) * (1 - sigmoid(z))

*Source: Lesson 03-logistic-regression, "The Sigmoid Function" section.*

### Why Linear Regression Fails for Classification

Linear regression on binary labels produces unbounded predictions (e.g., -0.5, 1.7). Classification needs:
1. Outputs between 0 and 1 (probabilities)
2. A sharp decision boundary
3. Robustness to outliers far from the boundary

Sigmoid provides all three. MSE with sigmoid creates a non-convex cost surface with many local minima, so a different loss function is needed.

*Source: Lesson 03-logistic-regression, "Why Linear Regression Fails" section.*

### Binary Cross-Entropy Loss

The loss function for logistic regression:

```
Loss = -(1/n) * sum(y * log(p) + (1-y) * log(1-p))
```

Where p = sigmoid(wx + b) is the predicted probability.

Behavior:
- When y=1 and p close to 1: log(1) ~ 0, loss near 0 (correct)
- When y=1 and p close to 0: log(0) ~ -infinity, loss huge (wrong)
- When y=0 and p close to 0: log(1) ~ 0, loss near 0 (correct)
- When y=0 and p close to 1: log(0) ~ -infinity, loss huge (wrong)

This loss is convex for logistic regression, guaranteeing a single global minimum.

*Source: Lesson 03-logistic-regression, "Binary Cross-Entropy Loss" section.*

### Gradient for Logistic Regression

The gradients for binary cross-entropy with sigmoid:

```
dL/dw = (1/n) * sum((p - y) * x)
dL/db = (1/n) * sum(p - y)
```

These look identical to linear regression gradients. The key difference is p = sigmoid(wx + b) instead of p = wx + b. The sigmoid introduces the nonlinearity while the update rule remains simple.

*Source: Lesson 03-logistic-regression, "Gradient Descent for Logistic Regression" section.*

### Decision Threshold

Default threshold is 0.5:

```
if sigmoid(wx + b) >= 0.5: predict 1
else: predict 0
```

Since sigmoid(z) = 0.5 when z = 0, the decision boundary is where wx + b = 0. This is a linear boundary in feature space. The threshold is tunable to trade precision for recall.

*Source: Lesson 03-logistic-regression, "The Decision Boundary" and "Threshold Tuning" sections.*

---

## Bias-Variance Tradeoff

### Definitions

**Bias:** Systematic error from wrong assumptions. The gap between the average model prediction (over many training sets) and the true value. High bias means underfitting: the model is too rigid to capture the real pattern.

```
High bias (underfitting):
  Model consistently predicts roughly the same wrong thing
  Training error: HIGH
  Test error: HIGH
  Gap between them: SMALL
```

**Variance:** Sensitivity to training data. How much predictions change when trained on different subsets of the same distribution. High variance means overfitting: the model fits noise in the training data.

```
High variance (overfitting):
  Model fits training data perfectly but fails on new data
  Training error: LOW
  Test error: HIGH
  Gap between them: LARGE
```

*Source: Lesson 10-bias-variance, "Bias" and "Variance" sections.*

### The Bias-Variance Decomposition

For any point x, expected prediction error under squared loss decomposes exactly:

```
Expected Error = Bias^2 + Variance + Irreducible Noise

where:
  Bias^2   = (E[f_hat(x)] - f(x))^2
  Variance = E[(f_hat(x) - E[f_hat(x)])^2]
  Noise    = E[(y - f(x))^2] = sigma^2
```

- f(x) is the true function
- f_hat(x) is the model's prediction
- E[...] is expectation over different training sets
- y is the observed label (true function plus noise)

The noise term is irreducible. No model can do better than sigma^2 on noisy data.

*Source: Lesson 10-bias-variance, "The Decomposition" section.*

### Model Complexity and the U-Curve

As model complexity increases:

| Complexity | Bias | Variance | Total Error |
|-----------|------|----------|-------------|
| Too low | HIGH | LOW | HIGH (underfitting) |
| Just right | MODERATE | MODERATE | LOWEST |
| Too high | LOW | HIGH | HIGH (overfitting) |

The sweet spot balances bias and variance. Push complexity down and variance drops but bias rises. Push complexity up and bias drops but variance rises.

*Source: Lesson 10-bias-variance, "Model Complexity vs Error" section.*

### Train/Test Error Gap as a Diagnostic

The gap between training error and test error reveals which regime you are in:

- **Large gap, low train error**: high variance (overfitting). Model fits training noise.
- **Small gap, both high**: high bias (underfitting). Model cannot capture pattern.
- **Small gap, both low**: good fit. Model generalizes.
- **Large gap, still shrinking with more data**: variance problem solvable by more data.
- **Small gap, both high and flat**: bias problem not fixable by more data.

*Source: Lesson 10-bias-variance, "Diagnosing Your Model" section.*

### Learning Curves

Learning curves plot training error and validation error as training set size grows. They reveal whether a model is data-limited or capacity-limited.

For high-bias models (e.g., degree-1 polynomial):
- Both curves converge to HIGH error
- Gap stays small
- More data does NOT help

For high-variance models (e.g., degree-12 polynomial on small data):
- Training error stays low
- Test error stays high
- Gap is large but shrinks with more data

For good-fit models:
- Both curves converge to LOW error
- Gap is small
- Model generalizes

*Source: Lesson 10-bias-variance, "Learning Curves" section.*

### Regularization as Bias-Variance Control

Regularization deliberately increases bias to reduce variance. It constrains the model so it cannot chase noise.

**L2 (Ridge) Regularization:**

```
Cost = MSE + lambda * sum(w_i^2)
```

Shrinks all weights toward zero. Keeps all features but reduces their influence. Higher lambda means more constraint, more bias, less variance.

**L1 (Lasso):**

Pushes some weights exactly to zero. Performs automatic feature selection.

**Dropout:**

Randomly disables neurons during training. Forces redundant representations.

**Early Stopping:**

Stops training before the model fully fits training data.

The regularization strength directly controls where you sit on the bias-variance curve.

*Source: Lesson 02-linear-regression, "Regularization Preview"; Lesson 10-bias-variance, "Regularization as Bias-Variance Control" section.*

---

## Source Code Shape

### Linear Regression Classes

**LinearRegression** (gradient descent):
- Constructor: `__init__(learning_rate=0.01)`
- Methods: `predict(X)`, `compute_cost(X, y)`, `compute_gradients(X, y)`, `fit(X, y, epochs=1000, print_every=200)`, `r_squared(X, y)`
- Maintains: `w`, `b`, `lr`, `cost_history`
- Default learning_rate: 0.01; typical use: 0.005
- Default epochs: 1000

**LinearRegressionNormal** (closed-form):
- Constructor: `__init__()`
- Methods: `fit(X, y)`, `predict(X)`, `r_squared(X, y)`
- No learning rate or iteration; solves in one call

**MultipleLinearRegression** (multi-feature):
- Constructor: `__init__(n_features, learning_rate=0.01)`
- Methods: `predict_single(x)`, `predict(X)`, `compute_cost(X, y)`, `fit(X, y, epochs=1000, print_every=200)`, `r_squared(X, y)`
- Uses weight list of length n_features

**PolynomialRegression**:
- Constructor: `__init__(degree, learning_rate=0.01)`
- Methods: `make_features(X)`, `predict(X)`, `fit(X, y, epochs=1000, print_every=200)`, `r_squared(X, y)`
- Expands x -> [x, x^2, ..., x^degree]

**RidgeRegression**:
- Constructor: `__init__(n_features, learning_rate=0.01, alpha=1.0)`
- Methods: `predict_single(x)`, `predict(X)`, `fit(X, y, epochs=1000, print_every=200)`
- Alpha controls L2 penalty strength. Default alpha: 1.0

*Source: Lesson 02-linear-regression, code/linear_regression.py*

### Logistic Regression Classes

**LogisticRegression** (binary):
- Constructor: `__init__(n_features, learning_rate=0.01)`
- Methods: `predict_proba(x)`, `predict(x, threshold=0.5)`, `compute_loss(X, y)`, `fit(X, y, epochs=1000, print_every=200)`, `accuracy(X, y)`
- Maintains: `weights`, `bias`, `lr`, `loss_history`
- Uses sigmoid for probability; default threshold 0.5

**ClassificationMetrics**:
- Constructor: `__init__(y_true, y_pred)` - computes TP, TN, FP, FN
- Methods: `accuracy()`, `precision()`, `recall()`, `f1()`, `print_confusion_matrix()`, `print_report()`

**SoftmaxRegression** (multi-class):
- Constructor: `__init__(n_features, n_classes, learning_rate=0.01)`
- Methods: `softmax(scores)`, `predict_proba(x)`, `predict(x)`, `fit(X, y, epochs=1000, print_every=200)`, `accuracy(X, y)`
- Maintains weight matrix of shape (n_classes, n_features) and biases vector

*Source: Lesson 03-logistic-regression, code/logistic_regression.py*

### Bias-Variance Utilities

**true_function(x)**: returns sin(1.5*x) + 0.5*x (true underlying function for experiments)

**generate_data(n_samples=30, noise_std=0.5, x_range=(-3, 3), seed=None)**: draws n_samples from uniform distribution over x_range, adds Gaussian noise with given std

**fit_polynomial(x_train, y_train, degree, lam=0.0)**: fits polynomial of given degree; if lam > 0, applies Ridge penalty with lambda=lam. Uses np.linalg.lstsq or np.linalg.solve depending on lam.

**predict_polynomial(x, w)**: evaluates polynomial with weights w at points x

**bias_variance_decomposition(degrees, n_bootstrap=200, n_train=30, noise_std=0.5, n_test=100, lam=0.0)**: runs bootstrap experiment for each degree. Returns dictionary mapping degree to {bias_sq, variance, total_error, noise}.

Key numeric defaults:
- n_bootstrap: 200 (number of bootstrap samples)
- n_train: 30 (training set size per bootstrap)
- n_test: 100 (test set size for computing error)
- noise_std: 0.5
- lam: 0.0 (no regularization by default)

*Source: Lesson 10-bias-variance, code/bias_variance.py*

---

## Worked Numeric Examples

### Linear Regression (Lesson 02)

Training data: 100 samples generated from y = 3.0*x + 7.0 + Gaussian(0, 2.0) noise, x uniform in [0, 10].

**Gradient descent fit** (learning_rate=0.005, 1000 epochs):
- Learned: y = 2.9589x + 7.2123 (approximately; from output)
- True: y = 3.0x + 7.0
- R-squared: approximately 0.95

**Normal equation fit** (same data):
- Produces identical w and b to gradient descent
- No iteration needed

**Multiple regression** (3 features: house size, bedrooms, age):
- 100 samples generated from: price = 50*size + 10000*bedrooms - 1000*age + 50000 + noise
- Features standardized before fitting
- R-squared (standardized): approximately 0.95

**Polynomial regression** (degree 2 vs degree 5):
- True function: y = 0.5*x^2 - 2*x + 3
- 50 data points, normalized inputs and outputs
- Degree 2 fit: R-squared ~0.98 (fits true curve well)
- Degree 5 fit: R-squared slightly higher but risks overfitting on new data

**Ridge regression** (alpha=0.1, 3 features):
- Same standardized data as multiple regression
- Ridge weights smaller (shrunk toward zero) compared to plain weights
- L2 penalty: alpha * sum(w_i^2) = 0.1 * sum(w_i^2)

*Source: Lesson 02-linear-regression, "Build It" section, code/linear_regression.py*

### Logistic Regression (Lesson 03)

Training data: 200 samples (100 per class), 2 features each. Class 0 centered at (2, 2), class 1 centered at (5, 5), both with std 1.0.

**Binary logistic fit** (learning_rate=0.1, 1000 epochs):
- Train accuracy: approximately 0.98
- Test accuracy: approximately 0.97
- Learned weights: approximately [0.5842, 0.6223]
- Learned bias: approximately -2.6853
- Decision boundary: 0.5842*x1 + 0.6223*x2 - 2.6853 = 0

**Threshold tuning** (test set):
- Threshold 0.3: Precision ~0.88, Recall ~1.00, F1 ~0.94
- Threshold 0.5: Precision ~0.97, Recall ~0.96, F1 ~0.96
- Threshold 0.7: Precision ~1.00, Recall ~0.80, F1 ~0.89

**Multi-class softmax** (3 classes, 2 features, 150 samples):
- Train accuracy: approximately 0.99
- Test accuracy: approximately 0.97
- 3 weight vectors (one per class) and 3 biases learned

**Linear vs sigmoid comparison** (binary labels from study hours):
- Linear fit on y in {0, 1} produces predictions outside [0, 1] (e.g., -0.2 at 1 hour, 1.3 at 10 hours)
- Sigmoid fit keeps all predictions in [0, 1]

*Source: Lesson 03-logistic-regression, "Build It" section, code/logistic_regression.py*

### Bias-Variance Decomposition (Lesson 10)

True function: f(x) = sin(1.5*x) + 0.5*x. Noise std: 0.5. Training samples per bootstrap: 30. Bootstrap rounds: 200.

**Polynomial degree sweep** (degrees 1, 2, 3, 5, 7, 10, 15):

Example output row (degree 5):
- Bias^2: ~0.0450
- Variance: ~0.0620
- Noise: 0.2500
- Total Error: ~0.3570

Degrees 1-3: Bias dominates (high, variance low).
Degrees 5-7: Sweet spot (bias and variance balanced).
Degrees 10-15: Variance dominates (bias low, variance high).

**Effect of training set size** (degree 5, fixed):
- n_train=10: Variance much higher, bias unchanged
- n_train=100: Variance reduced significantly, bias stable
- n_train=500: Variance further reduced toward noise floor

More data reduces variance but cannot reduce bias (bias is set by model capacity).

**Regularization sweep** (degree 15, lambda 0.0 to 100):
- lambda=0.0: Bias^2 ~0.05, Variance ~0.55 (high variance)
- lambda=1.0: Bias^2 ~0.10, Variance ~0.15 (balanced)
- lambda=100: Bias^2 ~0.40, Variance ~0.01 (high bias, constrained)

Optimal lambda is around 1.0-10.0 for this setup, depending on exact noise level.

**Learning curves** (degree 5):
- Small n_train (10-30): Train error low, test error high, gap large
- Large n_train (100+): Gap shrinks, both converge to modest error
- Suggests more data would continue to help (variance-limited problem)

*Source: Lesson 10-bias-variance, "Build It" section; code/bias_variance.py demo outputs*

---

## Out of Scope / Hold for Later

The following topics are mentioned in the vault lessons but deferred for other modules:

1. **Lasso regression (L1 regularization)**: Lesson 02 mentions it but defers depth to a later lesson. The key difference from Ridge: pushes weights to exactly zero (feature selection) rather than just shrinking them.

2. **Support Vector Machines (SVMs)**: Not covered. Would be introduced in a kernel methods module.

3. **Regularization depth beyond Ridge**: Elastic Net (L1 + L2), dropout variants, batch normalization. Lesson 02 and 10 preview but do not detail.

4. **Double descent phenomenon**: Lesson 10 mentions modern research (2019+) showing that error can decrease again past the interpolation threshold if you increase model capacity far enough. This is noted as incomplete classical theory but not fully developed.

5. **Cross-validation and hyperparameter tuning**: Learning curves use it conceptually, but detailed CV strategies (k-fold, stratified, nested) are held for another module.

6. **Confusion matrix advanced uses**: ROC curves, AUC, per-class metrics for multi-class. Lesson 03 covers binary confusion matrix only.

7. **Feature engineering and polynomial feature expansion**: Polynomial regression covers the math but not strategies for feature selection or transformation in production.

8. **Numerical stability** in sigmoid/softmax: Clamping and max-subtraction tricks are implemented in code but not theoretically analyzed.
