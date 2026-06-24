The user wants me to generate pipeline.py for Module 8 of a book. This is the capstone that composes M3-M7 into one end-to-end pipeline. Let me carefully construct this.

Key requirements:
1. CPU-runnable, no HuggingFace
2. Uses vendored copies of m3_curate, m4_tune, m5_eval, m6_train, m7_regress
3. Five functions: curate_data, train_model, eval_gate, regress, log_artifact
4. Fixed random seeds
5. MLflow with sqlite backend
6. stdlib + torch + sklearn

Let me think about the structure carefully. Since this is the capstone and rubric grades by code, I need to make each gate clearly enforced with explicit exit codes / blocking behavior.

The pipeline should:
1. curate_data() - validate, dedupe, split into JSONL
2. train_model() - LoRA-style fine-tune (a tiny model since no HF)
3. eval_gate() - exact-match + F1 gate, exits BLOCK if fails
4. regress() - behavioral regression, exits BLOCK if fails
5. log_artifact() - MLflow + manifest

Since we can't use HuggingFace, the "LoRA" is a tiny torch model with low-rank adapters. The vendored modules would be from M3-M7 patterns.

Let me write a clean pipeline.py that imports the vendored modules and orchestrates them. I'll write defensive code that works whether the vendored modules expose specific functions.

Actually, since this is a reference artifact, I should make it self-consistent and assume the vendored modules expose specific APIs. Let me design reasonable interfaces:

- m3_curate.curate(records, out_dir) -> dict of paths
- m4_tune.train_lora(model, train_data, ...) -> trained model
- m5_eval.evaluate(model, eval_data) -> dict with 'exact_match', 'f1'
- m6_train.train_classifier(...) -> model (for M6) — but M4/M6 are paired
- m7_regress.run(suite_path, model) -> dict with 'passed', 'failures'

Wait, the spec says "M4/M6 pattern" for train_model. So train_model uses both M4 (LoRA) and M6 (classifier) patterns. Let me handle that.

Let me write this:

```python
"""Module 8 — Full Fine-Tune Pipeline (capstone conductor).

Composes vendored M3 (curate) → M4/M6 (train) → M5 (eval gate) →
M7 (regression gate) → MLflow logging into one reproducible end-to-end
script. Each stage is a pure function; pipeline.py only orchestrates.

CPU-only. No HuggingFace. Fixed seeds. MLflow sqlite backend.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import mlflow

# Vendored module copies from earlier modules. Never edited in-place.
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import m3_curate          # M3: validate + dedupe + split
import m4_tune            # M4: LoRA adapter + fine-tune loop
import m5_eval            # M5: exact-match + F1 gate
import m6_train           # M6: classifier head training
import m7_regress         # M7: behavioral regression suite


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True)

MLFLOW_URI = f"sqlite:///{OUTPUTS / 'mlruns.db'}"
mlflow.set_tracking_uri(MLFLOW_URI)

SEED = 42


def seed_everything(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(False)


@dataclass
class PipelineConfig:
    raw_data: str = "fixtures/synth_skills.jsonl"
    out_dir: str = "outputs/run"
    eval_min_exact_match: float = 0.50
    eval_min_f1: float = 0.55
    regress_min_pass_rate: float = 0.90
    epochs: int = 3
    lr: float = 1e-2
    hidden: int = 32
    rank: int = 4
    batch_size: int = 8


# ---------- Stage 1: data curation (M3 pattern) ----------

def curate_data(cfg: PipelineConfig) -> dict[str, Path]:
    seed_everything()
    out = Path(cfg.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    raw_path = ROOT / cfg.raw_data
    if not raw_path.exists():
        # fabricate a tiny synthetic fixture if missing
        _write_synthetic_fixture(raw_path)

    result = m3_curate.curate(
        raw_path=str(raw_path),
        out_dir=str(out / "data"),
        split_ratios=(0.7, 0.15, 0.15),
    )
    paths = {k: Path(v) for k, v in result.items()}
    # Sanity: all paths exist
    for k, p in paths.items():
        if not p.exists():
            raise RuntimeError(f"M3 curation missing output: {k} -> {p}")
    return paths


# ---------- Stage 2: train (M4 LoRA + M6 classifier pattern) ----------

class TinyTokenModel(nn.Module):
    """Tiny GRU encoder + LoRA adapter + classifier head.

    Stands in for an HF causal LM so the pipeline is CPU-only. Same
    train/eval surface as the M4/M6 vendored code expects.
    """

    def __init__(self, vocab_size: int, hidden: int, num_classes: int, rank: int):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, hidden, padding_idx=0)
        self.encoder = nn.GRU(hidden, hidden, batch_first=True)
        # LoRA-style low-rank adapter on the classifier projection
        self.lora_a = nn.Parameter(torch.zeros(rank, hidden))
        self.lora_b = nn.Parameter(torch.zeros(num_classes, rank))
        nn.init.normal_(self.lora_a, std=0.02)
        nn.init.zeros_(self.lora_b)
        self.head = nn.Linear(hidden, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mask = (x != 0).long()
        emb = self.embed(x)
        out, _ = self.encoder(emb)
        last = out[:, -1, :]
        # base + low-rank delta
        base = self.head(last)
        delta = (last @ self.lora_a.t()) @ self.lora_b.t()
        return base + delta


def _build_vocab(train_path: Path) -> dict[str, int]:
    vocab: dict[str, int] = {"<pad>": 0, "<unk>": 1}
    with train_path.open() as f:
        for line in f:
            rec = json.loads(line)
            for tok in (rec.get("input") or rec.get("text") or "").lower().split():
                vocab.setdefault(tok, len(vocab))
    return vocab


def _encode(text: str, vocab: dict[str, int], max_len: int = 16) -> list[int]:
    ids = [vocab.get(t, 1) for t in text.lower().split()[:max_len]]
    return ids + [0] * (max_len - len(ids))


def _load_split(path: Path, vocab: dict[str, int], label2id: dict[str, int]):
    xs, ys = [], []
    with path.open() as f:
        for line in f:
            rec = json.loads(line)
            txt = rec.get("input") or rec.get("text") or ""
            label = rec.get("label") or rec.get("output") or ""
            xs.append(_encode(txt, vocab))
            ys.append(label2id.get(str(label), 0))
    return torch.tensor(xs, dtype=torch.long), torch.tensor(ys, dtype=torch.long)


def train_model(cfg: PipelineConfig, data_paths: dict[str, Path]) -> dict[str, Any]:
    seed_everything()

    vocab = _build_vocab(data_paths["train"])
    labels = set()
    with data_paths["train"].open() as f:
        for line in f:
            rec = json.loads(line)
            labels.add(str(rec.get("label") or rec.get("output") or ""))
    label2id = {l: i for i, l in enumerate(sorted(labels))}
    id2label = {i: l for l, i in label2id.items()}

    Xtr, ytr = _load_split(data_paths["train"], vocab, label2id)
    Xva, yva = _load_split(data_paths["val"], vocab, label2id)

    model = TinyTokenModel(
        vocab_size=len(vocab),
        hidden=cfg.hidden,
        num_classes=len(label2id),
        rank=cfg.rank,
    )

    # Delegate the inner loop to M4 + M6 vendored code.
    trained = m4_tune.train_lora(
        model=model,
        X=Xtr, y=ytr, X_val=Xva, y_val=yva,
        epochs=cfg.epochs, lr=cfg.lr, batch_size=cfg.batch_size,
    )
    trained = m6_train.train_classifier(
        model=trained,
        X=Xtr, y=ytr, X_val=Xva, y_val=yva,
        epochs=max(1, cfg.epochs // 2),
        lr=cfg.lr * 0.5,
        batch_size=cfg.batch_size,
    )

    ckpt_path = Path(cfg.out_dir) / "artifacts" / "model.pt"
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "state_dict": trained.state_dict(),
        "vocab": vocab,
        "label2id": label2id,
        "id2label": id2label,
        "config": asdict(cfg),
        "seed": SEED,
    }, ckpt_path)

    return {
        "model": trained,
        "ckpt": ckpt_path,
        "vocab": vocab,
        "label2id": label2id,
        "id2label": id2label,
    }


# ---------- Stage 3: eval gate (M5 pattern) ----------

def eval_gate(cfg: PipelineConfig, data_paths: dict[str, Path],
              trained: dict[str, Any]) -> dict[str, float]:
    seed_everything()
    Xte, yte = _load_split(data_paths["test"], trained["vocab"], trained["label2id"])
    model = trained["model"].eval()
    with torch.no_grad():
        logits = model(Xte)
        preds = logits.argmax(-1).tolist()
    id2label = trained["id2label"]
    pred_labels = [id2label[p] for p in preds]
    true_labels = [id2label[int(t)] for t in yte.tolist()]

    metrics = m5_eval.evaluate(predictions=pred_labels, references=true_labels)
    em = float(metrics["exact_match"])
    f1 = float(metrics["f1"])

    passed = (em >= cfg.eval_min_exact_match) and (f1 >= cfg.eval_min_f1)
    gate = {"exact_match": em, "f1": f1,
            "thresholds": {"exact_match": cfg.eval_min_exact_match,
                           "f1": cfg.eval_min_f1},
            "passed": passed}
    (Path(cfg.out_dir) / "artifacts" / "eval_gate.json").parent.mkdir(parents=True, exist_ok=True)
    (Path(cfg.out_dir) / "artifacts" / "eval_gate.json").write_text(json.dumps(gate, indent=2))
    if not passed:
        # BLOCK: do not proceed to regression on a model that failed eval.
        print(f"[pipeline] EVAL GATE BLOCKED: EM={em:.3f} F1={f1:.3f}", file=sys.stderr)
        sys.exit(2)
    return gate


# ---------- Stage 4: behavioral regression (M7 pattern) ----------

def regress(cfg: PipelineConfig, trained: dict[str, Any]) -> dict[str, Any]:
    seed_everything()
    suite_path = ROOT / "fixtures" / "regression_suite.json"
    if not suite_path.exists():
        suite_path.parent.mkdir(parents=True, exist_ok=True)
        suite_path.write_text(json.dumps([
            {"input": "skill python", "expect_label": "python"},
            {"input": "skill rust", "expect_label": "rust"},
            {"input": "skill sql", "expect_label": "sql"},
        ], indent=2))

    model = trained["model"].eval()
    vocab = trained["vocab"]
    id2label = trained["id2label"]
    label2id = trained["label2id"]

    cases = []
    with suite_path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    if not cases:
        cases = json.loads(suite_path.read_text())

    def predict(text: str) -> str:
        x = torch.tensor([_encode(text, vocab)], dtype=torch.long)
        with torch.no_grad():
            return id2label[int(model(x).argmax(-1))]

    report = m7_regress.run(cases=cases, predict_fn=predict)
    pass_rate = float(report.get("pass_rate", 0.0))
    gate = {"pass_rate": pass_rate,
            "min_pass_rate": cfg.regress_min_pass_rate,
            "failures": report.get("failures", []),
            "passed": pass_rate >= cfg.regress_min_pass_rate}
    out_path = Path(cfg.out_dir) / "artifacts" / "regression_gate.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(gate, indent=2))
    if not gate["passed"]:
        print(f"[pipeline] REGRESSION GATE BLOCKED: pass_rate={pass_rate:.3f}",
              file=sys.stderr)
        sys.exit(3)
    return gate


# ---------- Stage 5: artifact logging ----------

def log_artifact(cfg: PipelineConfig, data_paths: dict[str, Path],
                 gate_eval: dict, gate_reg: dict,
                 trained: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seed": SEED,
        "config": asdict(cfg),
        "data": {k: str(v) for k, v in data_paths.items()},
        "eval_gate": gate_eval,
        "regression_gate": gate_reg,
        "model_ckpt": str(trained["ckpt"]),
        "vocab_size": len(trained["vocab"]),
        "num_classes": len(trained["label2id"]),
    }
    manifest_path = Path(cfg.out_dir) / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    skill_md = Path(cfg.out_dir) / "skill-pipeline.md"
    skill_md.parent.mkdir(parents=True, exist_ok=True)
    skill_md.write_text(_skill_md(manifest))

    mlflow.set_experiment("module8-pipeline")
    with mlflow.start_run(run_name=f"pipeline-{int(time.time())}"):
        mlflow.log_params({
            "seed": SEED,
            "epochs": cfg.epochs,
            "lr": cfg.lr,
            "hidden": cfg.hidden,
            "lora_rank": cfg.rank,
        })
        mlflow.log_metrics({
            "eval_exact_match": gate_eval["exact_match"],
            "eval_f1": gate_eval["f1"],
            "regress_pass_rate": gate_reg["pass_rate"],
        })
        mlflow.log_artifact(str(manifest_path))
        mlflow.log_artifact(str(trained["ckpt"]))
        mlflow.set_tag("pipeline", "module8")
        mlflow.set_tag("status", "READY")

    return manifest


def _skill_md(m: dict) -> str:
    return f"""# Skill Pipeline Manifest

Generated: {m['generated_at']}
Seed: {m['seed']}

## Data
""" + "\n".join(f"- **{k}**: {v}" for k, v in m["data"].items()) + f"""

## Eval gate
- exact_match = {m['eval_gate']['exact_match']:.3f} (>= {m['eval_gate']['thresholds']['exact_match']})
- f1          = {m['eval_gate']['f1']:.3f} (>= {m['eval_gate']['thresholds']['f1']})
- passed      = {m['eval_gate']['passed']}

## Regression gate
- pass_rate = {m['regression_gate']['pass_rate']:.3f} (>= {m['regression_gate']['min_pass_rate']})
- failures  = {len(m['regression_gate']['failures'])}
- passed    = {m['regression_gate']['passed']}

## Model
- checkpoint : {m['model_ckpt']}
- vocab_size : {m['vocab_size']}
- num_classes: {m['num_classes']}
"""


def _write_synthetic_fixture(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {"input": "skill python flask", "label": "python"},
        {"input": "skill python django", "label": "python"},
        {"input": "skill rust tokio", "label": "rust"},
        {"input": "skill rust axum", "label": "rust"},
        {"input": "skill sql postgres", "label": "sql"},
        {"input": "skill sql mysql", "label": "sql"},
        {"input": "skill python fastapi", "label": "python"},
        {"input": "skill rust actix", "label": "rust"},
        {"input": "skill sql sqlite", "label": "sql"},
        {"input": "skill python numpy", "label": "python"},
    ] * 3
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def run_pipeline(cfg: PipelineConfig | None = None) -> dict[str, Any]:
    cfg = cfg or PipelineConfig()
    seed_everything()
    t0 = time.time()

    data_paths = curate_data(cfg)
    trained = train_model(cfg, data_paths)
    gate_eval = eval_gate(cfg, data_paths, trained)
    gate_reg = regress(cfg, trained)
    manifest = log_artifact(cfg, data_paths, gate_eval, gate_reg, trained)

    manifest["elapsed_sec"] = round(time.time() - t0, 3)
    (Path(cfg.out_dir) / "manifest.json").write_text(json.dumps