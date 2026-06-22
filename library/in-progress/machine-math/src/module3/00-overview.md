# Module 3: Splitting and Branching

Module 1 asked: how far apart are these points? Module 2 asked: what line fits through
them? This module asks a third and different question: which single yes/no question best
separates the labels?

That question is the seed of every decision tree. To answer it you need a way to measure
how mixed the labels in a node are before and after a split. That measurement comes from
information theory: Shannon entropy and Gini impurity both quantify disorder, and the
drop in disorder that a split buys is called information gain. The tree algorithm is just
that idea applied recursively until some stopping condition says enough.

## Three Lessons, One Thread

The module runs in order. Each lesson depends on the one before it.

**Entropy and Information Gain** is the foundation. Entropy measures how many bits you
need to describe the labels in a node; a pure node needs zero, a perfectly balanced
two-class node needs exactly one bit. Gini impurity measures the same thing with simpler
arithmetic: the probability of misclassifying a randomly drawn sample. Information gain
is the impurity at the parent minus the size-weighted average impurity at the two
children. The lesson builds `entropy`, `gini`, and `information_gain` in
`exercises/ml/tree.py` and verifies them against closed-form values.

**Decision Trees: Recursive Partitioning** puts the impurity functions to work. At every
node the algorithm tries every (feature, threshold) pair, computes the information gain
for each, picks the best, splits the data, and recurses on both children. Prediction is a
walk from root to leaf: at each internal node you take the branch whose condition your
sample satisfies; at the leaf you return the majority class. The lesson builds the full
`DecisionTreeClassifier` in `exercises/ml/tree.py` and verifies it against scikit-learn
on Iris.

**Overfitting and Cross-Validation** names the cost. A tree grown with no stopping
condition memorizes the training data: every leaf holds one sample, training accuracy is
perfect, and test accuracy collapses. Cross-validation finds the depth where the gap
between training and validation error starts to widen. That depth is your
`max_depth` hyperparameter.

## The Thread

Entropy and Gini are the rulers. The tree algorithm is the ruler applied greedily, split
by split. Cross-validation is what keeps you from applying the ruler until the ruler
breaks.

## What Is Given

Scikit-learn loads the Iris dataset and serves as the oracle in the acceptance test: your
from-scratch tree must agree with it on the same data, at the same depth, using the same
criterion. All algorithm logic is NumPy. The `exercises/ml/tree.py` file is the
throughline artifact; both lessons in this module add to it in sequence.

## What Is Deliberately Out of Scope

**Ensembles and random forests** are held for Module 4. A random forest runs many trees
on bootstrap samples of the data and takes a majority vote; each individual tree is built
exactly as you will build it here. The Azure Machine Learning designer surface exposes
this directly: the [Two-Class Decision Forest](https://learn.microsoft.com/azure/machine-learning/component-reference/two-class-decision-forest?view=azureml-api-2)
and [Multiclass Decision Forest](https://learn.microsoft.com/azure/machine-learning/component-reference/multiclass-decision-forest?view=azureml-api-2)
components wrap the same greedy tree algorithm you build in this module, then layer
bagging on top. Module 4 covers that layering.

**Evaluation metrics** (precision, recall, F1, ROC-AUC) are held for Module 5. This
module uses raw accuracy as a sanity check only; the full evaluation vocabulary belongs
after you can build the thing being evaluated.
