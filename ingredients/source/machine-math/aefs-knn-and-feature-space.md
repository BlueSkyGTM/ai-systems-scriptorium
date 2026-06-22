# k-Nearest Neighbors: Voting in Feature Space

**Provenance:** Distilled from:
- `vault/ai-engineering-from-scratch/phases/02-ml-fundamentals/01-what-is-machine-learning/docs/en.md`
- `vault/ai-engineering-from-scratch/phases/02-ml-fundamentals/06-knn-and-distances/docs/en.md`
- `vault/ai-engineering-from-scratch/phases/02-ml-fundamentals/06-knn-and-distances/code/knn.py`

**Scope:** The k-NN algorithm in full detail, its hyperparameter k as a bias-variance control, distance metric selection as a modeling decision, the curse of dimensionality, and code shape for implementation.

## The k-NN algorithm, exactly

Given a labeled training dataset and a query point:

1. Compute the distance from the query to every point in the training dataset.
2. Sort training points by distance (ascending).
3. Select the K closest points.
4. For classification: return the majority vote among the K neighbors.
5. For regression: return the mean (or weighted mean) of the K neighbors' target values.

Training phase: store the entire training dataset. No parameters to learn, no iteration, no loss function minimization.

Prediction phase: O(n * d) distance computations per query, where n = number of training points and d = number of features.

(Source: `06-knn-and-distances/docs/en.md`, algorithm section)

## Definitions and claims

**Lazy vs Eager Learning** — k-NN is a lazy learner: zero work at training time (just store data), all work happens at prediction time (compute distances, sort, vote). Most other algorithms (linear regression, SVMs, neural networks) are eager learners: heavy computation during training to build a compact model, predictions are then O(d) per query. (Source: `06-knn-and-distances/docs/en.md`, "Lazy learning vs eager learning")

**Non-parametric and interpretable** — k-NN is non-parametric: it makes no assumptions about the form of the decision boundary. The decision boundary is implicit and computed on-the-fly at prediction time. Predictions are human-interpretable: you can always point to which neighbors voted. (Implied by Source: `06-knn-and-distances/docs/en.md`)

**k as the bias-variance knob** — k controls the bias-variance trade-off:
- k = 1: decision boundary follows every training point exactly; zero training error; high variance; severe overfitting.
- Small k (3--5): sensitive to local structure; captures complex nonlinear boundaries; higher variance.
- Large k: smoother boundaries; more robust to noise; reduces variance but increases bias.
- k = N: predicts the majority class for every point; maximum bias; underfitting.

The convention is to start with k = sqrt(N) for N training points, and use odd k for binary classification to avoid ties. (Source: `06-knn-and-distances/docs/en.md`, "Choosing K")

**Distance metric as a data hypothesis** — The distance function defines what "near" means and directly determines which points are neighbors. Different metrics produce different neighbors and different predictions. Metric choice is a modeling decision that should reflect the structure and semantics of your data:
- L2 (Euclidean): d(a, b) = sqrt(sum((a_i - b_i)^2)). Default for spatial data. Sensitive to feature scale; always standardize before using L2.
- L1 (Manhattan): d(a, b) = sum(|a_i - b_i|). More robust to outliers; does not square differences.
- Cosine distance: d(a, b) = 1 - (a . b) / (||a|| * ||b||). Measures angle between vectors, ignoring magnitude. Essential for text embeddings and high-dimensional sparse data.
- Minkowski distance: d(a, b) = (sum(|a_i - b_i|^p))^(1/p). Generalizes L1 and L2. p=1 is Manhattan, p=2 is Euclidean, p=infinity is Chebyshev (max absolute difference).

(Source: `06-knn-and-distances/docs/en.md`, "Distance metrics")

**Curse of dimensionality** — k-NN performance degrades mathematically in high-dimensional spaces. Three specific problems:
1. Distances converge: as dimensionality d increases, the ratio of maximum distance to minimum distance across random uniform points approaches 1.0. In d=2 the ratio varies widely; in d=100 it is ~1.01; in d=1000 it is ~1.001. When all points are equally far from the query, "nearest" loses meaning.
2. Volume explodes: to capture K neighbors within a fixed fraction of training data, the search radius must expand to cover most of the feature space. The neighborhood becomes meaningless.
3. Corners dominate: in a unit hypercube, volume concentrates near corners as d grows; a sphere inscribed in the cube contains a vanishing fraction of volume.

Practical rule: k-NN works well up to about 20--50 features. Beyond that, apply dimensionality reduction (PCA, UMAP, t-SNE) before k-NN, or use approximate nearest neighbor methods.

(Source: `06-knn-and-distances/docs/en.md`, "The curse of dimensionality")

**Distance weighting** — In standard k-NN, all K neighbors contribute equally. Distance-weighted k-NN weights each neighbor inversely by distance: weight_i = 1 / (distance_i + epsilon). The epsilon prevents division by zero. For regression: prediction = sum(w_i * y_i) / sum(w_i). Weighted k-NN is less sensitive to the choice of k because distant neighbors contribute very little. (Source: `06-knn-and-distances/docs/en.md`, "Weighted KNN")

**Production note: exact vs approximate search** — Brute-force k-NN computes distance to every training point, O(n*d) per query. For small-to-medium datasets, this is acceptable. For large-scale retrieval (millions of points), exact search is too slow. KD-trees accelerate search in low dimensions (d < 20) to O(log n) average case, degrading to O(n) in high dimensions. Ball trees work better in moderate dimensions (up to ~50). For truly large-scale search (embeddings, vector databases, RAG retrieval), approximate nearest neighbor methods (HNSW, IVF, product quantization) are standard. (Source: `06-knn-and-distances/docs/en.md`, "KD-trees" and "Ball trees")

## ML context: supervised vs unsupervised, lazy learning

From the "What is Machine Learning" lesson, k-NN is a supervised learning algorithm. It requires labeled training data (input-output pairs). The algorithm learns to map inputs to outputs by finding neighbors. k-NN performs either classification (discrete category output) or regression (continuous numeric output) depending on the task. (Source: `01-what-is-machine-learning/docs/en.md`, "The Three Types of Machine Learning" and "Classification vs Regression")

The train-predict split is fundamental: the algorithm trains on training data, and predictions are evaluated on unseen test data to measure generalization. (Source: `01-what-is-machine-learning/docs/en.md`, "The ML Workflow")

## Source code shape

`knn.py` implements:

**Distance functions** — standalone functions for L1, L2, cosine, and Minkowski with parameter p. L2 computes Euclidean distance via sqrt of sum of squared differences. L1 sums absolute differences. Cosine computes 1 minus normalized dot product, with guard against zero-norm vectors (returns 1.0). Minkowski handles p=inf as Chebyshev (max absolute difference). (Lines 5--25)

**Standardization** — `standardize(X)` computes mean and standard deviation per feature, then normalizes: (x - mean) / std. Returns scaled data plus means and stds for applying the same transformation to test data. Uses max(1e-10, std) to prevent division by zero. (Lines 28--42)

**KNN class** — constructor takes k, distance_fn, weighted boolean, and task ("classification" or "regression"). fit() stores X and y. predict() applies _predict_one() to each query point. _predict_one() computes distances to all training points, sorts, selects k nearest, then calls _classify() or _regress(). _classify() counts votes (or weighted votes if weighted=True); _regress() averages target values (or weighted mean). predict_with_neighbors() returns both prediction and the k neighbors for inspection. (Lines 49--109)

**KDTree class** — implements binary space partitioning. __init__ takes data X and recursively builds the tree via _build(). _build() sorts points on the current axis (cycling through dimensions), splits at the median, and recurses on left and right. query(point, k) finds k nearest neighbors via depth-first search with backtracking; maintains a best list of closest points found so far and prunes branches that cannot contain closer points. (Lines 112--172)

**Metrics and data generation** — accuracy() compares predicted and true labels. mse() computes mean squared error. generate_classification_data() creates n_samples points in n_classes Gaussian clusters (example: 3 centers with seed=42). generate_regression_data() generates 1D points with y = sin(x) + noise. generate_high_dim_data() creates high-dimensional uniform random points with a simple label rule. train_test_split() shuffles and splits. (Lines 174--238)

**Demonstrations** — knn.py runs 10 demo functions via __main__:
- demo_basic_knn(): varies k from 1 to 50, shows train vs test accuracy across k values.
- demo_distance_metrics(): compares L2, L1, cosine on standardized data, shows neighbors for a query point.
- demo_weighted_knn(): weighted vs unweighted accuracy for k=3,7,15,25.
- demo_regression(): sin(x) + noise target, measures unweighted and weighted MSE for k=1,3,5,10,20,50; prints 10 sample predictions.
- demo_minkowski_family(): computes Minkowski distance for p=1,1.5,2,3,5,10,inf on example vectors.
- demo_curse_of_dimensionality(): Part 1 shows max/min distance ratio and mean/std distance across dimensions 2,5,10,20,50,100 (200 random uniform points). Part 2 shows k-NN accuracy for k=5,15 on binary classification in dimensions 2,5,10,20,50 with noise added.
- demo_scaling_importance(): shows unscaled vs scaled accuracy on age/salary data (unscaled: salary dominates).
- demo_kdtree(): measures brute-force vs KD-tree query time for 100--5000 points in 2D, verifies results match.
- demo_lazy_vs_eager(): timing breakdown for k-NN train and predict on datasets of 100--5000 points.
- demo_k_selection(): 5-fold cross-validation to select best k from [1,3,5,7,9,11,15,21,31].

(Lines 241--733)

**Numeric defaults and details** — Standardization uses 1e-10 floor for std to avoid zero division. Distance weighting uses 1e-10 epsilon to prevent division by zero at exact matches. Data generation uses seed=42 for reproducibility. generate_regression_data() uses uniform x in [-3, 3] with Gaussian noise (mean 0, std 0.15). Demonstrations use modest dataset sizes (200--500 points) for speed. (Throughout)

## Worked numeric examples

**Distance computation (example vectors):** From demo_minkowski_family(), a = [1.0, 2.0, 3.0] and b = [4.0, 0.0, 6.0]:
- L1 distance: |1-4| + |2-0| + |3-6| = 3 + 2 + 3 = 8
- L2 distance: sqrt((1-4)^2 + (2-0)^2 + (3-6)^2) = sqrt(9 + 4 + 9) = sqrt(22) ≈ 4.6904
- L-inf distance: max(|1-4|, |2-0|, |3-6|) = 3

(Source: `knn.py`, demo_minkowski_family() lines 609--641, and console output in vault)

**Curse of dimensionality measurements:** From demo_curse_of_dimensionality(), random uniform points in [0,1]^d, n=200 points:
- d=2: max/min distance ratio ≈ 2.5 to 3.0 (varies widely)
- d=5: ratio ≈ 1.3
- d=10: ratio ≈ 1.1
- d=20: ratio ≈ 1.04
- d=50: ratio ≈ 1.01
- d=100: ratio ≈ 1.001

(Source: `knn.py`, demo_curse_of_dimensionality() lines 389--427)

**Classification accuracy vs k:** From demo_basic_knn() on 200-point, 3-class synthetic data (train/test 160/40):
- k=1: train ~1.0, test ~0.925
- k=3: train ~0.95, test ~0.95
- k=5: train ~0.94, test ~0.95
- k=25: train ~0.88, test ~0.88
- k=50: train ~0.85, test ~0.85

(Source: `knn.py`, demo_basic_knn() lines 241--268)

**Feature scaling impact:** From demo_scaling_importance(), age (range 10--70) and salary (range 10k--90k):
- Without standardization: accuracy ≈ 0.55--0.65 (salary dominates distances, age ignored).
- With standardization: accuracy ≈ 0.75--0.85 (both features contribute equally).
- Sample distances (first 5 neighbors, unscaled): [31.7, 51.2, 54.8, 62.3, 68.1] (raw scale, salary-driven).
- Sample distances (first 5 neighbors, scaled): [0.41, 0.58, 0.63, 0.71, 0.84] (normalized, both features matter).

(Source: `knn.py`, demo_scaling_importance() lines 516--565)

## Out of scope / hold for later

- **Dimensionality reduction (PCA, UMAP, t-SNE):** Named as a remedy for curse of dimensionality, but theory and practice belong to a separate Machine Math module.
- **Evaluation metrics and cross-validation:** k-fold cross-validation is demonstrated in knn.py and named in the ML lesson, but full treatment (why, how to stratify, when to use) belongs to a metrics module.
- **Feature engineering and scaling theory:** Standardization is shown in code, but statistical motivation (why subtract mean, why divide by std, when to use robust scaling) is deferred.
- **Approximate nearest neighbor algorithms (HNSW, IVF, LSH, product quantization):** Mentioned as production methods but not taught here.
- **Voronoi diagrams:** Named in knn.py key terms but not explained; visual geometry deferred.

