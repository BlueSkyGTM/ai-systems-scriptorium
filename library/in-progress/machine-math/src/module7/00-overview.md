# Module 7: The Portfolio Artifact

Six modules ago you built `ml.distances` and wrote your first KNN classifier. Since then you have added gradient descent, linear regression, logistic regression, decision trees, random forests, gradient boosting, a full metrics library, and a feature-engineering toolkit. None of those pieces have met each other. Module 7 changes that.

The capstone assembles everything into one runnable, graded ML system on a real tabular dataset. You engineer features with your own `ml.features`, train a gradient-boosted classifier, evaluate honestly with your own `ml.metrics` (AUC, F1, subgroup slicing), write a model card, and grade the run with `rubric.py` against six criteria in code. The pipeline is called `pipeline.py`, and it imports `ml.features` and `ml.metrics` off disk. That import is the proof: if your from-scratch code is broken, the pipeline fails at import time, not silently at the wrong answer.

## What You Are Building

The dataset is a synthetic churn table: 1,000 customers, six columns, about 30% positive churn. The signal is learnable: short tenure, high monthly charge, and the basic plan all push churn probability up. The model is `sklearn.ensemble.GradientBoostingClassifier`, which runs the same algorithm you built from scratch in Module 4. The engineering and the evaluation are yours.

The output is a GitHub-postable artifact. An interviewer clones the repo, runs one command, and sees a model card with real numbers on a real dataset, graded by code against six criteria. The math is visible in every result.

## Four Lessons

**The Dataset and the Feature Pipeline** shows you how to generate the churn dataset with `generate_data.py` and how the load-and-engineer stage of `pipeline.py` works. You one-hot encode the plan type and region columns using `ml.features.one_hot_encode`, z-score the three numeric columns using `ml.features.zscore`, and hold out 20% of rows in a stratified split. Every call goes through your own code.

**Training the Model** walks through the model stage of `pipeline.py`: `GradientBoostingClassifier` with four hyperparameters, each justified against the bias-variance thread from Modules 2 through 4. More estimators and a lower learning rate, shallow trees, and subsampling are not magic numbers; they are the bias-variance tradeoff made concrete.

**Honest Evaluation and Slicing** covers the evaluation stage: `ml.metrics.roc_auc`, `ml.metrics.f1`, and `ml.metrics.slice_metric` over the `region` subgroup. Aggregate AUC above 0.75 is the floor. Slicing surfaces where the model underperforms, which is the information you need before a model ships.

**The Model Card and the Rubric** closes the module. You read the generated `MODEL_CARD.md` and then run `rubric.py`, which checks six criteria in code: that the pipeline runs, that feature engineering was applied, that AUC clears the floor, that slicing was done, that the model card has required sections, and that the pipeline was versioned. A deliberately deficient run must fail the criterion it offends.

## The Shared Artifact

`pipeline.py` is the terminal node of the full book. It composes `ml.features` and `ml.metrics` off disk: real imports, real calls, real results. Azure ML pipelines work the same way at production scale: each stage is a separate, reusable step, and the pipeline chains their outputs ([learn.microsoft.com/en-us/azure/machine-learning/concept-ml-pipelines](https://learn.microsoft.com/en-us/azure/machine-learning/concept-ml-pipelines)). What you build in this module is that idea at exercise scale, with the math you built from scratch as the evaluation layer.

## What Is Deliberately Out of Scope

Hyperparameter search (Grid Search, Bayesian optimization) would require a held-out validation set and a search loop. It belongs to a production MLOps workflow and is not the point here. The point is that you can justify every number already in the config. Azure ML AutoML automates featurization and hyperparameter selection ([learn.microsoft.com/en-us/azure/machine-learning/concept-automated-ml](https://learn.microsoft.com/en-us/azure/machine-learning/concept-automated-ml)), but understanding what it does requires having built the pieces yourself.
