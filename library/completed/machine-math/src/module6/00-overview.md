# Module 6: Feature Reality

Every module so far assumed clean numeric features. You had arrays of floats, distances worked, gradients flowed, splits made sense. Real data does not arrive that way. A column arrives as a string: "red," "blue," "med," "high." Another arrives with values in the hundreds of thousands next to values near zero. The math you built in Modules 1 through 5 breaks the moment you feed it raw columns without preparing them first. Module 6 is the preparation work.

## The Problem With Raw Data

A KNN classifier from Module 1 measures Euclidean distance. If one feature is "annual income" (range: 20,000 to 200,000) and another is "years of experience" (range: 0 to 40), income dominates every distance calculation. Experience effectively disappears. The model has not learned anything useful about experience; it has learned to measure income with a little noise.

Categorical columns are worse. A decision tree from Module 3 can handle a column that reads 0, 1, or 2. It cannot handle a column that reads "downtown," "rural," or "suburbs." Models read numbers. Encoding turns categories into numbers; scaling puts those numbers on a common footing.

## Four Lessons

**Scaling and Encoding** addresses the core problem: models read numbers, so you must turn raw categories into numbers and put all numeric columns on a common scale. One-hot encoding handles nominal categories (color, neighborhood, country) where no ordering exists. Ordinal encoding handles ordered categories (small/medium/large, low/med/high) where the rank matters. Scaling (z-score, min-max) was built in Module 1 and is reused directly here. The lesson shows both encoding functions from `ml/features.py` and explains which model families need scaling and which do not.

**Naive Bayes** introduces the first classifier that lives or dies on feature quality. It multiplies per-feature likelihoods under a strong independence assumption: each feature is treated as if it were completely unrelated to every other. That assumption is always wrong and often useful. The lesson derives the log-posterior prediction, fits a Gaussian per-class per-feature distribution, and shows why correlated or uninformative features hurt naive Bayes more than they hurt any tree-based model.

**Imbalanced Data** returns to the accuracy-lies problem from Module 5 and attacks it at the data level. Class weighting, random oversampling, and SMOTE each address the root cause differently. The lesson shows what each strategy does to the training distribution and when each one is appropriate.

**Feature Selection** closes the module with the question Module 1 named but did not answer: when does more information hurt? The curse of dimensionality means that adding irrelevant features degrades distance-based and coefficient-based models. Variance thresholding, mutual information, and permutation importance each filter the feature set for different reasons. The lesson shows `select_by_variance` and `select_by_importance` from `ml/features.py` and measures the accuracy difference between all features and selected features.

## The Shared Artifact

All four lessons extend a single file: `exercises/ml/features.py`. This is the feature-engineering library. It starts with `one_hot_encode` and `ordinal_encode` in lesson one, gains `random_oversample`, `random_undersample`, and `class_weights` in lesson three, and closes with `select_by_variance` and `select_by_importance` in lesson four. The Module 7 capstone imports `ml.features` directly alongside `ml.metrics` and `ml.naive_bayes`; what you build here goes straight into the final exam.

Scaling lives in `ml.distances` (built in Module 1). Nothing in this module reimplements it.

## What Is Deliberately Out of Scope

Deep-learning embeddings (Word2Vec, GloVe, BERT) are a different class of encoding; they require neural architecture and belong to a later book. The AutoML featurization pipeline in Azure Machine Learning automates many of the steps in this module, but understanding what it does and why requires building them yourself first.
