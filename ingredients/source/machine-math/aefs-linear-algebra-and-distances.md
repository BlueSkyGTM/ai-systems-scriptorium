# Feature Vectors and the Space They Live In

**Provenance:** Distilled from vault/ai-engineering-from-scratch/phases/01-math-foundations/:
- 01-linear-algebra-intuition/docs/en.md
- 01-linear-algebra-intuition/code/vectors.py
- 02-vectors-matrices-operations/docs/en.md
- 14-norms-and-distances/docs/en.md
- 14-norms-and-distances/code/distances.py

**Scope:** Vectors and matrices as geometry of a feature space; dot product as similarity probe; the three core distance metrics and when each is correct; feature scaling to handle unequal feature ranges.

## Definitions and Formulas

### Vectors and Magnitudes

A vector is a list of numbers. In AI, vectors represent data points, features, or parameters. Coordinates in n-dimensional space.

Example: 2D vector [3, 2] points from origin (0, 0) to (3, 2) on the plane.

Magnitude (L2 norm): the length of a vector.
```
|v| = sqrt(v_1^2 + v_2^2 + ... + v_n^2)
```
Also written as ||v||_2.

Unit vector: a vector divided by its magnitude, so ||v_hat|| = 1.
```
v_hat = v / |v|
```

### Matrices

A matrix is a 2D grid of numbers: m rows x n columns. Notation: (m x n).

Example: A 2x3 matrix has 2 rows and 3 columns:
```
A = [1  2  3]
    [4  5  6]
    
shape = (2, 3)
```

In neural networks, weight matrices transform input vectors into output vectors. A layer with 784 inputs and 128 outputs uses a 128x784 weight matrix.

### Dot Product and Geometric Form

The dot product of two vectors a and b:
```
a · b = a_1*b_1 + a_2*b_2 + ... + a_n*b_n
```

Geometric form (relates to angle theta between the vectors):
```
a · b = ||a|| * ||b|| * cos(theta)
```

Interpretation:
- Same direction: a · b > 0 (similar)
- Perpendicular: a · b = 0 (unrelated)
- Opposite direction: a · b < 0 (dissimilar)

The dot product measures how aligned two vectors are. This is the foundation of similarity search, attention scores, and RAG systems.

### Norms: Measuring Vector Size

A norm measures the "size" of a vector. Every distance function between two vectors can be written as the norm of their difference: d(a, b) = ||a - b||.

#### L1 Norm (Manhattan Distance)

Sum of absolute values of all components:
```
||x||_1 = |x_1| + |x_2| + ... + |x_n|
```

Called Manhattan distance because it measures distance on a city grid (only axis-aligned moves, no diagonals).

Example:
```
Point A = (1, 1)
Point B = (4, 5)

L1 distance = |4-1| + |5-1| = 3 + 4 = 7
```

#### L2 Norm (Euclidean Distance)

Square root of sum of squared components:
```
||x||_2 = sqrt(x_1^2 + x_2^2 + ... + x_n^2)
```

This is straight-line distance. Pythagoras in n dimensions.

Example:
```
Point A = (1, 1)
Point B = (4, 5)

L2 distance = sqrt((4-1)^2 + (5-1)^2) = sqrt(9 + 16) = sqrt(25) = 5.0
```

#### L-infinity Norm (Chebyshev Distance)

Maximum absolute component:
```
||x||_inf = max(|x_1|, |x_2|, ..., |x_n|)
```

The distance between two points is determined by the single dimension where they differ the most.

Example:
```
Point A = (1, 1)
Point B = (4, 5)

L-inf distance = max(|4-1|, |5-1|) = max(3, 4) = 4
```

#### Norm Ordering Property

For any vector and any p1 < p2:
```
||x||_inf <= ||x||_2 <= ||x||_1
```

Higher p values focus on fewer (larger) components.

### Cosine Similarity and Cosine Distance

Cosine similarity measures the angle between two vectors, ignoring their magnitudes:
```
cos_sim(a, b) = (a · b) / (||a||_2 * ||b||_2)
```

Ranges from -1 (opposite directions) to +1 (same direction). Perpendicular vectors have cosine similarity 0.

Cosine distance converts it to a distance:
```
cos_dist(a, b) = 1 - cos_sim(a, b)
```

Ranges from 0 (identical direction) to 2 (opposite direction).

Example:
```
a = (1, 0)    b = (1, 1)

cos_sim = (1*1 + 0*1) / (1 * sqrt(2)) = 1/sqrt(2) = 0.707
cos_dist = 1 - 0.707 = 0.293
```

### Dot Product vs Cosine Similarity

The dot product and cosine similarity are related:
```
a · b = ||a|| * ||b|| * cos(angle)
```

Cosine similarity is the dot product normalized by both magnitudes. When both vectors are already unit-normalized (magnitude = 1), dot product and cosine similarity are identical.

When they differ: dot product includes magnitude information. A vector with larger magnitude gets a higher dot product score. Cosine similarity ignores magnitude entirely.

### Feature Scaling

When features have unequal ranges, the largest-range column dominates distance calculations. Scaling makes all features contribute equally.

#### Min-Max Scaling (Normalization)

Scale each feature to range [0, 1]:
```
x_scaled = (x - x_min) / (x_max - x_min)
```

Preserves the shape of the data. Useful when you want bounded features.

#### Z-Score Standardization

Scale each feature to mean 0 and standard deviation 1:
```
x_scaled = (x - mean) / std_dev
```

Centers the data. Useful for algorithms sensitive to feature scale. Unbounded range.

## Intuitions and Claims

### Vectors and Matrices

- "A vector is just a list of numbers" but geometrically those numbers are coordinates in space. In AI, every data point, every embedding, every feature set is a vector. (01-linear-algebra-intuition/docs/en.md)

- A matrix is a transformation. It can rotate, scale, stretch, or project a vector. In neural networks, weight matrices ARE the model: they transform input into output. (01-linear-algebra-intuition/docs/en.md)

- In a dataset with n samples and d features, the data matrix has shape (n_samples, n_features). Each row is a sample (a point in d-dimensional feature space); each column is a feature. (02-vectors-matrices-operations/docs/en.md)

### Dot Product

- The dot product tells you how similar two vectors are. It is literally how search engines, recommendation systems, and RAG work: find vectors with high dot products. (01-linear-algebra-intuition/docs/en.md)

- Geometric interpretation: a · b = ||a|| * ||b|| * cos(theta). The dot product is the product of magnitudes times the cosine of the angle between them. (01-linear-algebra-intuition/docs/en.md, 14-norms-and-distances/docs/en.md)

### L1 vs L2 Norms and When to Use Each

- L1 norm is robust to outliers because it penalizes all errors linearly. A single huge difference does not dominate; all differences contribute equally. Use L1 for high-dimensional sparse data (text features, one-hot encodings). (14-norms-and-distances/docs/en.md)

- L2 norm is the straight-line distance and is standard for low-to-medium dimensional continuous data where feature scales are comparable. Use for physical distances, spatial data, sensor readings, image similarity at pixel level. (14-norms-and-distances/docs/en.md)

- The norm ordering L-inf <= L2 <= L1 always holds. Higher p values focus on fewer (larger) components. (14-norms-and-distances/docs/en.md, code/distances.py)

### Cosine Similarity Dominates NLP

- Why cosine similarity dominates NLP and embeddings: in text, document length should not affect similarity. A document about cats twice as long as another document about cats should still be "similar." Cosine similarity ignores magnitude (length) and cares only about direction. Two documents with the same word distribution but different lengths point in the same direction and get cosine similarity 1.0. (14-norms-and-distances/docs/en.md)

- When both vectors are L2-normalized (unit magnitude), dot product and cosine similarity are identical. (14-norms-and-distances/docs/en.md)

- Use cosine similarity when you want pure directional similarity. Use dot product when magnitudes carry meaningful information (e.g., popularity or confidence in retrieval systems). (14-norms-and-distances/docs/en.md)

### Feature Scaling

- When features have unequal ranges, the largest-range column dominates distance calculations. An unscaled feature with range [0, 1000] drowns out one with range [0, 1]. Scaling makes all features contribute equally. (Implicit in 14-norms-and-distances/docs/en.md discussion of feature scales)

- Min-max scaling bounds features to [0, 1] and preserves the shape of the data. Z-score standardization centers data to mean 0 and standard deviation 1 and is unbounded but often more stable for algorithms sensitive to scale. (Standard ML practice; encoding present in source materials)

### Connection to Regularization

- L1 regularization (Lasso) adds ||w||_1 to the loss function and drives small weights to exactly zero, performing automatic feature selection. The L1 penalty creates diamond-shaped constraint regions in weight space; corners lie on axes where some weights are zero. (14-norms-and-distances/docs/en.md)

- L2 regularization (Ridge) adds ||w||_2^2 to the loss function and shrinks all weights toward zero proportionally, but does not push weights to exactly zero. The L2 penalty creates circular constraint regions; no corners on axes. (14-norms-and-distances/docs/en.md)

## Worked Numeric Examples

### Vector Magnitude Example (01-linear-algebra-intuition/docs/en.md)

2D vector [3, 2]:
```
magnitude = sqrt(3^2 + 2^2) = sqrt(9 + 4) = sqrt(13) ≈ 3.606
```

### Dot Product Example (01-linear-algebra-intuition/docs/en.md)

a = [1, 2, 3]
b = [4, 5, 6]

```
a · b = 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32
```

### Projection Example (01-linear-algebra-intuition/docs/en.md)

a = [3, 4], b = [1, 0]

```
proj_b(a) = (a · b / b · b) * b
          = (3*1 + 4*0) / (1*1 + 0*0) * [1, 0]
          = 3 * [1, 0]
          = [3, 0]
```

The projection drops the y-component.

### L1, L2, L-inf Distances Example (14-norms-and-distances/code/distances.py)

A = [1, 2, 3]
B = [4, 0, 6]

```
L1 distance = |4-1| + |0-2| + |6-3| = 3 + 2 + 3 = 8
L2 distance = sqrt((4-1)^2 + (0-2)^2 + (6-3)^2) = sqrt(9 + 4 + 9) = sqrt(22) ≈ 4.690
L-inf distance = max(|4-1|, |0-2|, |6-3|) = max(3, 2, 3) = 3
```

Ordering verified: L-inf(3) <= L2(4.69) <= L1(8).

### Cosine Similarity Example (14-norms-and-distances/code/distances.py)

a = [1, 0]    b = [1, 1]

```
a · b = 1*1 + 0*1 = 1
||a|| = sqrt(1^2 + 0^2) = 1
||b|| = sqrt(1^2 + 1^2) = sqrt(2) ≈ 1.414

cos_sim = 1 / (1 * 1.414) = 0.707
cos_dist = 1 - 0.707 = 0.293
```

### Cosine vs Dot Product (14-norms-and-distances/code/distances.py)

a = [1, 2, 3]
b = [2, 4, 6]   (a scaled by 2)
c = [3, 1, 0]   (different direction)

```
cos_sim(a, b) = 1.0     (identical direction)
dot(a, b) = 1*2 + 2*4 + 3*6 = 2 + 8 + 18 = 28

cos_sim(a, c) ≈ 0.286   (different direction)
dot(a, c) = 1*3 + 2*1 + 3*0 = 5

Cosine says a and b are identical (same direction).
Dot product says b is much more similar (includes magnitude).
```

### Edit Distance Example (14-norms-and-distances/code/distances.py)

"kitten" -> "sitting"

```
kitten -> sitten   (substitute k -> s)
sitten -> sittin   (substitute e -> i)
sittin -> sitting  (insert g)

Edit distance = 3
```

### Jaccard Similarity Example (14-norms-and-distances/code/distances.py)

A = {cat, dog, fish}
B = {cat, bird, fish, snake}

```
Intersection = {cat, fish}      size = 2
Union = {cat, dog, fish, bird, snake}  size = 5

Jaccard similarity = 2/5 = 0.4
Jaccard distance = 1 - 0.4 = 0.6
```

## Out of Scope / Hold for Later

- Linear independence, basis, rank, and the rank-deficiency problem in multicollinearity (addressed in 01-linear-algebra-intuition/docs/en.md, but belongs to a later module on dimensionality and invertibility)
- Projection formula and its role in least-squares fitting (mentioned in 01-linear-algebra-intuition/docs/en.md, but deeper geometry deferred)
- Gram-Schmidt orthogonalization and QR decomposition (in 01-linear-algebra-intuition/docs/en.md, but belongs to numerical linear algebra module)
- Determinant and inverse (in 02-vectors-matrices-operations/docs/en.md, but belongs to later module on matrix invertibility)
- Mahalanobis distance and covariance-aware metrics (in 14-norms-and-distances/docs/en.md, but requires covariance estimation and belongs to a later statistics module)
- Edit distance, KL divergence, Wasserstein distance, and set-based metrics (in 14-norms-and-distances/docs/en.md, but outside the "feature space geometry" scope; belong to specialized distance modules for strings, distributions, and sets)
- Nearest neighbor search algorithms (KD-trees, HNSW, LSH, FAISS) and approximate nearest neighbor (in 14-norms-and-distances/docs/en.md, but belongs to a later retrieval and indexing module)
- Connection to regularization and loss functions (mentioned in 14-norms-and-distances/docs/en.md, but deeper treatment belongs to optimization module)
