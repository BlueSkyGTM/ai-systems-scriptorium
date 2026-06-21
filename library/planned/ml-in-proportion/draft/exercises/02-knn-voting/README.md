# Exercise: k-NN Classifier From Scratch

## Goal

Implement the `KNNClassifier` class from lesson 02 using only NumPy, fit it on an 80/20 train/test
split of the Iris dataset, sweep k over {1, 3, 5, 11, 21} and two metrics (Euclidean, cosine),
report accuracy for each combination, and plot accuracy vs k for both metrics on a single axes.

## Why

k-NN is the algorithm that makes the bias-variance tradeoff visible without any abstraction. You
can see the jagged decision boundary at k=1 and the over-smoothed one at k=21. Implementing it
from scratch means the parameter sweep is not a hyperparameter-search black box: you know exactly
which lines of code change when k changes. Building this classifier positions you to reason about
any distance-based system, including production vector search.

## Steps

1. Set up the data split with a fixed random seed so results are reproducible:
   ```python
   from sklearn.datasets import load_iris
   from sklearn.model_selection import train_test_split
   import numpy as np

   iris = load_iris()
   X_train, X_test, y_train, y_test = train_test_split(
       iris.data, iris.target, test_size=0.2, random_state=42, stratify=iris.target
   )
   ```
   Note: `stratify=iris.target` ensures each class is proportionally represented in the split.

2. Apply z-score normalization using only NumPy. Compute mean and std on the training set; apply
   the same transformation to both train and test (no peeking at test statistics):
   ```python
   mean = X_train.mean(axis=0)
   std  = X_train.std(axis=0)
   X_train_s = (X_train - mean) / std
   X_test_s  = (X_test  - mean) / std
   ```

3. Copy the `KNNClassifier` class from lesson 02 verbatim. Do not import from sklearn.

4. Run the sweep:
   ```python
   ks = [1, 3, 5, 11, 21]
   metrics = ["euclidean", "cosine"]
   results = {}
   for metric in metrics:
       for k in ks:
           clf = KNNClassifier(k=k, metric=metric)
           clf.fit(X_train_s, y_train)
           y_pred = clf.predict(X_test_s)
           acc = (y_pred == y_test).mean()
           results[(metric, k)] = acc
           print(f"metric={metric}, k={k}: accuracy={acc:.3f}")
   ```

5. Plot accuracy vs k for both metrics on a single axes using matplotlib:
   ```python
   import matplotlib.pyplot as plt
   fig, ax = plt.subplots()
   for metric in metrics:
       accs = [results[(metric, k)] for k in ks]
       ax.plot(ks, accs, marker="o", label=metric)
   ax.set_xlabel("k")
   ax.set_ylabel("Accuracy (test set)")
   ax.set_title("k-NN accuracy vs k, Iris dataset (80/20 split, z-score scaled)")
   ax.legend()
   plt.tight_layout()
   plt.savefig("knn_accuracy_vs_k.png", dpi=150)
   print("Plot saved to knn_accuracy_vs_k.png")
   ```

6. Read the plot. Write a comment in your script answering two questions:
   - At what value of k does each metric peak, and what does that tell you about the structure of
     the Iris feature space?
   - Do the two metrics agree on the best k, or disagree? If they disagree, why might that happen?

## Done When

- The accuracy table prints cleanly (all ten combinations).
- `knn_accuracy_vs_k.png` is saved and shows two distinct curves.
- Your script contains at least two sentences answering the interpretation questions in step 6.
- The best accuracy on the test set is at or above 93% for at least one metric-k combination (Iris
  is a clean dataset; lower than that signals a normalization or split bug).

## Stretch

Add a third metric, Manhattan distance, to the sweep and plot. Then: without normalization (using
raw feature values), rerun the Euclidean sweep and compare the accuracy curve to the normalized
version. Write a short comment explaining the difference in terms of the feature scales in the Iris
dataset. This is the experiment that makes the "normalize before distance" rule concrete rather than
a rule to memorize.
