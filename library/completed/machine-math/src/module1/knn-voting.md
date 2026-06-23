# k-Nearest Neighbors: Voting in Feature Space

Distance is a decision. Before any vote is cast, you choose a metric, and that choice encodes a hypothesis about what "similar" means in your data. Get the metric wrong and the votes are meaningless, no matter how many neighbors you consult.

## The Algorithm, Exactly

k-NN does three things at prediction time: measure, rank, vote. There is no model to fit, no loss to minimize, no parameters to learn. "Training" is storing the labeled dataset.

Given a query point `x`:

1. Compute the distance from `x` to every point in the training set.
2. Sort those distances ascending.
3. Take the `k` closest points.
4. Return the majority label among those `k` neighbors (classification) or their mean target value (regression).

The algorithm is called a **lazy learner** because it defers all computation to prediction time. Training is O(1); each prediction costs O(n * d) distance computations, where `n` is the number of training points and `d` is the number of features. That cost is fine at small scale and brutal at large scale, which is exactly why approximate nearest-neighbor methods exist.

Azure Machine Learning's AutoML SDK formalizes this: `ClassificationModels.KNN` and `RegressionModels.KNN` are both defined as an algorithm that "uses feature similarity to predict the values of new datapoints, meaning the new data point will be assigned a value based on how closely it matches the points in the training set" ([learn.microsoft.com](https://learn.microsoft.com/dotnet/api/microsoft.azure.powershell.cmdlets.machinelearningservices.support.classificationmodels.knn?view=az-ps-latest)).

## The Implementation

The `ml/knn.py` below imports the distance functions you built in the previous lesson. Every line maps to one of the three steps: measure, rank, vote. Reading it is the point.

```python
"""k-nearest neighbors, from scratch in NumPy.

A lazy learner: "training" is storing the data; all the work is at prediction time. Every line maps
to one of three steps -- measure distance to every training point, rank, vote. The metric is pluggable
because choosing it is a modeling decision, not a default.
"""
import numpy as np
from collections import Counter

from ml.distances import METRICS


class KNNClassifier:
    def __init__(self, k=5, metric="euclidean"):
        if metric not in METRICS:
            raise ValueError(f"Unknown metric: {metric!r}; choose one of {sorted(METRICS)}")
        self.k = k
        self.metric = metric

    def fit(self, X, y):
        """Store the labeled training set. No parameters are fit; this is the whole 'training' phase."""
        self.X_train = np.asarray(X, dtype=float)
        self.y_train = np.asarray(y)
        return self

    def predict(self, X):
        X = np.asarray(X, dtype=float)
        return np.array([self._predict_one(x) for x in X])

    def _predict_one(self, x):
        distance = METRICS[self.metric]
        distances = [distance(x, row) for row in self.X_train]
        k_idx = np.argsort(distances)[: self.k]
        votes = Counter(self.y_train[i] for i in k_idx)
        return votes.most_common(1)[0][0]
```

Note: the module docstring uses `--` (two hyphens) as a list separator inside the string literal. That is a code artifact, not prose; the style rule against em-dashes applies only to prose you read, not to characters inside string literals.

The `METRICS` dispatch table lives in `ml/distances.py`, the file you built last lesson. The classifier borrows it with one import. No distance logic is duplicated; extending the metric list means editing one file.

## k Is the Bias-Variance Knob

`k` controls the smoothness of the decision boundary with no indirection between the parameter and its geometric effect.

At `k=1`, every query point's prediction is determined by its single nearest neighbor. The decision boundary traces every kink and outlier in the training data: zero training error, high variance, severe overfitting. One mislabeled point in the training set can corrupt an entire neighborhood.

At `k=N` (all training points), every query gets the global majority class. The boundary is a flat line: zero variance, maximum bias, complete underfitting.

On Iris (150 samples, 80/20 stratified split, z-scored features, Euclidean distance), you see this tradeoff directly:

| k | Accuracy |
|---|----------|
| 1 | 0.967 |
| 3 | 0.967 |
| 5 | 1.000 |
| 11 | 1.000 |
| 21 | 0.900 |

The drop at `k=21` is the high-bias end arriving: the neighborhood has grown large enough to smooth away class boundaries that Iris actually has. This is a held-out set of 30 samples, so treat these numbers as directional, not definitive. The shape of the curve, not any single value, is the lesson.

The conventional starting range is odd values near the square root of the training set size: odd to avoid ties in binary classification, near `sqrt(n)` to keep neighborhoods local without chasing every outlier.

## The Metric Is a Hypothesis

The distance function defines what "near" means. Different metrics encode different assumptions about the geometry of your data.

**Euclidean** (L2) is the right default when all features are on comparable scales and a large absolute difference on any dimension genuinely means far apart. It squares differences, so a single large gap dominates. After z-scoring, Euclidean is usually the correct first choice for tabular data.

**Manhattan** (L1) sums absolute differences without squaring. It is more robust when features have heavy tails or when one outlier dimension would otherwise blow up the distance.

**Cosine** measures the angle between two vectors, ignoring magnitude. It is the correct choice when scale varies across observations but the proportional mix of features is what matters: a document with 30 mentions of "neural" and one with 3 mentions should be considered similar if the rest of their vocabulary profile matches. Text embeddings and high-dimensional sparse data both reward cosine.

On the same Iris held-out set at `k=5`:

| Metric | Accuracy |
|--------|----------|
| euclidean | 1.000 |
| manhattan | 1.000 |
| cosine | 0.933 |

Cosine's lower accuracy here reflects that Iris features are spatial measurements (petal length, petal width), not frequency profiles: direction alone misses information that absolute magnitude carries. The metric that matches the data geometry wins.

## Scaling Is Not Optional

Distance functions are sensitive to the units of each feature. A raw feature measured in thousands (salary) will dominate a feature measured in tens (age), regardless of their actual predictive power. The classifier ends up voting on whichever feature has the largest numerical range, not the most signal.

With the weakest Iris feature (sepal width) artificially inflated by a factor of 1000, unscaled accuracy on the same split is 0.800. Z-scoring restores it to 1.000. One column hijacked the distance calculation; z-scoring returned a fair vote.

The fix is always the same:

```python
from ml.distances import zscore

X_train_scaled = zscore(X_train)
X_test_scaled  = zscore(X_test)
```

Here you z-score each set to its own column statistics, which is enough for this module. Production
pipelines fit the scaler on training data only and apply that fixed transform to the test set so
the test statistics never leak into training, a discipline the feature-engineering module builds
out. The point either way: scale before you measure distance.

## The Curse of Dimensionality

k-NN degrades predictably as feature count grows. In high-dimensional spaces, the ratio of the maximum pairwise distance to the minimum pairwise distance converges toward 1.0. Every point becomes approximately equidistant from every other point. The concept of "nearest neighbor" loses its meaning: if the 1st nearest neighbor and the 1000th nearest neighbor are effectively the same distance away, the ranking carries no signal.

The practical ceiling is roughly 20 to 50 features. Beyond that, k-NN on raw feature vectors stops working reliably. The fix is dimensionality reduction before the distance calculation, not during it. This is why embeddings exist: a model trained on millions of examples compresses hundreds of raw dimensions into a dense vector where the distances are semantically meaningful. You run k-NN on the embedding, not on the raw features.

That is also the bridge to production vector search. Azure Cosmos DB's comparison of kNN and ANN states it directly: "kNN is precise but computationally intensive, making it less suitable for large datasets. ANN offers a balance between accuracy and efficiency, making it better suited for large-scale applications" ([learn.microsoft.com](https://learn.microsoft.com/azure/cosmos-db/gen-ai/knn-vs-ann)). At scale, exact k-NN becomes approximate nearest-neighbor search (HNSW, DiskANN, IVF). Azure AI Search supports both exhaustive KNN for small corpora and HNSW for production workloads ([learn.microsoft.com](https://learn.microsoft.com/azure/search/vector-search-ranking#algorithms-used-in-vector-search)). The geometry is identical to the loop in the classifier above; the only thing that changes is the data structure that makes the search fast enough to serve at query time.

When you build a RAG pipeline, the "retrieve relevant chunks" step is k-NN over embeddings. You are running the same algorithm. The production system has replaced the brute-force loop with a graph index, but the question it answers is unchanged: which stored vectors are nearest to this query vector?

## Core Concepts

- k-NN is a lazy learner: training is storing the data; each prediction is O(n * d) distance computations, a neighbor ranking, and a majority vote.
- `k` is a direct bias-variance lever: small k traces every training-set kink (high variance); large k smooths the boundary to the global majority (high bias); the right k is found by cross-validation on held-out data.
- The distance metric encodes a hypothesis about the data's geometry: Euclidean for scaled absolute differences, cosine for directional profiles, Manhattan when single large differences should not dominate.
- The curse of dimensionality collapses k-NN's signal in high-dimensional raw feature spaces; embedding models are the fix, compressing dimensions into vectors where distances remain meaningful.

<div class="claude-handoff" data-exercise="exercises/module1/knn-voting/">

**Build It in Claude Code**: Implement `ml/knn.py` from scratch, reusing the `METRICS` dispatch table you built in `ml/distances.py`. Fit a `KNNClassifier` on 80% of z-scored Iris (stratified split, `random_state=0`), then evaluate held-out accuracy for k in {1, 3, 5, 11, 21} with Euclidean distance; compare Euclidean vs cosine at k=5 on the same split. Report which combination wins, explain why in terms of what the metric assumes about the data, and note where the k=21 accuracy drop shows up and what it tells you about the bias side of the tradeoff.

</div>
