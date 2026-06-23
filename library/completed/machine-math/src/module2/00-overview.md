# Module 2: Fitting a Line (and Its Limits)

Module 1 stored the data. Every prediction in k-NN required the full training set at query
time: measure distance, rank neighbors, take a vote. No parameters were ever learned.
This module changes that. You will fit parameters by minimizing a loss, and you will
understand the engine that does the fitting.

That engine is gradient descent. The derivative of a loss surface tells you which direction
is uphill; the optimizer takes a step the opposite way, scaled by a learning rate. Do that
enough times on a convex loss and you reach the bottom. The bottom is where your model
lives.

## Four Lessons, One Thread

The module runs in order. Each lesson stands on the one before it.

**Gradient Descent: Rolling Downhill** builds the optimizer itself. One clean function,
`gradient_descent`, accepts any gradient function and any starting point. You verify it on
`f(theta) = (theta - 3)^2`, a bowl with one bottom at `theta = 3`. The exercise produces
`ml/gradient_descent.py`, the shared optimizer every subsequent model in this package reuses.

**Linear Regression: Fitting the Line** puts the first model on top of the optimizer.
The model is `y = w^T x + b`; the loss is mean squared error; the gradient is the descent
signal. You verify the gradient-descent solution against the normal equation (the
closed-form shortcut) and against scikit-learn, and confirm all three land at the same
coefficients. The exercise produces `ml/linreg.py`, which imports the optimizer from
`ml.gradient_descent` directly.

**Logistic Regression** swaps the output for a sigmoid and the loss for binary
cross-entropy. The gradient update rule looks identical to linear regression; the
nonlinearity lives entirely in the output. Gradient descent generalizes to this case
without any change to the optimizer.

**The Bias-Variance Tradeoff** names the limit. Lower training error is not the goal.
A model that fits the training data too well fails on new data. The lesson measures
bias and variance separately on polynomial regressors and shows the U-shaped error
curve that defines the sweet spot.

## The Thread

Gradient descent is the engine. Linear and logistic regression are the first two models
that ride it. Bias-variance is the limit: the noise floor in your data is irreducible, and
the model that chases training error past that floor is learning noise, not signal.

## What Is Given

Small, clean synthetic datasets generated with a fixed seed, so your numbers match the
lesson's exactly. scikit-learn loads data and serves as the oracle in acceptance tests:
your from-scratch implementation must agree with it numerically. All algorithm logic
is NumPy.

## What Is Deliberately Out of Scope

**Regularization depth** is held for later. Ridge and Lasso appear briefly at the
end of the bias-variance lesson to name the mechanism, but the full treatment belongs
in the module that covers regularized linear models and cross-validation together.

**Neural network training** uses gradient descent through a computation graph, with
the chain rule threading gradients back through every layer. That story is a separate
book. This module covers the same optimizer on a single linear output so the mechanics
are clear before the graph grows deep.
