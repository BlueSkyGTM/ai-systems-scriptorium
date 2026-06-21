# Feature Vectors and the Space They Live In

A dataset row is a vector. That single reframing converts every classical ML algorithm from a
procedure you follow into a geometry problem you can reason about. Before you write a single model,
you need to be fluent in the coordinate language: what a vector is, how a matrix packages a whole
dataset, what the dot product measures, and which distance metric fits which shape of data.

## The Row Is a Point

Tabulate four measurements of an iris flower: sepal length 5.1, sepal width 3.5, petal length 1.4,
petal width 0.2. That observation is a point in four-dimensional space, written as a row vector:

```
x = [5.1, 3.5, 1.4, 0.2]
```

Stack 150 such rows into a matrix `X` of shape (150, 4). That matrix is your dataset. Each column
is a feature dimension; each row is one point in a four-dimensional feature space. Every classic-ML
algorithm accepts a matrix in exactly this shape and reasons about its geometry.

The dimensionality is just the number of features. Two-dimensional data is easy to visualize: plot
a scatter. Four-dimensional data is the same object; you have lost the picture but not the geometry.

## Vectors: Length and Direction

A vector has two properties that matter in ML: magnitude (length) and direction.

The **magnitude** (L2 norm) of a vector `x` is:

```
||x|| = sqrt(x1^2 + x2^2 + ... + xn^2)
```

For the iris row above: `sqrt(5.1^2 + 3.5^2 + 1.4^2 + 0.2^2) = sqrt(26.01 + 12.25 + 1.96 + 0.04) = sqrt(40.26) ≈ 6.35`.

**Direction** is what remains after you divide by the magnitude. A unit vector points in the same
direction but has magnitude 1. Normalizing a vector to unit length is the operation that makes
cosine similarity meaningful, because it factors out scale and compares only angle.

## The Dot Product as a Similarity Probe

The dot product of two vectors `a` and `b` of the same dimension is the scalar:

```
a · b = a1*b1 + a2*b2 + ... + an*bn
```

This arithmetic has a geometric interpretation: `a · b = ||a|| * ||b|| * cos(θ)`, where `θ` is the
angle between the vectors. Two vectors that point in the same direction have `cos(θ) = 1` (maximum
similarity). Two orthogonal vectors have `cos(θ) = 0` (no shared direction). Two vectors pointing
opposite ways have `cos(θ) = -1`.

The dot product is everywhere in ML. Linear regression scores a new point by taking the dot product
of its feature vector with the learned weight vector. The attention mechanism in transformers scores
query-key pairs with a scaled dot product. In this module, the dot product is the engine behind
cosine similarity: the most common way to measure how alike two points are when magnitude should not
affect the answer.

[MS-Learn: Azure AI Search documents three vector similarity metrics; cosine similarity "measures
the angle between two vectors and isn't affected by differing vector lengths" and is the metric used
by Azure OpenAI embedding models. Source: vector-search-ranking, similarity-metrics-used-to-measure-nearness.]

## Three Distance Metrics, Three Different Questions

"How far apart are these two points?" has three common answers. The one you choose defines what
"far" means for your algorithm.

### Euclidean Distance (L2)

Euclidean distance is the straight-line distance between two points:

```
d_E(a, b) = sqrt((a1-b1)^2 + (a2-b2)^2 + ... + (an-bn)^2)
```

Use it when magnitude matters: you want to treat a point that is far away in absolute terms as
genuinely dissimilar. It is the natural metric for tabular data where all features are on comparable
scales after normalization. Euclidean distance is the default metric for k-NN on numeric features.

[MS-Learn: Azure Cosmos DB documents Euclidean distance as "the straight-line distance between two
points" and notes it is best for "spatial data, when magnitude matters." Source:
quickstart-vector-store-python, distance-metrics.]

### Cosine Similarity

Cosine similarity measures the angle between two vectors, not the distance between their tips:

```
cos_sim(a, b) = (a · b) / (||a|| * ||b||)
```

The result ranges from -1 to 1. Two vectors pointing in the same direction score 1; orthogonal
vectors score 0. Cosine similarity is the right metric when magnitude is noise. A customer who
bought three items in the same categories as a customer who bought thirty items should be considered
similar; raw counts differ, but the direction (proportional preference) is aligned.

[MS-Learn: Azure AI Foundry documents that "cosine similarity measures the cosine of the angle
between two vectors projected in a multidimensional space. Two documents might be far apart by
Euclidean distance because of size, they could still have a smaller angle between them and therefore
higher cosine similarity." Source: understand-embeddings, cosine-similarity.]

### Manhattan Distance (L1)

Manhattan distance sums the absolute differences along each axis:

```
d_M(a, b) = |a1-b1| + |a2-b2| + ... + |an-bn|
```

The name is the grid-city analogy: you walk north-south and east-west, never diagonally. Manhattan
distance is more robust to outliers than Euclidean, because large differences on a single axis are
not squared. In high-dimensional sparse data it often outperforms L2.

[MS-Learn: Azure Cosmos DB documents Manhattan distance as measuring "the distance between two
points by adding up the absolute differences between their coordinates." Source:
distance-functions.]

## Why Scaling Changes Everything

Consider a two-feature dataset: age (range 20-80) and annual income (range 20,000-200,000). In raw
Euclidean space, the income dimension dominates: a one-unit change in age and a one-unit change in
income contribute equally to the formula, but one unit of income is irrelevant while twenty years of
age is enormous. The distance metric is measuring the income feature and almost ignoring age.

The fix is normalization before distance computation. Two common forms:

- **Min-max scaling** linearly rescales each feature to [0, 1]: `x_scaled = (x - x_min) / (x_max - x_min)`. Every feature occupies the same range.
- **Z-score standardization** centers each feature at mean 0 with standard deviation 1: `x_scaled = (x - mean) / std`. Features with different natural variances are placed on a common scale.

[MS-Learn: Azure Machine Learning's Normalize Data component documents both transformations.
"ZScore: Converts all values to a z-score." "MinMax: The min-max normalizer linearly rescales
every feature to the [0,1] interval." Azure AutoML applies normalization automatically as part of
featurization because some algorithms "are sensitive to features that are on different scales."
Source: normalize-data, how-to-configure-auto-features.]

k-NN is one of the algorithms most sensitive to this problem: the entire prediction is a distance
calculation. Unscaled features produce neighbors determined by the largest-range column. Scaled
features give every dimension a fair vote.

## What a Feature Matrix Encodes

The matrix `X` of shape (n_samples, n_features) is not just data storage. It encodes a geometric
structure: the neighborhood graph of your observations. Points near each other in feature space
share similar feature combinations. The ML engineer's job is to set up that geometry correctly
before any model sees the data: the right features, the right metric, the right scale.

This is the conceptual foundation for k-NN, for PCA (which finds the directions of maximum variance
in the matrix), and for any distance-based retrieval system. A retrieval system using Azure AI
Search and cosine similarity is solving the same problem as k-NN: find the k closest points to a
query in a high-dimensional feature space. The math is identical; only the scale and the data type
of the features differ.

## Core Concepts

- A dataset row is a vector; the full dataset is a matrix of shape (n_samples, n_features); every ML algorithm reads this shape.
- The dot product `a · b = ||a|| * ||b|| * cos(θ)` is the engine behind cosine similarity: it measures how much two vectors point in the same direction, independent of their lengths.
- Euclidean distance measures straight-line separation (use when magnitude matters); cosine similarity measures angle (use when magnitude is noise); Manhattan distance sums absolute differences (use for robustness or sparse data).
- Feature scaling (min-max or z-score) is required before any distance-based algorithm; unscaled features hand the metric to the highest-range column.

<div class="claude-handoff" data-exercise="draft/exercises/01-feature-vectors/">

**Build It in Claude Code**: Load the Iris dataset with scikit-learn, compute pairwise Euclidean and cosine distances between the first five rows using NumPy (no sklearn distance helpers), print both matrices side by side, and write one sentence per metric explaining which pair is most similar and why the two metrics disagree on at least one pair.

</div>
