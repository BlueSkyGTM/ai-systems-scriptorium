# Module 1: The Shape of Data

Every ML algorithm treats an observation as a point in space. That framing is not a metaphor: a row
in a tabular dataset is literally a coordinate, and the algorithm's job is to reason about which
points are close together, which are far apart, and what that geometry implies about the labels. This
module builds that spatial intuition from the ground up, pairing the linear-algebra primitives
(vectors, matrices, dot products, distance metrics) with the first classic-ML algorithm that cannot
function without them: k-nearest neighbors.

k-NN is the sharpest entry point into the book's thesis. The algorithm has no internal model; it
does one thing: measure distance in feature space, rank the neighbors, and vote. Every design
decision in a k-NN system is a question about geometry. What does "close" mean here? Is raw
Euclidean distance the right measure, or does the angle between feature vectors (cosine similarity)
matter more? Does scaling the features change which points are neighbors? Those questions open the
full vocabulary of ML reasoning: distance metrics, normalization, the curse of dimensionality, the
tradeoff between k (the smoothness knob) and overfitting.

By the end of this module you will be able to read a feature matrix as a spatial object, choose a
distance metric with a reason, and implement k-NN from scratch in NumPy.

Two lessons:

1. **Feature Vectors and the Space They Live In**: vectors, matrices, and the geometry of a feature
   space; dot product as a similarity probe; the three distance metrics every ML engineer encounters
   (Euclidean, cosine, Manhattan), when each is correct, and when to reach for the others.
2. **k-Nearest Neighbors: Voting in Feature Space**: the k-NN algorithm from scratch; how the
   choice of k, metric, and feature scaling interact; where k-NN sits in the algorithm cheat sheet
   and why its simplicity makes it a debugging tool.

**What is given.** A preprocessed tabular dataset (UCI Iris, 150 rows, four numeric features) is
provided for all exercises; building the ingestion layer is not this module's job.

**What is deliberately out of scope.** High-dimensional approximate nearest-neighbor search (ANN /
HNSW) is a production-scale retrieval topic; this module covers exact k-NN on small datasets to
keep the geometry clear. PCA and dimensionality reduction are Module 1 adjacent but belong in
Module 6 where their linear-algebra story completes.
