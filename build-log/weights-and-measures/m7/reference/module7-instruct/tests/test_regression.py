"""tests/test_regression.py — behavioral regression suite for Module 7.

Validates the full pipeline:
  1. Seeds pin RNG state so generations are deterministic on CPU.
  2. tune.py produces a loadable LoRA adapter from a small fixture.
  3. regress.py emits exit code 0 (PASS) with the trained adapter.
  4. regress.py emits exit code 1 (BLOCK) for a random-weight negative control.
  5. MLflow receives metrics under the offline sqlite backend.
  6. The string-level comparison primitives behave as specified.

Run with:  pytest tests/test_regression.py -v
"""

from __future__ import annotations

import json
import os
import random
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
import torch

# --------------------------------------------------------------------------- #
# Path bootstrap                                                              #
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

torch.manual_seed(42)
random.seed(42)

ADAPTER_DIR = ROOT / "outputs" / "adapter"
SMOKE_FIXTURE = ROOT / "tests" / "fixtures" / "smoke_instructions.jsonl"
TUNE_PY = ROOT / "tune.py"
REGRESS_PY = ROOT / "regress.py"
MLFLOW_DB = ROOT / "outputs" / "mlruns.db"


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _run(cmd: list[str], timeout: int = 120, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, **(env or {})},
    )


def _ensure_trained_adapter() -> None:
    """Train a tiny adapter once per test session if it is not already present."""
    if (ADAPTER_DIR / "adapter_config.json").exists():
        return
    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
    proc = _run(
        [sys.executable, str(TUNE_PY),
         "--data", str(SMOKE_FIXTURE),
         "--out", str(ADAPTER_DIR),
         "--steps", "6"],
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"tune.py failed during test bootstrap.\n"
        f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    assert (ADAPTER_DIR / "adapter_config.json").exists(), "adapter_config.json missing"


# --------------------------------------------------------------------------- #
# Session-scoped fixtures                                                     #
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def trained_adapter() -> Path:
    _ensure_trained_adapter()
    return ADAPTER_DIR


@pytest.fixture(scope="session")
def base_model():
    import regress
    return regress.load_base_model()


# --------------------------------------------------------------------------- #
# Determinism / seed sanity                                                   #
# --------------------------------------------------------------------------- #
class TestDeterminism:
    def test_torch_seed_pinned(self):
        torch.manual_seed(42)
        a = torch.rand(8)
        torch.manual_seed(42)
        b = torch.rand(8)
        assert torch.equal(a, b)

    def test_python_seed_pinned(self):
        random.seed(42)
        a = [random.random() for _ in range(8)]
        random.seed(42)
        b = [random.random() for _ in range(8)]
        assert a == b

    def test_base_generation_is_deterministic(self, base_model):
        import regress
        regress.torch.manual_seed(42)
        out1 = regress.generate(base_model, "the quick brown", max_new_tokens=4)
        regress.torch.manual_seed(42)
        out2 = regress.generate(base_model, "the quick brown", max_new_tokens=4)
        assert out1 == out2, "base generation is not deterministic under fixed seed"


# --------------------------------------------------------------------------- #
# Comparison primitives                                                       #
# --------------------------------------------------------------------------- #
class TestComparisonPrimitives:
    def test_exact_match_identical(self):
        from regress import exact_match
        assert exact_match("Paris", "Paris") == 1

    def test_exact_match_case_sensitive(self):
        from regress import exact_match
        assert exact_match("Paris", "paris") == 0

    def test_exact_match_prefix(self):
        from regress import exact_match
        # Tuned is a prefix-extension of base -> still counts as a match
        # because the canonicalized first token matches.
        assert exact_match("Paris, France", "Paris") == 1

    def test_keyword_match_present(self):
        from regress import keyword_match
        assert keyword_match("The capital of France is Paris.", "Paris") == 1

    def test_keyword_match_absent(self):
        from regress import keyword_match
        assert keyword_match("London is large.", "Paris") == 0

    def test_keyword_match_empty_target(self):
        from regress import keyword_match
        # Empty keyword should never match — protects against vacuous passes.
        assert keyword_match("anything", "") == 0


# --------------------------------------------------------------------------- #
# Adapter artifact shape                                                      #
# --------------------------------------------------------------------------- #
class TestAdapterArtifacts:
    def test_config_exists_and_is_json(self, trained_adapter):
        cfg = json.loads((trained_adapter / "adapter_config.json").read_text())
        assert isinstance(cfg, dict)
        assert cfg.get("rank", 0) > 0
        assert cfg.get("alpha", 0) > 0
        assert "base_model" in cfg

    def test_weights_file_exists(self, trained_adapter):
        weights = trained_adapter / "adapter.pt"
        assert weights.exists() and weights.stat().st_size > 0

    def test_adapter_loads_into_base(self, trained_adapter):
        import regress
        model = regress.load_tuned_model(trained_adapter)
        assert model is not None
        # Must be CPU after load on a CPU-only box.
        for p in model.parameters():
            assert p.device.type == "cpu"


# --------------------------------------------------------------------------- #
# Regression decision logic (unit-level)                                      #
# --------------------------------------------------------------------------- #
class TestRegressionDecision:
    def test_passes_when_tuned_equals_base(self, monkeypatch):
        import regress
        prompts = regress.load_regression_prompts()
        monkeypatch.setattr(regress, "generate_base", lambda p, **k: "ok")
        monkeypatch.setattr(regress, "generate_tuned", lambda p, **k: "ok")
        result = regress.run_regression(prompts)
        assert result["decision"] == "PASS"
        assert result["tuned_score"] >= result["base_score"]
        assert result["blocking_cases"] == []

    def test_blocks_when_tuned_degrades(self, monkeypatch):
        import regress
        prompts = regress.load_regression_prompts()
        monkeypatch.setattr(regress, "generate_base", lambda p, **k: "good")
        monkeypatch.setattr(regress, "generate_tuned", lambda p, **k: "bad")
        result = regress.run_regression(prompts)
        assert result["decision"] == "BLOCK"
        assert result["blocking_cases"], "expected at least one blocking case"
        assert all(c["tuned"] < c["base"] for c in result["blocking_cases"])


# --------------------------------------------------------------------------- #
# End-to-end subprocess tests                                                 #
# --------------------------------------------------------------------------- #
class TestEndToEnd:
    def test_regress_passes_with_trained_adapter(self, trained_adapter):
        proc = _run(
            [sys.executable, str(REGRESS