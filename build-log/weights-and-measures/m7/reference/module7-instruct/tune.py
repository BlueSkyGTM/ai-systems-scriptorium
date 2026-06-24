"""tune.py — Module 7: Instruction-Tuning a Tiny LLM with LoRA.

Builds a small from-scratch Transformer language model, pretrains it on a couple of
"skills", then LoRA-fine-tunes it to add a new skill without retraining the base.
Pure PyTorch (no HuggingFace). Runs on CPU in well under 90 seconds.

The point is the mechanics, not the scale:
  - The base model is a real (if tiny) next-token Transformer. Pretraining teaches it
    two response skills: `thank -> thanks` and `bye -> goodbye`.
  - LoRA adds low-rank trainable matrices to the attention projections and freezes the
    base. Instruction-tuning teaches a THIRD skill, `greet -> hello`, by training only
    the adapter (a few hundred parameters), with a little replay of the old skills so
    the new skill does not clobber them.
  - The adapter saved to outputs/adapter/ is a small delta, not a retrained model.

regress.py loads the base alone and the base+adapter, and checks the adapter added the
new behaviour without regressing the old ones.

Sequence format (fixed length 7):
    <bos> VERB NAME <sep> RESPONSE NAME <eos>
e.g. "<bos> greet alice <sep> hello alice <eos>"
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

SEED = 42
random.seed(SEED)
torch.manual_seed(SEED)

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
ADAPTER_DIR = OUTPUTS / "adapter"
BASE_PATH = OUTPUTS / "base.pt"
ADAPTER_PATH = ADAPTER_DIR / "adapter.pt"
DATA_PATH = OUTPUTS / "instruct.jsonl"

# ---------------------------------------------------------------------------
# Vocabulary and the synthetic skill data
# ---------------------------------------------------------------------------
SPECIALS = ["<pad>", "<bos>", "<sep>", "<eos>"]
VERBS = ["greet", "thank", "bye"]
RESPONSES = ["hello", "thanks", "goodbye"]
NAMES = ["alice", "bob", "carol", "dave", "erin",
         "frank", "grace", "heidi", "ivan", "judy"]

VERB_TO_RESPONSE = {"greet": "hello", "thank": "thanks", "bye": "goodbye"}

VOCAB: List[str] = SPECIALS + VERBS + RESPONSES + NAMES
STOI: Dict[str, int] = {tok: i for i, tok in enumerate(VOCAB)}
ITOS: Dict[int, str] = {i: tok for tok, i in STOI.items()}
PAD, BOS, SEP, EOS = (STOI[t] for t in ["<pad>", "<bos>", "<sep>", "<eos>"])
SEQ_LEN = 7  # <bos> verb name <sep> resp name <eos>


def encode_example(verb: str, name: str) -> List[int]:
    resp = VERB_TO_RESPONSE[verb]
    return [BOS, STOI[verb], STOI[name], SEP, STOI[resp], STOI[name], EOS]


def make_pairs(verbs: List[str], names: List[str]) -> List[Tuple[str, str]]:
    return [(v, n) for v in verbs for n in names]


def to_tensor(pairs: List[Tuple[str, str]]) -> torch.Tensor:
    return torch.tensor([encode_example(v, n) for v, n in pairs], dtype=torch.long)


# ---------------------------------------------------------------------------
# A tiny Transformer LM, with LoRA-ready linear layers
# ---------------------------------------------------------------------------
class LoRALinear(nn.Module):
    """A Linear whose base weight is frozen; a low-rank A,B delta is trainable.

    y = base(x) + (alpha / r) * (x A^T) B^T
    B is zero-initialised so the adapter is a no-op until trained.
    """

    def __init__(self, in_features: int, out_features: int, r: int = 8, alpha: int = 16) -> None:
        super().__init__()
        self.base = nn.Linear(in_features, out_features)
        self.r = r
        self.scale = alpha / r
        self.A = nn.Parameter(torch.zeros(r, in_features))
        self.B = nn.Parameter(torch.zeros(out_features, r))
        nn.init.normal_(self.A, std=0.02)
        self.lora_enabled = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.base(x)
        if self.lora_enabled:
            out = out + self.scale * (x @ self.A.t()) @ self.B.t()
        return out

    def enable_lora(self) -> None:
        self.lora_enabled = True

    def freeze_base(self) -> None:
        self.base.weight.requires_grad_(False)
        self.base.bias.requires_grad_(False)


class Block(nn.Module):
    def __init__(self, d_model: int, n_head: int, d_ff: int) -> None:
        super().__init__()
        self.n_head = n_head
        self.d_head = d_model // n_head
        self.q = LoRALinear(d_model, d_model)
        self.k = nn.Linear(d_model, d_model)
        self.v = LoRALinear(d_model, d_model)
        self.proj = nn.Linear(d_model, d_model)
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff), nn.ReLU(), nn.Linear(d_ff, d_model)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, t, d = x.shape
        h = self.ln1(x)
        q = self.q(h).view(b, t, self.n_head, self.d_head).transpose(1, 2)
        k = self.k(h).view(b, t, self.n_head, self.d_head).transpose(1, 2)
        v = self.v(h).view(b, t, self.n_head, self.d_head).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) / (self.d_head ** 0.5)
        mask = torch.tril(torch.ones(t, t, device=x.device)).bool()
        att = att.masked_fill(~mask, float("-inf"))
        att = F.softmax(att, dim=-1)
        out = (att @ v).transpose(1, 2).contiguous().view(b, t, d)
        x = x + self.proj(out)
        x = x + self.ff(self.ln2(x))
        return x


class TinyLM(nn.Module):
    def __init__(self, vocab_size: int, d_model: int = 64, n_head: int = 4,
                 d_ff: int = 128, n_layer: int = 2, seq_len: int = SEQ_LEN) -> None:
        super().__init__()
        self.tok = nn.Embedding(vocab_size, d_model)
        self.pos = nn.Embedding(seq_len, d_model)
        self.blocks = nn.ModuleList([Block(d_model, n_head, d_ff) for _ in range(n_layer)])
        self.ln = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)
        self.seq_len = seq_len

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        b, t = idx.shape
        pos = torch.arange(t, device=idx.device).unsqueeze(0)
        x = self.tok(idx) + self.pos(pos)
        for blk in self.blocks:
            x = blk(x)
        return self.head(self.ln(x))

    # -- LoRA control --------------------------------------------------------
    def lora_layers(self) -> List[LoRALinear]:
        return [m for m in self.modules() if isinstance(m, LoRALinear)]

    def enable_lora(self) -> None:
        for m in self.lora_layers():
            m.enable_lora()

    def freeze_for_lora(self) -> None:
        """Freeze everything except the LoRA A,B parameters."""
        for p in self.parameters():
            p.requires_grad_(False)
        for m in self.lora_layers():
            m.A.requires_grad_(True)
            m.B.requires_grad_(True)
            m.enable_lora()

    def adapter_state(self) -> Dict[str, torch.Tensor]:
        state = {}
        for i, m in enumerate(self.lora_layers()):
            state[f"lora.{i}.A"] = m.A.detach().clone()
            state[f"lora.{i}.B"] = m.B.detach().clone()
        return state

    def load_adapter(self, state: Dict[str, torch.Tensor]) -> None:
        for i, m in enumerate(self.lora_layers()):
            m.A.data.copy_(state[f"lora.{i}.A"])
            m.B.data.copy_(state[f"lora.{i}.B"])
            m.enable_lora()


# ---------------------------------------------------------------------------
# Training helpers
# ---------------------------------------------------------------------------
def lm_loss(model: TinyLM, batch: torch.Tensor) -> torch.Tensor:
    """Next-token loss over the response span (positions 4..6 predicted from 3..5)."""
    logits = model(batch[:, :-1])
    targets = batch[:, 1:]
    loss = F.cross_entropy(
        logits.reshape(-1, logits.size(-1)), targets.reshape(-1), reduction="none"
    ).view(targets.shape)
    weight = torch.zeros_like(targets, dtype=torch.float)
    weight[:, 3:] = 1.0  # response span
    return (loss * weight).sum() / weight.sum()


def train(model: TinyLM, data: torch.Tensor, epochs: int, lr: float,
          params=None) -> float:
    params = params if params is not None else [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.Adam(params, lr=lr)
    model.train()
    final = 0.0
    for _ in range(epochs):
        opt.zero_grad()
        loss = lm_loss(model, data)
        loss.backward()
        opt.step()
        final = float(loss.item())
    return final


def pretrain_base(model: TinyLM, epochs: int = 300, lr: float = 0.01) -> float:
    """Teach the base two skills: thank->thanks and bye->goodbye (NOT greet)."""
    pairs = make_pairs(["thank", "bye"], NAMES)
    return train(model, to_tensor(pairs), epochs, lr)


def lora_finetune(model: TinyLM, epochs: int = 300, lr: float = 0.01) -> float:
    """Teach the new skill greet->hello via LoRA, with replay of the old skills so
    the adapter does not regress them."""
    model.freeze_for_lora()
    new_skill = make_pairs(["greet"], NAMES)
    replay = make_pairs(["thank", "bye"], NAMES[:4])  # a little replay
    data = to_tensor(new_skill + replay)
    trainable = [p for p in model.parameters() if p.requires_grad]
    return train(model, data, epochs, lr, params=trainable)


# ---------------------------------------------------------------------------
# Generation (greedy decode of the response span)
# ---------------------------------------------------------------------------
def generate_response(model: TinyLM, verb: str, name: str) -> List[str]:
    """Greedy-decode the response tokens for a '<bos> verb name <sep>' prompt."""
    model.eval()
    seq = [BOS, STOI[verb], STOI[name], SEP]
    with torch.no_grad():
        for _ in range(3):  # resp, name, eos
            idx = torch.tensor([seq], dtype=torch.long)
            nxt = int(model(idx)[0, -1].argmax().item())
            seq.append(nxt)
            if nxt == EOS:
                break
    return [ITOS[i] for i in seq[4:] if i != EOS]


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
def write_dataset() -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", encoding="utf-8") as f:
        for v, n in make_pairs(["greet"], NAMES):
            row = {
                "messages": [
                    {"role": "user", "content": f"{v} {n}"},
                    {"role": "assistant", "content": f"{VERB_TO_RESPONSE[v]} {n}"},
                ]
            }
            f.write(json.dumps(row) + "\n")


def build(base_epochs: int = 300, lora_epochs: int = 300) -> dict:
    """Full pipeline: pretrain base, save it, LoRA-tune, save the adapter."""
    torch.manual_seed(SEED)
    random.seed(SEED)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)

    model = TinyLM(len(VOCAB))
    base_loss = pretrain_base(model, epochs=base_epochs)
    torch.save({"state_dict": model.state_dict(), "vocab": VOCAB}, BASE_PATH)

    lora_loss = lora_finetune(model, epochs=lora_epochs)
    n_adapter = sum(p.numel() for p in model.parameters() if p.requires_grad)
    n_total = sum(p.numel() for p in model.parameters())
    torch.save(model.adapter_state(), ADAPTER_PATH)
    write_dataset()

    return {
        "base_loss": base_loss,
        "lora_loss": lora_loss,
        "adapter_params": n_adapter,
        "total_params": n_total,
        "base_path": str(BASE_PATH),
        "adapter_path": str(ADAPTER_PATH),
    }


def load_base() -> TinyLM:
    blob = torch.load(BASE_PATH, weights_only=False)
    model = TinyLM(len(blob["vocab"]))
    model.load_state_dict(blob["state_dict"])
    model.eval()
    return model


def load_tuned() -> TinyLM:
    model = load_base()
    model.load_adapter(torch.load(ADAPTER_PATH, weights_only=False))
    model.eval()
    return model


def main() -> None:
    parser = argparse.ArgumentParser(description="Instruction-tune a tiny LM with LoRA.")
    parser.add_argument("--base-epochs", type=int, default=300)
    parser.add_argument("--lora-epochs", type=int, default=300)
    args = parser.parse_args()
    summary = build(args.base_epochs, args.lora_epochs)
    print(
        f"[tune] base_loss={summary['base_loss']:.4f} lora_loss={summary['lora_loss']:.4f} "
        f"adapter_params={summary['adapter_params']} / {summary['total_params']} total"
    )


if __name__ == "__main__":
    main()
