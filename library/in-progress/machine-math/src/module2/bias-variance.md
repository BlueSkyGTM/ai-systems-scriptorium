# The Bias-Variance Tradeoff

The lowest training error you can achieve is not the goal. A model that memorizes training noise
will always beat a reasonable model on its own training data, and will fail on everything else.
The question is not "how low can train error go?" but "how large is the gap between train and test
error?" That gap is the variance, and learning to read it is the skill.

## Bias and Variance Are Opposite Failure Modes

**Bias** is the systematic error that comes from a model too rigid to capture the true pattern.
At the extreme, a degree-1 polynomial fit to a sinusoidal signal cannot bend; it is underfitting.
Train error and test error are both high. The gap between them is small, because the model is
underfitting everywhere, not just on training data.

**Variance** is the sensitivity to which training samples you happened to see. At the extreme, a
degree-15 polynomial fit to 45 noisy points will chase every kink and outlier in those 45 points.
Train error is very low. Test error is high. The gap is the signal: the model is fitting noise, and
noise does not generalize.

The decomposition is exact. For squared loss, expected prediction error at any point splits into:

```
Expected Error = Bias^2 + Variance + Irreducible Noise
```

The noise floor is fixed by the data generation process. No model beats it. Everything above it
is either bias or variance, and pushing one down tends to push the other up.

## The Experiment: Train a Line, Then a Degree-15 Polynomial

The setup: 60 points drawn from `y = sin(x) + noise` (noise std 0.3), split 75/25 into 45
training points and 15 test points. Fit `ml.linreg.LinearRegression` on polynomial features of
rising degree. Measure train MSE and test MSE.

The results:

| Degree | Train MSE | Test MSE |
|--------|-----------|----------|
| 1 | 0.272 | 0.611 |
| 3 | 0.066 | 2.549 |
| 5 | 0.062 | 3.207 |
| 9 | 0.067 | 4.573 |
| 15 | 0.057 | 4.795 |

Train error falls from 0.272 at degree 1 to 0.057 at degree 15: a 79% reduction. Test error climbs
from 0.611 at degree 1 to 4.795 at degree 15: a 685% increase, or 7.8x the degree-1 baseline. The
gap at degree 15 is not an accident; it is a direct measurement of the model fitting training noise.

At degree 1 (underfitting): the gap is 0.339. The model is too rigid; both errors are elevated.
The high train error is the tell.

At degree 15 (overfitting): the gap is 4.738. Train error is at its lowest. The model has memorized
the 45 training points so thoroughly that it has nothing useful to say about the 15 held-out ones.
The high test error is the tell.

Somewhere between degree 1 and degree 15 is the sweet spot. You find it by reading test error on
held-out data, not by watching train error fall.

## The Gap Is the Diagnostic

Azure Machine Learning's AutoML evaluation guidance makes this operational: `log_loss` (cross-entropy)
is defined as the "loss function used in (multinomial) logistic regression" and its objective is
"closer to 0 the better" ([learn.microsoft.com](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-understand-automated-ml)).
The same principle applies to regression: you evaluate on a held-out set, not the training set,
because the training set cannot tell you anything about generalization.

The diagnostic map is direct:

- **Both errors high, small gap:** high bias. The model cannot represent the pattern. Adding more
  data does not help; adding model capacity does.
- **Low train error, high test error, large gap:** high variance. The model memorizes training
  noise. More data helps (it dilutes the noise); less capacity also helps.
- **Both errors low, small gap:** good fit. Stop here.

## The Same Knob You Saw in Module 1

k-NN's `k` is a bias-variance lever. At `k=1`, the model traces every kink in the training data:
low bias, high variance, the decision boundary fits every outlier. At `k=N` (all training
points), the boundary is a flat majority vote: high bias, zero variance. The right `k` is the one
where test error is lowest on a held-out validation set.

Polynomial degree is the same knob. So is the regularization strength `lambda` in Ridge regression:
higher `lambda` shrinks weights toward zero, trading variance for bias. The underlying tradeoff is
the same across all three. What changes is the parameter name and the model family.

This is the practical test that every model faces. Lower training error is always achievable:
add capacity, add features, remove regularization. But the model that ships is the one that
generalizes, and generalization is read from the gap, not from the training curve.

## Core Concepts

- Bias and variance are opposite failure modes: high bias means train and test error are both high
  (the model is too rigid); high variance means train error is low but test error is high (the
  model fits noise).
- The gap between training error and test error is the direct measurement of variance: a 7.8x rise
  in test error from degree 1 to degree 15 is not a theoretical concern, it is a number in your
  output table.
- The sweet spot is found by reading held-out error across model complexity: you cannot see it
  from the training curve alone, because training error falls monotonically with capacity.
- The same tradeoff governs k-NN's k, polynomial degree, and regularization strength; the
  parameter changes but the diagnostic does not.

<div class="claude-handoff" data-exercise="exercises/module2/bias-variance/">

**Build It in Claude Code**: Write the overfitting experiment in `exercises/module2/bias-variance/`.
Use `ml.linreg.LinearRegression` to fit rising polynomial degrees (1, 3, 5, 9, 15) on a 1-D
noisy sinusoid (60 points, 75/25 split). Assert that degree-15 train error is lower than degree-1
train error and that degree-15 test error is higher than degree-1 test error. The gate at
`exercises/module2/bias-variance/test_bias_variance.py` must pass green with
`python -m pytest exercises/module2/bias-variance`. No new `ml/` package file is needed; this
exercise uses `ml.linreg` directly.

</div>
