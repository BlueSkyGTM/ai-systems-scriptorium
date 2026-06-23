# Module 1: The Shape of Data

Every row in a tabular dataset is a point in space. That reframing is not a metaphor: a row of
four iris measurements is literally a coordinate in four-dimensional feature space, and the
algorithm's job is to reason about which points cluster together and which do not. This module
pairs the linear-algebra primitives that make that geometry work (vectors, matrices, dot products,
distance metrics, feature scaling) with k-nearest neighbors, the first algorithm in this book and
the one that is pure geometry.

k-NN is the right entry point. It has no internal model, no loss surface, no learned
parameters. It does exactly one thing at prediction time: measure distance in feature space, rank
the neighbors, and let them vote. Every design decision in a k-NN system is a question about
geometry. What does "close" mean in this data? Is straight-line Euclidean distance the right
measure, or does the angle between feature vectors matter more? Does scaling change which points
count as neighbors? Those questions open the full vocabulary of distance-based ML reasoning.

## Two Lessons, One Thread

The module runs in order. The second lesson stands on the first.

**Feature Vectors and the Space They Live In** builds the geometric primitives: what a feature
vector is, how the dot product probes directional alignment, and how the three standard distance
metrics (Euclidean, cosine, Manhattan) encode three different answers to "how far apart?" It also
covers feature scaling, the precondition every distance-based algorithm requires. The exercise
produces `ml/distances.py`: five NumPy functions (three metrics, two scalers) that every
subsequent algorithm in the package reuses.

**k-Nearest Neighbors: Voting in Feature Space** builds the algorithm on top of that foundation.
It imports the `METRICS` dispatch table from `ml/distances.py` directly, so no distance logic is
copied or reimplemented. The exercise produces `ml/knn.py`. Together, `distances.py` and `knn.py`
form the first working piece of the `exercises/ml/` package that the book composes through to the
capstone.

## What Is Given

A preprocessed tabular dataset: UCI Iris, 150 rows, four numeric features (sepal length, sepal
width, petal length, petal width), three classes. An 80/20 stratified split with
`random_state=0` is the fixed evaluation protocol across both lessons. You load the dataset with
scikit-learn; all algorithm logic is from-scratch NumPy.

## What Is Deliberately Out of Scope

**Dimensionality reduction (PCA)** is held for the module where its linear-algebra story
completes. The eigenvalue decomposition that powers PCA uses the same matrix machinery this
module introduces, but understanding what PCA does requires seeing the covariance matrix first. It
belongs later.

**Approximate nearest-neighbor search (ANN)** is the production cousin of exact k-NN. At scale,
brute-force distance computation over millions of vectors is not viable; HNSW, DiskANN, and IVF
indexes trade a small accuracy cost for a massive speed gain. Azure AI Search and Azure Cosmos DB
both implement ANN under the hood when you run a vector query. This module covers exact k-NN on a
small clean dataset because that is what makes the geometry clear. Naming ANN here is useful:
you will recognize the retrieval layer in a RAG pipeline as the same algorithm, running on an
optimized index instead of a brute-force loop.
