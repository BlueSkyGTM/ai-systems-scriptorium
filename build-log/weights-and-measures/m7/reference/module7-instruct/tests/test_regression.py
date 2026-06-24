"""pytest suite for the M7 instruction-tuned artifact.

Builds the base + adapter once per session, then checks the LoRA mechanics, the
behavioural improvement, and the gate's two-sided behaviour (PASS on the real adapter,
BLOCK on a random one).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import regress as regress_mod  # noqa: E402
import tune as tune_mod  # noqa: E402


@pytest.fixture(scope="session")
def built():
    return tune_mod.build()


def test_adapter_is_low_rank(built):
    # The adapter must be a small fraction of the full model (real LoRA ratio).
    assert built["adapter_params"] > 0
    assert built["adapter_params"] < built["total_params"] // 10


def test_artifacts_written(built):
    assert Path(built["base_path"]).exists()
    assert Path(built["adapter_path"]).exists()


def test_base_lacks_new_skill(built):
    base = tune_mod.load_base()
    # The base was never trained on "greet"; it should not answer "hello".
    assert " ".join(tune_mod.generate_response(base, "greet", "alice")) != "hello alice"


def test_tuned_learns_new_skill(built):
    tuned = tune_mod.load_tuned()
    assert " ".join(tune_mod.generate_response(tuned, "greet", "alice")) == "hello alice"


def test_old_skills_preserved(built):
    tuned = tune_mod.load_tuned()
    assert " ".join(tune_mod.generate_response(tuned, "thank", "bob")) == "thanks bob"
    assert " ".join(tune_mod.generate_response(tuned, "bye", "carol")) == "goodbye carol"


def test_gate_passes_on_real_adapter(built):
    m = regress_mod.evaluate()
    assert m["no_regression"]
    assert m["improved"] > 0
    assert m["passed"] is True


def test_gate_blocks_random_adapter(built):
    # A random adapter of identical shape must not pass the gate.
    tuned = tune_mod.load_tuned()
    torch.manual_seed(0)
    for m in tuned.lora_layers():
        m.A.data.normal_()
        m.B.data.normal_()
    base = tune_mod.load_base()
    base_scores = regress_mod.score(base, regress_mod.SUITE)
    bad_scores = regress_mod.score(tuned, regress_mod.SUITE)
    regressed = any(t < b for t, b in zip(bad_scores, base_scores))
    improved = sum(int(t > b) for t, b in zip(bad_scores, base_scores))
    assert regressed or improved == 0  # i.e., the gate would BLOCK


def test_score_primitive():
    base = tune_mod.load_base()
    scores = regress_mod.score(base, regress_mod.SUITE)
    assert len(scores) == len(regress_mod.SUITE)
    assert all(s in (0, 1) for s in scores)
