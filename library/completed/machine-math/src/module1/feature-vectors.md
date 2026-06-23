# Feature Vectors and the Space They Live In

Every row in your dataset is a point in space. That reframing converts a table of numbers into a
geometry problem, and it is the foundation every distance-based ML algorithm stands on.

## The Row Is a Point

Measure an iris flower: sepal length 5.1, sepal width 3.5, petal length 1.4, petal width 0.2. That
observation is one point in four-dimensional space, written as a row vector:

```
x = [5.1, 3.5, 1.4, 0.2]
```

Stack 150 such rows into a matrix `X` of shape (150, 4). Each column is a feature axis; each row is
one point in four-dimensional feature space. Every classic ML algorithm accepts a matrix in exactly
this shape.

The dimensionality is the number of features. Four-dimensional data is the same geometric object
as two-dimensional data; you have lost the picture, not the geometry.

A vector has two properties that matter in ML: magnitude and direction. The magnitude (L2 norm) is:

```
||x|| = sqrt(x1² + x2² + ... + xn²)
```

For the iris row: `sqrt(5.1² + 3.5² + 1.4² + 0.2²) = sqrt(40.26) ≈ 6.35`. Dividing by the
magnitude gives a unit vector: same direction, magnitude 1. That normalization step is what makes
cosine similarity meaningful.

## The Dot Product as a Similarity Probe

The dot product of two vectors `a` and `b` is:

```
a · b = a1*b1 + a2*b2 + ... + an*bn
```

Its geometric meaning: `a · b = ||a|| * ||b|| * cos(θ)`, where `θ` is the angle between them. Same
direction: `cos(θ) = 1`. Orthogonal: `cos(θ) = 0`. Opposite: `cos(θ) = -1`.

In NumPy, the dot product is one call:

```python
import numpy as np

a = np.array([1.0, 2.0, 3.0])
b = np.array([4.0, 5.0, 6.0])
print(np.dot(a, b))   # 32.0  (1*4 + 2*5 + 3*6)
```

The dot product is the engine behind cosine similarity, attention scores in transformers, and linear
regression scoring. Azure AI Search documents it as one of three vector similarity metrics, alongside
cosine and Euclidean, and notes that for normalized vectors dot product is identical to cosine
similarity but slightly more performant
(learn.microsoft.com/azure/search/vector-search-ranking#similarity-metrics-used-to-measure-nearness).

## Three Distance Metrics, Three Different Questions

"How far apart are these two points?" has three common answers in ML. Each encodes a different
assumption about what "far" means.

### Euclidean Distance (L2)

Straight-line distance, Pythagoras in n dimensions:

```
euclidean(a, b) = sqrt((a1-b1)² + (a2-b2)² + ... + (an-bn)²)
```

Use it when absolute magnitude matters: a point far away in raw coordinate space is genuinely
dissimilar. It is the natural metric for tabular data where features are on comparable scales after
normalization. Azure Cosmos DB's distance function reference describes Euclidean as "the straight-line
distance between two points" and recommends it for spatial data where magnitude matters
(learn.microsoft.com/azure/cosmos-db/gen-ai/distance-functions).

### Cosine Distance

Cosine similarity measures the angle between two vectors, ignoring their lengths:

```
cos_sim(a, b)      = (a · b) / (||a|| * ||b||)
cosine_distance(a, b) = 1 - cos_sim(a, b)
```

Result ranges from 0 (identical direction) to 2 (opposite direction). Use cosine distance when
magnitude is noise. A short document and a long document about the same topic point in the same
direction in term-frequency space; their Euclidean distance is large, their cosine distance is near
zero. Azure AI Foundry's embeddings documentation puts it precisely: "two documents might be far
apart by Euclidean distance because of size, they could still have a smaller angle between them and
therefore higher cosine similarity"
(learn.microsoft.com/azure/ai-foundry/openai/concepts/understand-embeddings). Azure OpenAI embedding
models use cosine as their default metric, and Azure AI Search recommends specifying `cosine` in the
vector configuration when indexing Azure OpenAI embeddings
(learn.microsoft.com/azure/search/vector-search-ranking#similarity-metrics-used-to-measure-nearness).

### Manhattan Distance (L1)

Sum the absolute differences along each axis:

```
manhattan(a, b) = |a1-b1| + |a2-b2| + ... + |an-bn|
```

The name is the grid-city analogy: you walk north-south and east-west, never diagonally. Azure Cosmos
DB's distance function reference describes it as "the distance between two points by adding up the
absolute differences between their coordinates"
(learn.microsoft.com/azure/cosmos-db/gen-ai/distance-functions). Because large per-axis differences
are not squared, Manhattan distance is more robust to outliers than Euclidean; in high-dimensional
sparse data it often outperforms L2.

### The Three Metrics on One Example

```
A = [1, 2, 3]
B = [4, 0, 6]

euclidean       = sqrt((4-1)² + (0-2)² + (6-3)²) = sqrt(9 + 4 + 9) = sqrt(22) ≈ 4.69
manhattan       = |4-1| + |0-2| + |6-3|           = 3 + 2 + 3       = 8
cosine_distance = 1 - (a·b)/(||a||·||b||)
                = 1 - (1*4 + 2*0 + 3*6) / (sqrt(14) * sqrt(52))
                = 1 - 22 / (3.742 * 7.211)
                ≈ 1 - 0.815                        ≈ 0.18
```

Manhattan (8) exceeds Euclidean (4.69) here because summing raw per-axis gaps can never
undercut the straight-line distance: the diagonal path is always the shortest one. Cosine (0.18)
reads these same two points as fairly similar in direction even though they sit nearly 5 units
apart in space, because A and B point in roughly the same angular neighborhood. Each metric weighs
the axes differently; the right choice depends on the geometry of your data, not convention.

## Why Scaling Changes Everything

Consider age (range 20–80) and annual income (range 20,000–200,000). Raw Euclidean distance treats
one unit of age and one unit of income as equally important. One dollar of income is irrelevant; twenty
years of age is enormous. The metric measures income and nearly ignores age.

The fix is scaling before any distance computation. Two standard forms:

**Min-max scaling** rescales each feature to [0, 1]:

```
x_scaled = (x - x_min) / (x_max - x_min)
```

**Z-score standardization** centers each feature to mean 0, standard deviation 1:

```
x_scaled = (x - mean) / std
```

Azure Machine Learning's Normalize Data component documents both exactly: "ZScore: Converts all
values to a z-score" and "MinMax: The min-max normalizer linearly rescales every feature to the
[0,1] interval"
(learn.microsoft.com/azure/machine-learning/component-reference/normalize-data). The two methods have
different shapes: min-max bounds the output to a fixed range and preserves the distribution; z-score
centers the data and is unbounded, which makes it more stable for algorithms sensitive to extreme
values.

The function signatures you will implement match these definitions exactly:

```python
minmax_scale(X)   # rescale each column to [0, 1]
zscore(X)         # center each column to mean 0, std 1
```

After scaling, every feature axis contributes equally to the distance calculation. That is not a
preprocessing nicety; it is the precondition for any distance-based algorithm to work correctly.
k-NN is the most exposed: the entire prediction is a distance vote, and unscaled features hand that
vote entirely to whichever column has the largest raw range.

## What the Geometry Buys You

The matrix `X` of shape (n_samples, n_features) encodes a neighborhood structure. Points close in
feature space share similar feature combinations; points far apart do not. Setting up that geometry
correctly, choosing the right metric and applying the right scale, is the work that happens before any
model sees the data.

The same math runs at production scale. Azure AI Search resolves a vector query by computing cosine
similarity between an incoming embedding and every indexed document vector; Azure Cosmos DB stores
that index alongside your data and returns the nearest neighbors by whichever distance function you
configure. The retrieval system and the k-NN classifier are solving identical problems at different
scales. Getting the metric wrong costs the same either way.

## Core Concepts

- A dataset row is a vector; the full dataset is a matrix of shape (n_samples, n_features); every
  classic ML algorithm reads this shape and reasons about its geometry.
- The dot product `a · b = ||a|| * ||b|| * cos(θ)` measures directional alignment; cosine
  similarity normalizes it by magnitude so that vector length does not affect the score.
- Euclidean distance measures straight-line separation (use when magnitude matters); cosine distance
  measures angle (use when magnitude is noise); Manhattan distance sums absolute per-axis differences
  (use for robustness or sparse high-dimensional data).
- Feature scaling (min-max or z-score) is required before any distance-based algorithm: without it,
  the highest-range column casts all the votes.

<div class="claude-handoff" data-exercise="exercises/module1/feature-vectors/">

**Build It in Claude Code**: Load the Iris dataset with scikit-learn, then build five functions from scratch in NumPy inside `ml/distances.py`: `euclidean(a, b)` (straight-line L2 distance, returns float), `manhattan(a, b)` (sum of absolute per-axis differences), `cosine_distance(a, b)` (1 minus cosine similarity; raises `ValueError` on a zero vector), `minmax_scale(X)` (rescale each column to [0, 1]), and `zscore(X)` (center each column to mean 0, std 1). Compute pairwise Euclidean and cosine distance between the first five rows and print both matrices. Write one sentence per metric explaining why they disagree on at least one pair.

</div>
