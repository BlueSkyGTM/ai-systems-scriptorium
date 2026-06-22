# Calculus and Optimization for Linear Regression

## Provenance

Extracted from:
- `vault/ai-engineering-from-scratch/phases/01-math-foundations/04-calculus-for-ml/docs/en.md` (derivatives, gradients, chain rule, Taylor series)
- `vault/ai-engineering-from-scratch/phases/01-math-foundations/05-chain-rule-and-autodiff/docs/en.md` (chain rule deep dive)
- `vault/ai-engineering-from-scratch/phases/01-math-foundations/08-optimization/docs/en.md` (gradient descent, momentum, Adam, learning rates)
- `vault/ai-engineering-from-scratch/phases/01-math-foundations/18-convex-optimization/docs/en.md` (convexity, Hessian, why neural networks work despite non-convexity)

Scope: Core material for "Fitting a Line (and Its Limits)" — derivatives and slopes, partial derivatives and gradients, the chain rule, the gradient descent update rule, learning rate behavior, convexity and global minima, and the closed-form solution vs iterative optimization.

## Definitions and Formulas

### Derivative (univariate)

**Definition:** The rate of change of a function at a point.

Formal definition (limit form):
```
f'(x) = lim   f(x + h) - f(x)
        h->0  -----------------
                     h
```

**Geometric meaning:** The slope of the tangent line to the graph of f at the point x.

**Numerical approximation (central difference):**
```
f'(x) ≈ f(x + h) - f(x - h)
        ---------------------   , where h = 1e-7 works well in practice
                  2h
```

**Example: f(x) = x^2**

| x | f(x) | f'(x) = 2x | meaning |
|---|------|-----------|---------|
| -2 | 4 | -4 | slope tilts left (negative rate of change) |
| 0 | 0 | 0 | flat, at the bottom |
| 2 | 4 | 4 | slope tilts right (positive rate of change) |

[Source: 04-calculus-for-ml]

### Partial derivative (multivariate)

**Definition:** The derivative of a function with respect to one variable, holding all others constant.

For a function f(x, y, z):
```
df/dx = partial derivative w.r.t. x (treat y, z as constants)
df/dy = partial derivative w.r.t. y (treat x, z as constants)
df/dz = partial derivative w.r.t. z (treat x, y as constants)
```

**Example: f(x, y) = x^2 + 3xy + y^2**
```
df/dx = 2x + 3y    (treat y as constant)
df/dy = 3x + 2y    (treat x as constant)
```

**Interpretation:** If I nudge just the weight corresponding to variable i, how much does the loss change?

[Source: 04-calculus-for-ml]

### Gradient (vector of partial derivatives)

**Definition:** The vector collecting all partial derivatives of a function.

For f(x, y, z):
```
grad f = [df/dx, df/dy, df/dz]
```

**Geometric meaning:** Points in the direction of steepest ascent. The negative gradient points toward steepest descent.

**Example: f(x, y) = x^2 + y^2 at point (1, 1)**
```
grad f = [2x, 2y] = [2, 2]

This vector points away from the minimum at (0, 0).
The negative gradient [-2, -2] points toward it (downhill).
```

[Source: 04-calculus-for-ml]

### Chain Rule

**Statement:** If y = f(g(x)), then:
```
dy/dx = dy/dg * dg/dx = f'(g(x)) * g'(x)
```

**Interpretation:** Multiply the local derivatives along the chain.

**Example: y = (3x + 1)^2**
```
Outer function: f(u) = u^2,      f'(u) = 2u
Inner function: g(x) = 3x + 1,   g'(x) = 3

dy/dx = 2(3x + 1) * 3 = 6(3x + 1)

At x = 1:  dy/dx = 6(3*1 + 1) = 6*4 = 24
```

**Multivariate chain rule (for neural networks):** When a variable fans out through multiple operations, sum the contributions. Backpropagation is the chain rule applied systematically through a computation graph.

[Source: 04-calculus-for-ml, 05-chain-rule-and-autodiff]

### The Gradient Descent Update Rule

**Formula:**
```
w_new = w_old - learning_rate * (df/dw)

For every weight:
  1. Compute the partial derivative of loss with respect to that weight
  2. Multiply by the learning rate (controls step size)
  3. Subtract from the weight
  4. Repeat
```

**In linear regression context:** Adjust weights proportional to how much they contributed to the error.

[Source: 04-calculus-for-ml, 08-optimization]

### Mean Squared Error (MSE) Loss and Its Gradient

**Formula:**
```
Loss = (1/n) * sum_{i=1}^{n} (y_i - pred_i)^2

where pred_i = w*x_i + b
```

**Partial derivatives for linear regression:**
```
dLoss/dw = (2/n) * sum_{i=1}^{n} (pred_i - y_i) * x_i
dLoss/db = (2/n) * sum_{i=1}^{n} (pred_i - y_i)
```

[Source: 04-calculus-for-ml (demo_linear_regression)]

### Convex Function

**Definition (inequality test):** A function f is convex if for any two points x, y in its domain and any t in [0, 1]:
```
f(tx + (1-t)y) <= t*f(x) + (1-t)*f(y)
```

Geometrically: the line segment between any two points on the graph lies above or on the graph (a bowl shape, not a valley with multiple bottoms).

**Second derivative test (1D):** If f''(x) >= 0 for all x, then f is convex.

**Hessian test (multivariate):** If the Hessian matrix H is positive semidefinite (all eigenvalues >= 0) everywhere, then f is convex.

**Examples of convex functions relevant to ML:**
- f(x) = x^2 (parabola)
- f(x) = e^x (exponential)
- Mean Squared Error loss for linear regression
- Logistic regression loss

[Source: 18-convex-optimization]

### Hessian Matrix

**Definition:** The matrix of all second partial derivatives.

For f(x, y):
```
H = | d^2f/dx^2    d^2f/dxdy |
    | d^2f/dydx    d^2f/dy^2 |
```

**Eigenvalue interpretation:**
- All eigenvalues > 0 (positive definite): local minimum (bowl pointing up)
- All eigenvalues < 0 (negative definite): local maximum (bowl pointing down)
- Mixed signs (indefinite): saddle point (curved up in some directions, down in others)

**Condition number:** The ratio (largest eigenvalue) / (smallest eigenvalue). High condition number means an elongated valley (slow gradient descent), low condition number means a well-rounded bowl (fast convergence).

[Source: 04-calculus-for-ml, 18-convex-optimization]

### Taylor Series Approximation

**First-order (linear) approximation:**
```
f(x + h) ≈ f(x) + f'(x)*h
```
This is what gradient descent assumes: that the loss function behaves linearly over a small step.

**Second-order (quadratic) approximation:**
```
f(x + h) ≈ f(x) + f'(x)*h + (1/2)*f''(x)*h^2
```

**Multivariate form:**
```
f(x + h) ≈ f(x) + grad f(x)^T * h + (1/2) * h^T * H(x) * h
```
where H is the Hessian.

**Why it matters:** Gradient descent minimizes the first-order linear approximation. Newton's method minimizes the second-order quadratic approximation. Small learning rates work because the linear approximation is accurate only near the starting point.

[Source: 04-calculus-for-ml]

## Intuitions and Claims

### Why the negative gradient descends

**Claim:** The gradient points toward steepest ascent; the negative gradient points toward steepest descent.

**Why:** The gradient is defined as the vector of partial derivatives. A positive partial derivative means increasing that variable increases the function. Going opposite the gradient means decreasing in all directions (weighted by how much each contributes to the loss).

[Source: 04-calculus-for-ml]

### Learning rate trade-off

**Too large (e.g., lr = 1.0):** The step overshoots the valley. You bounce between walls, oscillating and diverging.

**Too small (e.g., lr = 0.0001):** The step is tiny. Progress is slow; convergence takes thousands of steps.

**Goldilocks zone (e.g., lr = 0.01):** Large enough to make steady progress, small enough to stay roughly on the descent path.

**Typical starting points:** 0.001 for Adam, 0.01 for SGD with momentum.

[Source: 08-optimization]

### Why convexity matters

**Central theorem:** For a convex function, every local minimum is the global minimum.

**Consequences:** 
- Gradient descent cannot get trapped in a bad local minimum
- No need for random restarts or sophisticated learning rate schedules
- The solution is unique (up to flat regions)
- Mathematical convergence guarantees are possible

**In linear regression:** MSE loss is convex in the weights. Gradient descent on MSE always finds the global optimum (or a point arbitrarily close to it, depending on step size and iterations).

[Source: 18-convex-optimization]

### Local vs global minima

**Local minimum:** A point lower than all nearby points, but not necessarily the lowest overall.

**Global minimum:** The lowest point of the function over its entire domain.

**For convex functions:** All local minima are global minima (only one valley).

**For non-convex functions (e.g., neural networks):** Multiple local minima and saddle points exist. However, in high-dimensional spaces, most local minima have loss values close to the global minimum, and saddle points (not bad local minima) are the real obstacle that SGD must escape.

[Source: 18-convex-optimization]

### The closed-form solution vs iterative optimization

**Closed-form (analytical) solution for linear regression:**
```
w = (X^T X)^{-1} X^T y
```
This solves the optimization problem in one step by inverting a matrix. Fast for small datasets.

**Gradient descent (iterative):**
```
For each step:
  compute gradient of loss
  update w = w - lr * gradient
  repeat until convergence
```
Slower per iteration but scales to large datasets. No matrix inversion needed.

**When to use each:**
- Closed-form: Few features, small dataset, need exact solution
- Gradient descent: Many features, large dataset, can afford iterations

[Source: 04-calculus-for-ml, 08-optimization]

### Momentum smooths oscillations

**Idea:** Instead of just following the current gradient, accumulate past gradients into a velocity vector. A ball rolling downhill does not stop and reverse at every bump.

**Formula:**
```
v = beta * v + gradient    (typically beta = 0.9)
w = w - lr * v
```

**Effect:** Dampens oscillations in narrow valleys, allowing faster progress. The accumulated velocity helps push through directions of consistent descent.

[Source: 08-optimization]

### Adam adapts the learning rate per weight

**Idea:** Different weights need different learning rates. Weights with huge gradients should take smaller steps; weights with tiny gradients should take larger steps.

**Method:** Track the first moment (mean of gradients) and second moment (mean of squared gradients) for each weight.

**Result:** A weight with high gradient magnitude gets divided by a large number (small step), a weight with low gradient magnitude gets divided by a small number (large step).

**Default hyperparameters (work for most problems):** lr=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8

[Source: 08-optimization]

### Why neural networks work despite being non-convex

**Paradox:** Neural networks have wildly non-convex loss landscapes (millions of local minima and saddle points). Classical optimization theory says this should fail. Yet SGD finds good solutions reliably.

**Reasons:**
1. **Overwhelming probability of saddle points (not local minima):** In high dimensions (millions of weights), the probability that a critical point is a local minimum is ~2^(-n), where n is the number of parameters. Almost all critical points are saddle points.

2. **Most local minima are good enough:** When local minima do exist, they tend to have loss values close to the global minimum. Getting trapped in a terrible local minimum is extremely unlikely in high dimensions.

3. **Stochastic noise helps escape saddle points:** Mini-batch SGD adds noise that helps escape saddle points (where the gradient is nearly zero but the curvature is mixed).

4. **Overparameterization smooths the landscape:** Networks with more parameters than training examples have smoother, more connected loss surfaces with fewer bad local minima.

[Source: 18-convex-optimization]

## Worked Numeric Examples

### Example 1: Numerical vs Analytical Derivative at x=2

Comparing numerical finite differences against analytical formulas.

| Function | Numerical | Analytical | Error |
|----------|-----------|-----------|-------|
| x^2 | 4.000000 | 4.0 | 0.00e+00 |
| x^3 | 12.000000 | 12.0 | 0.00e+00 |
| sin(x) | -0.416147 | -0.416147 | 2.78e-12 |
| e^x | 7.389056 | 7.389056 | 0.00e+00 |
| 1/x | -0.250000 | -0.25 | 0.00e+00 |

[Source: 04-calculus-for-ml, derivatives.py]

### Example 2: Gradient at a Point

Function: f(x, y) = x^2 + 3xy + y^2 at point (1, 2)

```
Analytical gradient: [df/dx, df/dy] = [2*1 + 3*2, 3*1 + 2*2] = [8, 7]
Numerical gradient:                                            [8.0, 7.0]
```

[Source: 04-calculus-for-ml, derivatives.py]

### Example 3: 1D Gradient Descent on f(x) = x^2

Start x = 5.0, learning rate = 0.1

| Step | x | f(x) |
|------|-------|---------|
| 0 | 5.0000 | 25.000000 |
| 4 | 2.6144 | 6.835092 |
| 8 | 1.3684 | 1.872646 |
| 12 | 0.7180 | 0.515641 |
| 16 | 0.3764 | 0.141772 |
| 19 | 0.2016 | 0.040644 |

Converges to x ≈ 0 (the true minimum).

[Source: 04-calculus-for-ml, derivatives.py]

### Example 4: 2D Gradient Descent on f(x, y) = x^2 + y^2

Start (4.0, 3.0), learning rate = 0.1

| Step | x | y | f(x, y) |
|------|----------|----------|---------|
| 0 | 4.0000 | 3.0000 | 25.000000 |
| 5 | 2.1024 | 1.5768 | 7.100435 |
| 10 | 1.1035 | 0.8276 | 1.982903 |
| 15 | 0.5789 | 0.4342 | 0.553915 |
| 20 | 0.3038 | 0.2279 | 0.154510 |
| 25 | 0.1594 | 0.1195 | 0.043173 |
| 29 | 0.0730 | 0.0548 | 0.008262 |

Converges to (0, 0) (the true minimum).

[Source: 04-calculus-for-ml, derivatives.py]

### Example 5: Hessian Analysis — Saddle vs Bowl

**Saddle function: f(x, y) = x^2 - y^2 at (0, 0)**
```
Hessian: [[2, 0], [0, -2]]
Eigenvalues: 2, -2
Mixed signs --> SADDLE POINT (not a minimum)
```

**Bowl function: f(x, y) = x^2 + y^2 at (0, 0)**
```
Hessian: [[2, 0], [0, 2]]
Eigenvalues: 2, 2
Both positive --> LOCAL MINIMUM
```

**Rosenbrock at minimum (1, 1)**
```
Hessian: [[802, -400], [-400, 200]]
Eigenvalues: 1002.00, -0.00  (approximately both positive)
Positive semidefinite --> Confirms local minimum
```

[Source: 04-calculus-for-ml, derivatives.py; 18-convex-optimization, convex.py]

### Example 6: Taylor Approximation of sin(x) near x=0

| h | True sin(h) | Order 0 | Order 1 | Order 2 |
|---|-------------|---------|---------|---------|
| 0.1 | 0.099833 | 0.000000 | 0.100000 | 0.099833 |
| 0.5 | 0.479426 | 0.000000 | 0.500000 | 0.479167 |
| 1.0 | 0.841471 | 0.000000 | 1.000000 | 0.833333 |
| 2.0 | 0.909297 | 0.000000 | 2.000000 | 1.666667 |

**Insight:** First-order approximation is excellent for small h (h=0.1), excellent for h=0.5, but breaks down for h >= 1.0. This is why gradient descent needs small step sizes (learning rates): the linear approximation only holds locally.

[Source: 04-calculus-for-ml, derivatives.py]

### Example 7: Linear Regression Training

Target: y = 2x + 1, fitted via gradient descent starting from random weights.

| Epoch | w | b | Loss |
|-------|---------|---------|---------|
| 0 | 0.4967 | 0.6476 | 3.206700 |
| 40 | 1.6088 | 0.7568 | 0.018500 |
| 80 | 1.8287 | 0.9003 | 0.000289 |
| 120 | 1.9254 | 0.9572 | 0.000008 |
| 160 | 1.9709 | 0.9824 | 0.000000 |
| 199 | 1.9909 | 0.9948 | 0.000000 |

**Final:** y = 1.99x + 0.99 (converges to true y = 2.00x + 1.00)

[Source: 04-calculus-for-ml, derivatives.py]

### Example 8: Learning Rate Effect on Rosenbrock Function

Minimizing f(x,y) = (1-x)^2 + 100(y-x^2)^2 from (-1.0, 1.0). Target: (1, 1), f = 0.

| Learning Rate | Final x | Final y | Loss | Status |
|---|----------|----------|----------|--------|
| 0.0001 | -0.98934 | 0.98883 | 3.970000 | slow |
| 0.0005 | 1.00029 | 1.00059 | 0.000000 | converged |
| 0.001 | nan | nan | inf | DIVERGED |
| 0.005 | nan | nan | inf | DIVERGED |

**Key insight:** Too small (0.0001): barely moves. Medium (0.0005): converges. Large (0.001+): overshoots and diverges.

[Source: 08-optimization, optimizers.py]

### Example 9: Optimizer Comparison on Rosenbrock

Starting from (-1.0, 1.0), 5000 steps.

| Optimizer | Final x | Final y | Loss | Steps to converge |
|-----------|----------|----------|----------|---------|
| Gradient Descent (lr=0.0005) | 0.999992 | 1.000000 | 0.000000 | ~3500 |
| SGD + Momentum (lr=0.0001, beta=0.9) | 0.992134 | 0.981233 | 0.000156 | slow |
| Adam (lr=0.01) | 1.000000 | 1.000000 | 0.000000 | ~1200 |

**Key insight:** Adam converges fastest due to adaptive per-weight learning rates.

[Source: 08-optimization, optimizers.py]

### Example 10: Newton's Method vs Gradient Descent on Quadratic

Function: f(x, y) = 50x^2 + y^2, start (10, 10), target (0, 0).

**Newton's method (exact for quadratics):**

| Step | x | y | f(x, y) |
|------|----------|----------|---------|
| 0 | 10.00000000 | 10.00000000 | 5100.00000000 |
| 1 | 0.00000000 | 0.00000000 | 0.00000000 |

Converges in 1 step (quadratic convergence near the minimum).

**Gradient descent (lr=0.015):**

| Step | x | y | f(x, y) |
|------|----------|----------|---------|
| 0 | 10.00000000 | 10.00000000 | 5100.00000000 |
| 1 | 9.95150000 | 9.70000000 | 4877.96000000 |
| 10 | 8.42748 | 3.27941 | 3634.48 |
| 100 | 1.61239 | 0.00008 | 129.97 |
| 499 | 0.00000 | 0.00000 | 0.00000 |

Takes ~500 steps (linear convergence, but each step is much cheaper than Newton's inverse Hessian).

[Source: 18-convex-optimization, convex.py]

### Example 11: Convexity Checker Results

Testing the definition: f(tx + (1-t)y) <= t*f(x) + (1-t)*f(y) on 2000 random samples.

| Function | Convex? | Violations |
|----------|---------|-----------|
| f(x) = x^2 | CONVEX | 0 |
| f(x) = e^x | CONVEX | 0 |
| f(x, y) = x^2 + y^2 | CONVEX | 0 |
| f(x) = sin(x) | NOT CONVEX | many |
| f(x) = x^3 | NOT CONVEX | many |
| f(x, y) = x^2 - y^2 | NOT CONVEX | many |

[Source: 18-convex-optimization, convex.py]

### Example 12: Momentum Effect on SGD

Minimizing Rosenbrock with SGD, varying momentum beta, lr=0.0001, 5000 steps.

| Momentum (beta) | Final x | Final y | Loss |
|---|----------|----------|----------|
| 0.0 (no momentum) | 0.97213 | 0.94621 | 0.000841 |
| 0.5 | 0.98134 | 0.96304 | 0.000356 |
| 0.9 | 0.99213 | 0.98407 | 0.000062 |
| 0.99 (very high) | 0.99804 | 0.99609 | 0.000003 |

**Key insight:** Higher momentum accelerates descent but risks overshooting. Beta=0.9 is the standard trade-off.

[Source: 08-optimization, optimizers.py]

## Out of Scope / Hold for Later

- **Backpropagation through neural network layers:** Uses the chain rule systematically through a computation graph; covered in autodiff lessons.
- **Automatic differentiation (autodiff) library internals:** How PyTorch/JAX compute gradients automatically; covered in lesson 05.
- **Second-order methods beyond brief mention:** L-BFGS, K-FAC, natural gradient; impractical for neural networks but mentioned in convex-optimization context.
- **Constrained optimization (Lagrange multipliers, KKT conditions):** Relevant for SVMs and regularization theory; beyond linear regression scope.
- **Batch normalization, learning rate schedules (cosine annealing, warmup):** Covered in deeper training lessons.
- **Stochastic vs batch gradient descent noise analysis:** Beyond univariate and simple multivariate linear regression.
