# Antilibrary — Training Internals (out of seam)

> The Made-With-ML seam is MLOps/serving. The model-training machinery below is kept for reference but sits outside the serving seam.

## Out-of-seam modules

| Module/Area | What it does | Why antilibrary |
| :--- | :--- | :--- |
| `data.py` | Loads, cleans, splits, tokenizes, and preprocesses text data into Ray datasets. | Concerns dataset construction and feature engineering — upstream of the version/serve/monitor pipeline. |
| `models.py` | Defines the PyTorch neural network architecture (a finetuned LLM) and its save/load logic. | Model architecture definition is a given input to the MLOps workflow; the curriculum treats the trained artifact as the unit of interest. |
| `train.py` | Orchestrates the distributed model training workload and logs checkpoints/metrics to MLflow. | The training loop itself is outside the seam; only the artifacts and metrics it emits (via MLflow) are in-seam. |
| `tune.py` | Runs distributed hyperparameter tuning experiments using Ray Tune and MLflow tracking. | Hyperparameter search is model development, not serving/monitoring/CI. |
| Notebook Setup/Data/Training sections | Walk through environment setup, data preparation, and model training in an interactive flow. | These sections build the model; the serving seam picks up after a trained, tracked artifact exists. |

## Kept in-seam (for contrast)

In-seam material covers `predict.py`, `serve.py`, `evaluate.py`, `deploy/`, and the experiment-tracking + serving sections of the notebook.
