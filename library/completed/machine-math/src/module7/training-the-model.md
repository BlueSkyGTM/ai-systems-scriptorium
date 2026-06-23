# Training the Model

The feature matrix is ready: 800 rows, 10 columns, every value a float. Now you hand it to a model and ask for probabilities. The model is `sklearn.ensemble.GradientBoostingClassifier`. You built gradient boosting from scratch in Module 4; sklearn's classifier runs the same algorithm. The difference is that the classifier predicts churn probability, not a regression target, so it uses log loss instead of squared error. The hyperparameters are the same ones Module 4's lesson named: estimator count, learning rate, tree depth, and subsample fraction.

## The Model Stage

The fourth stage of `pipeline.py` is a single block:

```python
    # ------------------------------------------------------------------
    # 4. Train
    # ------------------------------------------------------------------
    clf = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        random_state=42,
    )
    clf.fit(X_train, y_train)
```

Four hyperparameters, each with a reason.

## Justifying Each Hyperparameter

**`n_estimators=200, learning_rate=0.05`**

These two work together. Each estimator is a weak learner, a shallow tree that corrects the previous round's residuals. `learning_rate` scales how much each tree contributes to the running prediction. A higher learning rate means each tree takes a larger step, which learns the training signal faster but overshoots the minimum and overfits. A lower learning rate needs more trees to reach the same training loss. The Module 4 hyperparameter lesson showed this tradeoff directly: the optimal `n_estimators` rises as `learning_rate` falls. At 0.05 and 200 trees, the model takes small steps for a long time, which regularizes the fit. You would need 50 trees at `learning_rate=0.2` to reach roughly the same training loss, but the resulting model would be higher variance.

**`max_depth=4`**

Each tree in the ensemble is a depth-4 decision tree, capable of capturing up to 4-way feature interactions. A depth-4 tree is still a weak learner relative to a full tree, which is what boosting requires. Deeper trees reduce bias but increase variance; at depth 4, each tree is expressive enough to find real splits without memorizing the training set. The Module 3 lesson on overfitting and cross-validation showed what happens when trees grow unconstrained: training accuracy rises, test accuracy falls.

**`subsample=0.8`**

At each boosting round, the algorithm samples 80% of the training rows without replacement before fitting the next tree. This is the stochastic gradient boosting trick from Module 4's boosting lesson: randomness in the sample forces diversity in the trees, which reduces variance. The tradeoff is a slight increase in bias from each individual tree, which the ensemble's averaging absorbs. Subsampling also speeds up training by 20% at essentially no accuracy cost on datasets this size.

**`random_state=42`**

Seeds both the subsampling and any internal randomness. Reproducibility is not a convenience; it is the precondition for comparing runs. A model card that reports AUC 0.8865 is meaningful only if the same number comes up every time.

## The Production Context

In Module 4 you built `ml.ensemble.GradientBoostingRegressor` from scratch. The math you wrote, fitting a shallow tree to the negative gradient of the loss, is exactly what sklearn runs here. The difference is the implementation quality: sklearn's version handles edge cases, runs faster with Cython, and is tested against thousands of datasets. Using it as the production learner while keeping the engineering and evaluation in your own code is the correct separation: you understand what the model does, and you use the tool that does it reliably.

Azure ML can train gradient-boosted models as part of a managed training job, handling compute provisioning and logging ([learn.microsoft.com/en-us/azure/machine-learning/concept-train-machine-learning-model](https://learn.microsoft.com/en-us/azure/machine-learning/concept-train-machine-learning-model)). The pipeline shape you are building here, features in, predictions out, evaluation against a held-out set, is the same shape at exercise scale.

The call that starts the timer is `clf.fit(X_train, y_train)`. On 800 rows and 10 features, it completes in under a second. The predictions come back in the next stage via `clf.predict(X_test)` and `clf.predict_proba(X_test)[:, 1]`. The second column of `predict_proba` is the estimated churn probability for each test row; that probability vector goes to `ml.metrics.roc_auc`.

## Core Concepts

- `n_estimators` and `learning_rate` trade off: more estimators at a lower rate reach similar training loss with lower variance, because each tree's contribution is smaller and cannot overfit alone.
- `max_depth` caps each tree's expressiveness; shallow trees are weak learners by design, which is what boosting requires to correct residuals without memorizing the training set.
- `subsample` below 1.0 introduces stochastic gradient boosting: each round trains on a random row subset, diversifying the ensemble and reducing variance at the cost of a small bias increase.
- Using sklearn's `GradientBoostingClassifier` as the production learner while calling `ml.features` and `ml.metrics` from your own package is the correct division: you own the engineering and the evaluation; you delegate the optimized fit to the library.

<div class="claude-handoff" data-exercise="exercises/module7/training-the-model/">

**Build It in Claude Code:** Add the model stage to `exercises/module7/pipeline.py` with the exact hyperparameters above. The gate is green when the pipeline trains and produces 200 predictions with probabilities in [0, 1].

</div>
