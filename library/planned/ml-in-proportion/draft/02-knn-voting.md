# k-Nearest Neighbors: Voting in Feature Space

k-nearest neighbors is the most honest algorithm in classical ML. It makes no assumption about the
shape of the decision boundary. It builds no internal model. When asked to classify a new point, it
does exactly one thing: measure its distance to every training point, find the k closest, and take
a majority vote. That transparency is what makes it the right first algorithm to study: every
parameter you tune is a geometric decision you can visualize and reason about.

## The Algorithm, Exactly

Given:

- A training set of labeled points `(x_i, y_i)`, each `x_i` a vector in n-dimensional feature space.
- A new query point `x_q` without a label.
- A chosen k and a distance metric.

k-NN predicts the label of `x_q` by:

1. Computing the distance from `x_q` to every `x_i` in the training set.
2. Sorting those distances, ascending.
3. Taking the k points with the smallest distances (the "k nearest neighbors").
4. For classification: returning the most common label among those k points (majority vote). For regression: returning the average of their target values.

No parameters are fit during "training." The training phase is storing the data. All computation
happens at prediction time, which is why k-NN is called a lazy learner.

[MS-Learn: Azure Machine Learning's AutoML SDK documents k-NN under both `ClassificationModels.Knn`
and `RegressionModels.Knn`, defining it as an algorithm that "uses feature similarity to predict
the values of new datapoints, meaning the new data point will be assigned a value based on how
closely it matches the points in the training set." Source: classificationmodels.knn,
regressionmodels.knn.]

## Implementing k-NN From Scratch

The NumPy implementation is short enough to read in a sitting, and reading it is the point: every
line maps directly to one of the three steps above.

```python
import numpy as np
from collections import Counter

class KNNClassifier:
    def __init__(self, k=3, metric="euclidean"):
        self.k = k
        self.metric = metric

    def fit(self, X, y):
        # "Training" is storage only.
        self.X_train = X
        self.y_train = y

    def _distance(self, a, b):
        if self.metric == "euclidean":
            return np.sqrt(np.sum((a - b) ** 2))
        elif self.metric == "cosine":
            return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        elif self.metric == "manhattan":
            return np.sum(np.abs(a - b))
        raise ValueError(f"Unknown metric: {self.metric}")

    def predict(self, X):
        return np.array([self._predict_one(x) for x in X])

    def _predict_one(self, x):
        distances = [self._distance(x, x_tr) for x_tr in self.X_train]
        k_indices = np.argsort(distances)[: self.k]
        k_labels = [self.y_train[i] for i in k_indices]
        return Counter(k_labels).most_common(1)[0][0]
```

This is the complete algorithm. The only complexity is the distance function. Everything else is
sorting and voting.

## k Is a Smoothness Knob

k controls the bias-variance tradeoff directly, with no abstraction layer between the parameter and
its geometric effect.

With `k=1`, every training point is its own neighborhood: the decision boundary is jagged, following
the exact layout of the training data. High variance, low bias. A single mislabeled point can flip
a neighborhood.

With `k=N` (all training points), every query point gets the same prediction: the global majority
class. Zero variance, high bias. The model has stopped caring about geometry.

Somewhere in between is the value of k that minimizes held-out error for your dataset. The
conventional starting range is odd values between 3 and the square root of the training set size
(to avoid ties and to keep neighborhoods local). You find the right k by cross-validation, which
Module 3 covers in detail; for now, note that the cross-validation curve for k-NN is one of the
clearest illustrations of the bias-variance tradeoff you will ever see.

## Distance Metric Choice Is a Modeling Decision

The metric you hand to the distance function is a hypothesis about the structure of your data. It
is not a neutral default.

**Euclidean** is correct when the feature space is roughly isotropic: all features are on comparable
scales and a large absolute difference on any dimension genuinely means "far apart." After z-score
normalization on tabular data, Euclidean is usually the right first choice.

**Cosine** is correct when the scale of each observation varies but the proportional pattern is
what matters. A customer with 3 electronics purchases and a customer with 30 electronics purchases
should be considered similar if the mix of sub-categories is the same. Cosine similarity factors
out magnitude and compares direction.

**Manhattan** is correct when the feature space is sparse or has outlier-heavy dimensions: the L1
norm does not square large differences, so a single extreme feature does not blow up the distance
calculation.

[MS-Learn: Azure Cosmos DB kNN-vs-ANN documentation describes exact k-NN computation as "precise
but computationally intensive, making it less suitable for large datasets," and notes that vectorization
and distance calculation are the two core steps: "calculate the distance between the query point and
all other points in the dataset using a distance function." Source: knn-vs-ann, how-knn-works.]

## The Curse of Dimensionality

k-NN degrades predictably as the number of features grows. In high-dimensional spaces, all points
become approximately equidistant from any query point. The concept of "nearest neighbor" loses
meaning: if the distances from any point to its k nearest neighbors and its k farthest neighbors
converge, there is no signal left in the ranking.

The practical implication: k-NN on raw text features (tens of thousands of dimensions) does not
work well. k-NN on an embedding vector (a few hundred to a few thousand dimensions, designed by a
model to concentrate semantic signal) can work well, because the embedding model has already done
the dimensionality reduction for you.

Feature selection and dimensionality reduction are the tools that fight the curse. This is why PCA
and SVD sit in the same curriculum arc as k-NN, in Module 6: they are partial cures for the same
disease.

## Where k-NN Fits in the Algorithm Zoo

[MS-Learn: Azure Machine Learning's algorithm selection guide lists k-NN for both classification
and regression in AutoML, alongside decision trees, SVM, linear models, and ensemble methods.
Source: how-to-configure-auto-train, configure-your-experiment-settings.]

k-NN is:

- **Interpretable**: you can show a user exactly which training examples determined a prediction.
- **Non-parametric**: no assumption about the data distribution; the decision boundary is data-driven.
- **Lazy**: all computation is at inference time, which makes training instantaneous and prediction slow on large datasets.
- **A debugging benchmark**: if your parametric model cannot beat k-NN on your data, you have a modeling problem, not a data problem.

In production, exact k-NN at scale is replaced by approximate nearest neighbor (ANN) algorithms:
HNSW, DiskANN, ball trees. These are the data structures behind Azure AI Search vector indexes and
Azure Cosmos DB vector search. The math they approximate is identical to the loop in the code block
above; they trade exact answers for logarithmic lookup time.

## Core Concepts

- k-NN is a lazy learner: training is storage; prediction is distance calculation, neighbor ranking, and majority vote.
- k is a bias-variance lever: small k gives a jagged decision boundary (high variance); large k gives a smooth one (high bias); cross-validation finds the right value.
- The distance metric is a hypothesis about the structure of your data: Euclidean for normalized absolute differences, cosine for proportional patterns, Manhattan for sparse or outlier-heavy features.
- The curse of dimensionality causes k-NN to degrade as feature count grows; embedding-based representations are the production-scale fix.
- Production vector search (Azure AI Search, Cosmos DB vector indexes) is approximate nearest-neighbor search: the same geometry as k-NN, optimized for scale.

<div class="claude-handoff" data-exercise="draft/exercises/02-knn-voting/">

**Build It in Claude Code**: Implement the KNNClassifier class above from scratch in NumPy, fit it on 80% of the Iris dataset, evaluate accuracy on the held-out 20% for k in {1, 3, 5, 11, 21}, and plot accuracy vs k; then rerun with Euclidean vs cosine metric and report which combination wins.

</div>
