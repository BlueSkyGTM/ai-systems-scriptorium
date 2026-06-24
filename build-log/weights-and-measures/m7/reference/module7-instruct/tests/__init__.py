"""
tests package for Module 7: Instruction-Tuned LLM with Behavioral Regression Suite.

This package contains pytest-based regression tests that verify:
1. The LoRA fine-tuning pipeline (tune.py) produces a valid adapter.
2. The behavioral regression suite (regress.py) correctly gates tuned vs. base model quality.
3. Negative cases (e.g., random-weight adapters) are properly blocked.
"""

import random

# Fixed seeds for deterministic test behavior — mirrors the seeds used
# in tune.py, regress.py, and smoke.py so the entire suite is reproducible.
TORCH_SEED = 42
RANDOM_SEED = 42

# Convenience paths used across test modules.
FIXTURE_DIR = "fixtures"
OUTPUTS_DIR = "outputs"
ADAPTER_DIR = "outputs/adapter"

# MLflow offline tracking URI (must match regress.py / smoke.py).
MLFLOW_URI = "sqlite:///outputs/mlruns.db"


def reset_seeds() -> None:
    """Reset global RNG seeds to fixed values.

    Call this inside individual test functions or fixtures when a test
    needs a clean, deterministic RNG state. Note: torch is imported lazily
    inside this function to keep the package import side-effect free.
    """
    import torch

    random.seed(RANDOM_SEED)
    torch.manual_seed(TORCH_SEED)


__all__ = [
    "TORCH_SEED",
    "RANDOM_SEED",
    "FIXTURE_DIR",
    "OUTPUTS_DIR",
    "ADAPTER_DIR",
    "MLFLOW_URI",
    "reset_seeds",
]
