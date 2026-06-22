# Overfitting and Cross-Validation

Your tree just hit 100% training accuracy. That is not good news.

A decision tree with no depth limit can always reach zero training error: it keeps splitting until
every leaf contains exactly one class. At that point the tree has memorized the training set,
including every measurement quirk and label noise that will never appear the same way in new data.
The question is the same one you met in M2: how large is the gap between train accuracy and test
accuracy? That gap is the variance, and `max_depth` is the knob that controls it.

## The Experiment

The dataset is breast cancer classification from scikit-learn: 569 samples, 30 features, two
classes. Split 75/25 with `random_state=42`. Train `ml.tree.DecisionTreeClassifier` at rising
`max_depth`, then read both train accuracy and test accuracy.

| max_depth | Train accuracy | Test accuracy |
|-----------|----------------|---------------|
| 1         | 0.923          | 0.895         |
| 2         | 0.946          | 0.916         |
| 3         | 0.972          | 0.951         |
| 4         | 0.995          | 0.944         |
| 7         | 1.000          | 0.944         |
| None      | 1.000          | 0.944         |

Train accuracy climbs monotonically, reaching a perfect 1.000 by depth 7. Test accuracy peaks at
depth 3 (0.951) and never improves again, even as the tree keeps growing. The fully grown tree
memorized noise; it has nothing new to say about samples it did not train on.

This is the same story told in M2, different algorithm. In M2 you saw polynomial degree drive
train MSE down and test MSE up. Here `max_depth` drives train accuracy up and test accuracy
sideways. In M1 you saw k-NN's `k` do the same: at `k=1` the boundary traces every training
point, high variance; at large `k` it smooths out, high bias. The parameter changes, the
tradeoff does not.

## Why the Tree Memorizes

A decision tree splits recursively on the (feature, threshold) pair that reduces impurity most.
With no stopping rule, it splits until every leaf is pure: one class, one sample. At that point
train accuracy is exactly 1.000 by construction. But those final splits are fitting noise: the
last few samples separated by a threshold that will not appear the same way in the test set.

The ingredient source (AEFS decision tree module) states this directly: "A tree grown to full
depth (one sample per leaf) perfectly memorizes training data but generalizes terribly." The
depth hyperparameter is pre-pruning: you stop growth early rather than growing and trimming
afterward.

From the table, depth 3 is the sweet spot on this dataset. Train accuracy (0.972) is still
well above depth 1 (0.923), meaning the tree has learned real structure. Test accuracy (0.951)
is the highest observed. Past depth 3, train accuracy keeps rising but test accuracy does not:
the added splits are pure memorization.

## Choosing max_depth: Cross-Validation

There is a catch. If you read the table above and say "depth 3 wins," you have tuned on the
test set. You used held-out test data to make a modeling decision. The test set is no longer
a clean measure of generalization: it has influenced the model choice.

Cross-validation solves this by keeping the test set sealed and selecting `max_depth` on a
rotation through the training data. The procedure, as Azure Machine Learning's Cross Validate
Model component describes it ([learn.microsoft.com/azure/machine-learning/component-reference/cross-validate-model](https://learn.microsoft.com/azure/machine-learning/component-reference/cross-validate-model?view=azureml-api-2)):

1. Divide the training data into k equal folds.
2. For each fold: train on the remaining k-1 folds, evaluate on the held-out fold.
3. Average the k evaluation scores.

Five-fold cross-validation on this dataset trains five trees per candidate depth, each on 80%
of the training data, validated on the remaining 20%. The averaged validation score for each
depth tells you which `max_depth` generalizes best, using only the training portion. The test
set stays sealed until after the depth is chosen.

Azure ML's automated ML documentation makes the principle explicit: "Cross-validation takes
many subsets of your full training data and trains a model on each subset. The idea is that a
model might get lucky and have great accuracy with one subset, but by using many subsets, the
model can't achieve high accuracy every time" ([learn.microsoft.com/azure/machine-learning/concept-manage-ml-pitfalls](https://learn.microsoft.com/azure/machine-learning/concept-manage-ml-pitfalls?view=azureml-api-2#review-automated-ml-features-to-prevent-overfitting)). That rotation is what makes the choice reliable.

The test set is evaluated exactly once, after every modeling decision is final.

## The Diagnostic in Practice

Three readings from the train/test table:

- **Both accuracies low, small gap:** high bias. The tree is too shallow; it cannot represent
  the pattern. Increase `max_depth`.
- **Train accuracy high, test accuracy lower, large gap:** high variance. The tree is memorizing
  noise. Decrease `max_depth`, or use cross-validation to find the depth where the gap closes.
- **Both accuracies high, small gap:** good fit. Stop here.

The table says depth 3 is the last point where the gap is closing, not widening. Past depth 3
the gap grows: train accuracy rises, test accuracy sits still. That is the overfitting signature,
and it is a number, not an opinion.

## Core Concepts

- A decision tree with no depth limit always reaches 1.000 train accuracy by splitting until
  every leaf is pure; the gap between train accuracy and test accuracy is the direct measurement
  of overfitting.
- `max_depth` is the bias-variance knob for trees: the same tradeoff you measured with
  polynomial degree in M2 and with k in M1, different parameter name.
- Test accuracy peaked at depth 3 (0.951) on this dataset and never improved at depth 4 or
  higher, even as train accuracy climbed to 1.000: the fully grown tree memorized noise.
- Cross-validation selects `max_depth` by rotating through training folds, so the test set
  stays sealed until after the choice is final; tuning on the test set discards the only
  clean measure of generalization you have.

<div class="claude-handoff" data-exercise="exercises/module3/overfitting-and-cross-validation/">

**Build It in Claude Code**: Write the depth-sweep and cross-validation experiment in
`exercises/module3/overfitting-and-cross-validation/`. Use `ml.tree.DecisionTreeClassifier`
on breast cancer data (75/25 split, `random_state=42`) at rising `max_depth` to demonstrate
that train accuracy climbs to 1.000 while held-out test accuracy peaks at a moderate depth and
does not keep improving. The gate at
`exercises/module3/overfitting-and-cross-validation/test_overfitting.py` must pass green with
`python -m pytest exercises/module3/overfitting-and-cross-validation`.

</div>
