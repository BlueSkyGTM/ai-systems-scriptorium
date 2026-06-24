The user wants me to generate tune.py for Module 7. Let me think carefully about what this needs:

1. LoRA fine-tune a tiny model (synthetic 2-layer GPT-like Transformer)
2. Small instruction-following dataset (20-50 examples, JSONL chat format)
3. Must run on CPU in < 90 seconds
4. Saves LoRA adapter to outputs/adapter/
5. Fixed random seeds
6. No HuggingFace transformers - stdlib + torch only
7. MLflow sqlite backend
8. Python 3.11+

Let me design this carefully:

**Architecture:**
- A tiny GPT-like Transformer with 2 transformer layers, small d_model (e.g., 64 or 128), small vocab
- LoRA injected into attention weights (q, v projections)
- Train on instruction data formatted as "INSTRUCTION: ... RESPONSE: ..."

**Dataset:**
- Need to create a small JSONL dataset of 20-50 examples
- Could generate a synthetic dataset programmatically (e.g., simple skill: reverse a string, count letters, etc.) since we don't have an external file
- Actually, since this is a self-contained tune.py, I should probably bundle a tiny inline dataset OR generate one programmatically. Let me bundle 20-30 examples inline.

Let me think about what skill to teach. To keep it deterministic and exact-match testable, a simple deterministic skill makes sense. E.g., "Uppercase the following: X" -> "X.upper()". Or "Echo the input: X" -> "X". Or arithmetic. 

Actually, the dataset should be in JSONL chat format. Let me create a file like `data/instruct.jsonl` with examples. But the spec says tune.py should run - so either it reads a file or generates inline. To be safe and self-contained, let me have it generate the data inline AND optionally read from a file if present.

Wait, re-reading: "on a small instruction-following dataset (20-50 examples, JSONL chat format)". So we need to write the JSONL file too. Let me have tune.py generate it to `data/instruct.jsonl` on first run if not present. That makes it self-contained.

Let me design the skill: A simple "greet by name" task. "Greet the user: NAME" -> "Hello, NAME!". This is exact-match testable.

Actually let me make it more interesting - multiple simple skills:
- Reverse: "Reverse: abc" -> "cba"
- Uppercase: "Uppercase: foo" -> "FOO"
- Greet: "Greet: Alice" -> "Hello, Alice!"

But that complicates things. For a small 2-layer model with limited training, let's pick one skill with high consistency. Let me go with: "Echo the input: X" -> "X". Or better, teach it to answer questions like "What is 2+2?" with "4".

Let me keep it really simple: a copy/echo skill that the base model can't do well at zero-shot but learns quickly.

Actually, for the regression test to work, we need the model to learn something the base model doesn't do. Let me use: "Translate to upper: <word>" -> "<WORD>". With a fixed vocabulary of words, the model can learn this mapping.

Hmm but vocab is characters mostly. Let me use character-level tokenization. That keeps vocab small (~100 chars) and makes training fast.

**Tokenization:**
Character-level tokenizer. Vocab = printable ASCII chars + special tokens.

**Model:**
- 2 transformer layers
- d_model = 128
- n_heads = 4
- d_ff = 256
- max_seq_len = 64

**LoRA:**
Inject LoRA into query and value projections of each attention layer. Rank 4-8.

**Training:**
- AdamW, lr=1e-3
- ~20-30 epochs on 30 examples
- Loss only on response tokens

Let me write this carefully.

```python
"""
tune.py — LoRA fine-tune a tiny 2-layer GPT-like model on a small instruction dataset.

CPU-runnable in < 90 seconds. Saves LoRA adapter weights to outputs/adapter/.
Logs training metrics to MLflow (sqlite backend).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

# MLflow (optional but required by spec)
import mlflow

# ----------------------------------------------------------------------------
# Reproducibility
# ----------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
torch.manual_seed(SEED)
os.environ.setdefault("PYTHONHASHSEED", str(SEED))
torch.set_num_threads(max(1, torch.get_num_threads() // 2))

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
DATA_DIR = ROOT / "data"
ADAPTER_DIR = OUTPUTS / "adapter"
MODEL_DIR = OUTPUTS / "base"

OUTPUTS.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------
# MLflow
# ----------------------------------------------------------------------------
mlflow.set_tracking_uri(f"sqlite:///{OUTPUTS / 'mlruns.db'}")
mlflow.set_experiment("module7-instruct-tune")

# ----------------------------------------------------------------------------
# Character-level tokenizer
# ----------------------------------------------------------------------------
class CharTokenizer:
    def __init__(self):
        chars = sorted(set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?'-:"))
        self.itos = ["<pad>", "<bos>", "<eos>", "<unk>"] + chars
        self.stoi = {c: i for i, c in enumerate(self.itos)}
        self.pad_id = 0
        self.bos_id = 1
        self.eos_id = 2
        self.unk_id = 3

    def encode(self, s: str) -> List[int]:
        return [self.stoi.get(c, self.unk_id) for c in s]

    def decode(self, ids: List[int]) -> str:
        return "".join(self.itos[i] for i in ids if i >= 4)

    def __len__(self):
        return len(self.itos)


# ----------------------------------------------------------------------------
# Tiny GPT-like model
# ----------------------------------------------------------------------------
@dataclass
class ModelConfig:
    vocab_size: int = 70
    d_model: int = 128
    n_heads: int = 4
    d_ff: int = 256
    n_layers: int = 2
    max_seq_len: int = 64
    dropout: float = 0.0


class CausalSelfAttention(nn.Module):
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        assert cfg.d_model % cfg.n_heads == 0
        self.n_heads = cfg.n_heads
        self.head_dim = cfg.d_model // cfg.n_heads
        self.qkv = nn.Linear(cfg.d_model, 3 * cfg.d_model, bias=False)
        self.proj = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.scale = 1.0 / math.sqrt(self.head_dim)

    def forward(self, x):
        B, T, C = x.shape
        qkv = self.qkv(x)  # B, T, 3C
        q, k, v = qkv.split(C, dim=-1)
        q = q.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) * self.scale
        mask = torch.triu(torch.ones(T, T, device=x.device, dtype=torch.bool), diagonal=1)
        att = att.masked_fill(mask, float("-inf"))
        att = F.softmax(att, dim=-1)
        y = att @ v
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(y)


class MLP(nn.Module):
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.fc1 = nn.Linear(cfg.d_model, cfg.d_ff)
        self.fc2 = nn.Linear(cfg.d_ff, cfg.d_model)

    def forward(self, x):
        return self.fc2(F.gelu(self.fc1(x)))


class Block(nn.Module):
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.d_model)
        self.attn = CausalSelfAttention(cfg)
        self.ln2 = nn.LayerNorm(cfg.d_model)
        self.mlp = MLP(cfg)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x


class TinyGPT(nn.Module):
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.cfg = cfg
        self.tok = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.pos = nn.Embedding(cfg.max_seq_len, cfg.d_model)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layers)])
        self.ln_f = nn.LayerNorm(cfg.d_model)
        self.head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        # weight tying
        self.head.weight = self.tok.weight

    def forward(self, idx, targets=None):
        B, T = idx.shape
        pos = torch.arange(T, device=idx.device)
        x = self.tok(idx) + self.pos(pos)[None, :, :]
        for blk in self.blocks:
            x = blk(x)
        x = self.ln_f(x)
        logits = self.head(x)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1), ignore_index=-100)
        return logits, loss


# ----------------------------------------------------------------------------
# LoRA
# ----------------------------------------------------------------------------
class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, r: int = 4, alpha: float = 8.0):
        super().__init__()
        self.base = base
        for p in self.base.parameters():
            p.requires_grad = False
        in_f = base.in_features
        out_f = base.out_features
        self.r = r
        self.alpha = alpha
        self.scaling = alpha / r
        self.A = nn.Parameter(torch.zeros(r, in_f))
        self.B = nn.Parameter(torch.zeros(out_f, r))
        nn.init.kaiming_uniform_(self.A, a=math.sqrt(5))
        # B stays zero -> initial LoRA contribution is 0

    def forward(self, x):
        return self.base(x) + (x @ self.A.t() @ self.B.t()) * self.scaling


def inject_lora(model: TinyGPT, r: int = 4, alpha: float = 8.0) -> List[LoRALinear]:
    """Inject LoRA into the qkv projection of every attention layer."""
    adapters = []
    for i, blk in enumerate(model.blocks):
        original_qkv = blk.attn.qkv
        # Wrap the whole qkv projection as one LoRA target (treat as a single Linear)
        lora = LoRALinear(original_qkv, r=r, alpha=alpha)
        blk.attn.qkv = lora
        adapters.append(lora)
    return adapters


# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
def build_dataset() -> List[dict]:
    """Generate a tiny instruction-following dataset for an 'upper' skill.

    Format: instruction -> response, where response is the uppercased input.
    This is exact-match testable.
    """
    rng = random.Random(SEED)
    words = ["cat", "dog", "hello", "world", "fish", "moon", "star", "code",
             "data", "train", "model", "loss", "grid", "byte", "file", "test",
             "node", "edge", "wave", "leaf", "rain", "snow", "fire", "lake",
             "rock", "ship", "kite", "drum", "tree", "book"]
    rows = []
    for w in words:
        instr = f"UPPER: {w}"
        resp = w.upper()
        rows.append({"instruction": instr, "response": resp})
    # Add a few noise examples so the model must read the instruction
    for w in ["x", "y", "abc", "word"]:
        rows.append({"instruction": f"UPPER: {w}", "response": w.upper()})
    rng.shuffle(rows)
    return rows


def write_jsonl(path: Path, rows: List[dict]) -> None:
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def load_jsonl(path: Path) -> List[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def format_example(tok: CharTokenizer, row: dict, max_len: int) -> Tuple[List[int], List[int]]:
    """Tokenize instruction + response, return (input_ids, labels with -100 mask on instruction)."""
    instr = row["instruction"]
    resp = row["response"]
    # Format: <bos> {instr} | {resp} <eos>
    instr_ids = [tok.bos_id] + tok.encode(instr) + tok.encode("|")
    resp_ids = tok.encode(resp) + [tok.eos_id]
    input_ids = instr_ids + resp_ids
    labels = [-100] * len(instr_ids) + resp_ids[:]
    # Truncate
    if len(input_ids) > max_len:
        input_ids = input_ids[:max_len]
        labels = labels[:max_len]
    # Pad
    pad = max_len - len(input_ids)
    input_ids = input_ids + [tok.pad_id] * pad
    labels = labels + [-100] * pad
    return input_ids, labels


def collate(batch_ids, batch_labels):
    return torch.tensor(batch_ids, dtype=torch.long), torch.tensor(batch_labels, dtype=torch.long)


# ----------------------------------------------------------------------------
# Train
# ----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=2e-3)
    parser.add_argument("--lora-r", type=int, default=8)
    parser.add_argument("--lora-alpha", type=float, default=16.0)
    parser.add_argument("--limit", type=int, default=0, help="limit dataset size (smoke test)")
    parser.add_argument("--out", type=str, default=str(ADAPTER_DIR))
    parser.add_argument("--mlflow", action="store_true", default=True)
    args = parser.parse_args()

    t0 = time.time()
    device = torch.device("cpu")
    torch.manual_seed(SEED)

    # --- Data ---
    rows = build_dataset()
    if args.limit > 0:
        rows = rows[: args.limit]
    write_jsonl(DATA_DIR / "instruct.jsonl", rows)
    print(f"[tune] dataset: {len(rows)} examples -> {DATA_DIR / 'instruct.jsonl'}")

    tok = CharTokenizer()
    max_len = 48
    cfg = ModelConfig(vocab_size=len(tok), max_seq_len=max_len)

    examples = [format_example(tok, r, max_len) for r in rows]
    input_ids = torch.stack([torch.tensor(e[0]) for e in examples])
    labels = torch.stack([torch.tensor(e[1]) for e in examples])

    # --- Base model ---
    base = TinyGPT(cfg).to(device)
    base.eval()
    for p in base.parameters():
        p.requires_grad = False

    # Save base model so regress.py can load it
    torch.save({"state_dict": base.state_dict(), "cfg": cfg.__dict__}, MODEL_DIR / "tiny_gpt.pt")
    print(f"[tune] base model saved -> {MODEL_DIR / 'tiny_gpt.pt'}")

    # --- Inject LoRA ---
    adapters = inject_lora(base, r=args.lora_r, alpha=args.lora_alpha)
    trainable = [p for p in base.parameters() if p.requires_grad]
    n_trainable = sum(p.numel() for p in trainable)
    n_total = sum(p.numel() for p in base.parameters())
    print(f"[tune] trainable params: {n_trainable} / {n_total} ({100*n_trainable/n_total:.2f}%)")

    opt = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.0)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)

    # --- Train loop ---
    n = len(rows)
    mlflow_active = args.mlflow
    if mlflow_active:
        mlflow.start_run(run_name=f"lora-r{args.lora_r}")
        mlflow.log_params({
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "n_examples": n,
            "n_trainable_params": n_trainable,
            "base_total_params": n_total,
            "max_seq_len": max_len,
            "seed": SEED,
        })

    step = 0
    for epoch in range(args.epochs):
        perm = torch.randperm(n)
        epoch_loss = 0.0
        nb = 0
        for i in range(0, n, args.batch_size):
            idx = perm[i : i + args.batch_size]
            xb = input_ids[idx]
            yb = labels[idx]
            base.train()
            opt.zero_grad()
            _, loss = base(xb, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable, 1.0)
            opt.step()
            epoch_loss += loss.item()
            nb += 1
            if mlflow_active:
                mlflow.log_metric("train_loss_step", loss.item(), step=step)
            step += 1
        scheduler.step()
        avg = epoch_loss / max(nb, 1)
        if mlflow_active:
            mlflow.log_metric("train_loss_epoch", avg, step=epoch)
        if epoch % 5 == 0 or epoch == args.epochs - 1:
            print(f