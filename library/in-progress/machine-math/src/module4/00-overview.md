# Module 4: Ensembles and the Gradient

Module 3 gave you one tree. One tree is a weak, high-variance learner: fit it deeply and
it memorizes the training set; constrain it with `max_depth` and it misses real signal.
Module 4 asks what happens when you run many trees together, and finds two completely
opposite answers.

## Two Strategies, One Building Block

The M3 `DecisionTreeClassifier` is the building block both strategies share. What changes
is how the trees relate to each other.

**Bagging** runs trees independently. You draw a bootstrap sample (sampling rows with
replacement), train a full tree on it, and repeat. Because each tree sees a slightly
different dataset, the trees make different mistakes. Average their predictions and the
random errors cancel, cutting variance without meaningfully raising bias. Random forests
add one more twist: at each split, each tree considers only a random subset of features,
forcing even more diversity. The result is an ensemble that is systematically more
accurate than any single tree it contains.

**Boosting** runs trees sequentially, and each tree's job is to fix the last tree's
mistakes. Start with a constant prediction (the mean for regression). Compute the
difference between the truth and what the ensemble predicts so far: those are the
residuals. Fit a new, shallow tree to the residuals. Add a shrunken version of that
tree to the ensemble. Repeat. For squared-error loss, the residuals are the negative
gradient of the loss with respect to the current prediction, so each stage is a step
of gradient descent: not in the space of model weights, but in the space of functions.

The two strategies are not just implementation choices. They fix different problems.
Bagging cuts variance while keeping bias roughly flat. Boosting cuts bias by iteratively
correcting systematic errors, at the risk of overfitting if you run too many rounds.

## Three Lessons

The module runs in order. Each lesson builds on the one before it.

**Bagging and Random Forests** shows how averaging many independent high-variance trees
cuts their collective variance. You build `RandomForestClassifier` in `exercises/ml/ensemble.py`,
directly reusing the `DecisionTreeClassifier` from `ml/tree.py`. Measured on breast
cancer classification, the 100-tree forest outperforms any single tree.

**Boosting and the Gradient** shows how sequential residual fitting becomes gradient
descent in function space. You first add `DecisionTreeRegressor` to `exercises/ml/tree.py`,
then build `GradientBoostingRegressor` in `exercises/ml/ensemble.py`. The Friedman-1
regression dataset serves as the acceptance gate.

**Hyperparameters and the Tradeoff** closes the module by naming the levers on both
ensembles: `n_estimators`, `learning_rate`, `max_depth`, `max_features`. You measure the
bias-variance tradeoff directly: what happens to test error as you vary each knob while
holding the others fixed?

## What Is Given

Scikit-learn provides datasets (`load_breast_cancer`, `make_friedman1`) and serves as the
oracle in both acceptance gates: your from-scratch ensembles must agree with scikit-learn's
equivalents on held-out data. All algorithm logic is NumPy plus the `ml.tree` classes you
have already built.

## What Is Deliberately Out of Scope

**Evaluation metrics** (precision, recall, F1, ROC-AUC) are held for Module 5. The
acceptance gates in this module use raw accuracy or R-squared as sanity checks only.

**Feature engineering** is held for Module 6. Both ensembles here receive clean, numeric
features from scikit-learn datasets.

**XGBoost and LightGBM** are the production successors to the from-scratch gradient
booster you build here. They add second-order gradient approximations, column
subsampling, and cache-aware block structures. The Azure Machine Learning designer's
Boosted Decision Tree Regression and Two-Class Boosted Decision Tree components are
backed by LightGBM and expose the same three levers: number of trees, learning rate, and
tree depth. Module 4's from-scratch version teaches the same mechanics those components
implement.
