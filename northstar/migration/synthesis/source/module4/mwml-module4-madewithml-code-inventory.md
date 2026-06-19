# Module 4 · Made-With-ML — Code Inventory

> Source: `madewithml/` (Python package) + `Makefile`. Seam = serving/MLOps; training internals are antilibrary.

## Modules

| Module | Purpose | Seam category |
| :--- | :--- | :--- |
| `madewithml/__init__.py` | Loads environment variables from a `.env` file upon package import. | `infra` |
| `madewithml/config.py` | Sets up project directory structures, configures MLflow tracking, and establishes logging settings. | `infra` |
| `madewithml/data.py` | Loads, cleans, splits, tokenizes, and preprocesses text data into Ray datasets. | `training` |
| `madewithml/evaluate.py` | Computes overall, per-class, and slicing evaluation metrics on a holdout dataset. | `eval` |
| `madewithml/models.py` | Defines the PyTorch neural network architecture (a finetuned LLM) and its save/load logic. | `training` |
| `madewithml/predict.py` | Loads model checkpoints to execute offline or online inference and retrieve MLflow run artifacts. | `serving` |
| `madewithml/serve.py` | Wraps the predictor in a FastAPI application and deploys it as a Ray Serve deployment. | `serving` |
| `madewithml/train.py` | Orchestrates the distributed model training workload and logs checkpoints/metrics to MLflow. | `training` |
| `madewithml/tune.py` | Runs distributed hyperparameter tuning experiments using Ray Tune and MLflow tracking. | `training` |
| `madewithml/utils.py` | Provides shared functions for reproducibility, data collation, and dictionary/JSON utilities. | `infra` |

## Makefile

| Target | Command | Purpose |
| :--- | :--- | :--- |
| `style` | `black .` <br> `flake8` <br> `python3 -m isort .` <br> `pyupgrade` | Formats code, lints, sorts imports, and upgrades syntax. |
| `clean` | `python notebooks/clear_cell_nums.py` <br> `find . -type f -name "*.DS_Store" -ls -delete` <br> `find . \| grep -E "(__pycache__\|\.pyc\|\.pyo)" \| xargs rm -rf` <br> `find . \| grep -E ".pytest_cache" \| xargs rm -rf` <br> `find . \| grep -E ".ipynb_checkpoints" \| xargs rm -rf` <br> `rm -rf .coverage*` | Executes styling, clears notebook cell numbers, and removes various system and Python caches/artifacts. |
