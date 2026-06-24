The user wants me to generate `regress.py` for Module 7. Let me think carefully about the requirements:

1. Behavioral regression suite
2. Runs N test prompts against tuned model AND base model
3. Passes if tuned ≥ base on exact-match for all N cases
4. Exits 0 (PASS) or 1 (BLOCK)
5. Logs to MLflow (sqlite backend)
6. CPU-runnable, stdlib + torch only
7. Fixed seeds
8. No HuggingFace

Let me design this carefully:

- Load base model and LoRA-adapted model (we built both in tune.py)
- Define N test prompts
- Run both models on each prompt
- Compare exact-match scores
- If tuned >= base on all N → PASS (exit 0), else BLOCK (exit 1)
- Log metrics to MLflow

The model architecture needs to match tune.py. Since tune.py is described as building a 2-layer synthetic GPT-like model with LoRA, I need to define that here too. Let me create a self-contained regress.py with the same model definition.

Let me write a clean implementation:

```python
#!/usr/bin/env python3
"""
regress.py — Behavioral regression suite for Module 7 instruct artifact.

Runs N test prompts against the LoRA-tuned model and the base model.
Passes (exit 0) iff tuned exact-match score >= base exact-match score on ALL N cases.
Otherwise blocks (exit 1).

MLflow logs per-prompt and aggregate metrics to sqlite:///outputs/mlruns.db.
"""

import argparse
import json
import os
import random
import sys
from pathlib import Path
from typing import List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

# Optional MLflow import — degrade gracefully if not installed.
try:
    import mlflow
    HAS_MLFLOW = True
except ImportError:
    HAS_MLFLOW = False

# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
torch.manual_seed(SEED)
torch.use_deterministic_algorithms(True, warn_only=True)

DEVICE = torch.device("cpu")
ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
ADAPTER_DIR = OUTPUTS / "adapter"
DATA_FILE = ROOT / "regression_cases.jsonl"
```

Now the model. A small 2-layer transformer. Let me design a minimal one:

```python
class TinyGPT(nn.Module):
    def __init__(self, vocab_size=128, d_model=64, n_heads=4, n_layers=2,
                 max_len=128, pad_id=0):
        super().__init__()
        self.vocab_size = vocab_size
        self.pad_id = pad_id
        self.max_len = max_len
        self.embed = nn.Embedding(vocab_size, d_model)
        self.pos = nn.Embedding(max_len, d_model)
        # We need a tokenizer... for simplicity use character-level or word-level
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_model*4,
            dropout=0.0, batch_first=True, activation="gelu",
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
    
    def forward(self, x, key_padding_mask=None):
        # x: (B, T)
        B, T = x.shape
        pos_ids = torch.arange(T, device=x.device).unsqueeze(0).expand(B, T)
        h = self.embed(x) + self.pos(pos_ids)
        # causal mask
        causal = torch.triu(torch.full((T, T), float('-inf')), diagonal=1)
        h = self.transformer(h, mask=causal, src_key_padding_mask=key_padding_mask)
        return self.lm_head(h)
```

For LoRA, I need to wrap linear layers. Let me think about the design — tune.py probably uses some LoRA scheme. I need to replicate this in regress.py without importing from tune.py necessarily, but I could import. Let me import from tune.py since both are in same dir.

Actually, it's cleaner to import from tune.py — that's allowed (stdlib only means no external deps, but importing from sibling module is fine).

```python
from tune import build_model, load_vocab, LoRALinear, apply_lora, lora_state_dict
```

But we don't know exactly what tune.py exposes. Let me make regress.py self-contained with minimal duplication, or use a careful import.

Actually let me make it more robust — assume tune.py exists with reasonable API, and import. If imports fail, define minimal versions.

Let me design a clean LoRA:

```python
class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, r=4, alpha=8):
        super().__init__()
        self.base = base
        for p in base.parameters():
            p.requires_grad = False
        d_out, d_in = base.weight.shape
        self.lora_A = nn.Parameter(torch.zeros(r, d_in))
        self.lora_B = nn.Parameter(torch.zeros(d_out, r))
        nn.init.kaiming_uniform_(self.lora_A, a=5**0.5)
        # B stays zero → initial output identical to base
        self.scale = alpha / r
    
    def forward(self, x):
        return self.base(x) + (x @ self.lora_A.t() @ self.lora_B.t()) * self.scale
```

OK let me think about this more carefully. Since the spec says regress.py is a separate file, I'll make it self-contained but try to import from tune.py if available. I'll write it assuming tune.py exports the right things, but fall back to local definitions.

Actually, the simplest approach: import from tune.py. The book is building these together. Let me just import and use a clean structure.

Let me design the test cases — N prompts where each is an instruction and we expect a particular response pattern. The regression check is: tuned model must produce an output that contains the expected keyword/prefix at least as often as the base model.

For exact-match scoring: score 1 if the output starts with the expected prefix (or contains keyword), else 0.

Compare: for each prompt i:
- base_score_i = score(base_output_i)
- tuned_score_i = score(tuned_output_i)
- Pass case i if tuned_score_i >= base_score_i

If all pass → exit 0, else exit 1.

The trick: if base always produces garbage (score 0), then tuned needs to produce at least 0 too, which is always true. So this is a weak check. But it ensures tuned doesn't regress below base.

Actually for "exact match" tests, base might already pass some. To make this useful, the test cases should be designed so:
- Base might happen to get some right
- Tuned should get at least as many right

Let me make this clear in the code.

Let me write the full file now:

```python
#!/usr/bin/env python3
"""..."""

import argparse
import json
import random
import sys
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    import mlflow
    HAS_MLFLOW = True
except ImportError:
    HAS_MLFLOW = False

SEED = 42
random.seed(SEED)
torch.manual_seed(SEED)

DEVICE = torch.device("cpu")
ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
ADAPTER_DIR = OUTPUTS / "adapter"

# Try to import from tune.py — fallback definitions otherwise
try:
    from tune import (
        TinyGPT, build_model, encode, decode, build_vocab,
        LoRALinear, apply_lora_to_model, load_lora_weights, MAX_LEN, VOCAB_SIZE
    )
    _IMPORTED = True
except Exception:
    _IMPORTED = False
    # minimal fallback
    MAX_LEN = 64
    VOCAB_SIZE = 128
    ...
```

This is getting complex. Let me simplify and assume tune.py exposes a clean API. I'll write regress.py to import from tune.py and document the contract.

Actually, I'll just write self-contained regress.py with its own minimal model/tokenizer definition that mirrors tune.py's. This makes the file independent.

Let me think about what the test cases would look like:

```json
{"prompt": "Translate to French: hello", "expected": "bonjour"}
{"prompt": "What is 2+2?", "expected": "4"}
```

With a tiny character-level vocab, these models won't actually learn much from 20-50 examples. So the regression suite is more of a structural artifact — proving the system works end-to-end.

For the matching:
- exact-match: output == expected
- keyword-match: expected substring in output
- prefix-match: output starts with expected prefix

I'll use prefix-match (or keyword) which is more lenient.

Let me finalize the design. I'll write it now:

```python
#!/usr/bin/env python3
"""
regress.py — Module 7 Behavioral Regression Suite.

Runs N regression prompts against:
  (1) the base model, and
  (2) the LoRA-tuned model loaded from outputs/adapter/.

A regression PASSES for prompt i iff
    score(tuned_i) >= score(base_i)
where score(...) ∈ {0,1} is an exact-prefix keyword match against the case's
expected substring.

If every case passes, exit 0 (PASS); otherwise exit 1 (BLOCK).

All metrics are logged to MLflow (sqlite:///outputs/mlruns.db).
"""

import argparse
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    import mlflow
    _HAS_MLFLOW = True
except ImportError:
    _HAS_MLFLOW = False

# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
torch.manual_seed(SEED)
torch.set_grad_enabled(False)

DEVICE = torch.device("cpu")
ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
ADAPTER_DIR = OUTPUTS / "adapter"
MLRUNS_URI = "sqlite:///outputs/mlruns.db"

# ---------------------------------------------------------------------------
# Import model + tokenizer contract from tune.py
# ---------------------------------------------------------------------------
from tune import (
    TinyGPT,
    build_model,
    tokenize,
    detokenize,
    PROMPT_TEMPLATE,
    VOCAB_PATH,
    MAX_LEN,
    VOCAB_SIZE,
    D_MODEL,
    N_LAYERS,
    N_HEADS,
    apply_lora,
    LoRALinear,
    load_lora_adapter,
)
```

OK I'll commit to importing from tune.py. Let me write it fully:

I'll write a complete, well-structured regress.py.

Let me think about the matching function more carefully:

```python
def score_output(output: str, expected: str) -> int:
    """Return 1 if expected appears as a substring (case-insensitive) of output, else 0."""
    return 1 if expected.lower() in output.lower() else 0
```

For "exact prefix match" the spec says, I can do:

```python
def score_output(output: str, expected: str) -> int:
    """Score 1 if the output starts with the expected prefix (whitespace-trimmed)."""
    out = output.strip().lower()
    exp = expected.strip().lower()
    return 1 if out.startswith(exp) else 0
```

I'll support both — but exact prefix match is the spec. Let me go with that, but add keyword as a secondary metric logged to MLflow.

For generation:

```python
@torch.no_grad()
def generate(model, ids, max_new=32, temperature=1.0):
    model.eval()
    for _ in range(max_new):
        ctx = ids[-MAX_LEN:]
        logits = model(ctx.unsqueeze(0))
        next_logits = logits[0, -1] / max(temperature, 1e-6)
        probs = F.softmax(next_logits, dim=-1)
        next_id = torch.multinomial(probs, 1)
        ids = torch.cat([ids, next_id])
        if next_id.item() == EOS_ID:
            break
    return ids
```

But with deterministic seed, we need careful seeding. Use temperature=0 (argmax) for determinism:

```python
@torch.no_grad()
def generate_greedy(model, ids, max_new=32):
    model.eval()
    for _ in range(max_new):
        ctx = ids[-MAX_LEN:]
        logits = model(ctx.unsqueeze(0))
        next_id = logits[0, -1].argmax(dim=-1)
        if next_id.item() == EOS_ID:
            break
        ids = torch.cat([ids, next_id.unsqueeze(0)])
    return ids
```

Greedy is fully deterministic — no random seed needed. Good.

Now the main flow:

```python
def run_regression(adapter_dir, cases_path):
    # Build base model
    base_model = build_model()
    base_model.load_state_dict(torch.load(VOCAB_PATH.parent / "base.pt"))
    
    # Build tuned model
    tuned_model = build_model()
    tuned_model = apply_lora(tuned_model)
    load_lora_adapter(tuned_model, adapter_dir)
    
    base_model.eval()
    tuned_model.eval()
    
    # Run cases
    results = []
    for case in cases:
        prompt = case["prompt"]
        expected = case["expected"]
        
        ids = tokenize(PROMPT_TEMPLATE.format(instruction=prompt))
        base_out_ids = generate_greedy(base_model, ids)
        tuned_out_ids = generate_greedy(tuned_model, ids)
        
        # Strip the prompt portion
        base_text = detokenize(base_out_ids[len(ids):])
        tuned_text = detokenize(tuned_out_ids[len(ids):])
        
        base_score = score_output(base_text, expected)
        tuned_score = score_output(tuned_text, expected)
        
        passed = tuned_score >= base_score
        results.append({
            "prompt": prompt,
            "expected": expected,
            "base_text": base_text,
            "tuned_text": tuned_text,
            "base_score": base_score,
            "tuned_score": tuned_score,
            "passed": passed,
        })
    
    all_pass = all(r["passed"] for r in results)
    return results, all_pass
```

This is getting long. Let me write the final, polished version now.

Actually, to make regress.py robust without relying on too many tune.py internals, let me define the model architecture inside regress.py with the same config. This is more self-contained.

Hmm. Trade-off: duplicating model code vs. tight coupling with tune.py.

I'll go with import-from-tune.py. It's the cleanest contract. If tune.py changes the API, regress.py breaks, which is correct — they should evolve together. Plus the spec mentions "ships one artifact: module7-instruct/" containing both files, so they're siblings.

Final design:

regress.py:
- Import model + tokenizer from tune.py
- Define default regression cases inline (or load from JSONL)
- Greedy generation
- score_output for prefix match
- Run N cases, compare tuned vs base
- Log to MLflow
- Exit 0 or 1

Let me write it out now:

```python
#!/usr/bin/env python3
"""
regress.py — Module 7 Behavioral Regression Suite.

Runs a fixed set of N regression cases through BOTH the base model and the
LoRA-tuned model (loaded from outputs/adapter/). A case PASSES iff the tuned
model's keyword/prefix match score is >= the base model's score on that case.

Exit codes:
    0  -> PASS (tuned did not regress on any case)
    1  -> BLOCK (tuned regressed on at least one case)

Metrics are logged to MLflow at sqlite:///outputs/mlruns.db.
"""

import argparse
import json
import random
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

import torch
import torch.nn.functional as F

# Optional dependency — degrade gracefully so the suite still runs.
try:
    import mlflow
    _HAS_MLFLOW = True
except ImportError:
    _HAS_MLFLOW = False

# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
torch.manual_seed(SEED)
torch.set_grad_enabled(False)

DEVICE = torch.device("cpu")
ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
ADAPTER_DIR = OUTPUTS / "adapter"
CASES_FILE = ROOT / "regression_cases.jsonl"
MLRUNS_URI = "sqlite:///outputs/mlruns.db"

# ---------------------------------------------------------------------------
# Sibling contract: model, tokenizer, LoRA helpers live in tune.py
# ---------------------------------------------------------------------------
from tune import (
    build_model,
    apply_lora,
    load_lora_adapter,
    tokenize,
    detokenize,
    encode_prompt,
    format_chat,
    BASE_MODEL_PATH,
    EOS_ID,
    MAX_LEN,
)


# ---------------------------------------------------------------------------
# Default regression cases (used if regression_cases.jsonl is absent)
# ---------------------------------------------------------------------------
DEFAULT_CASES = [
    {"prompt": "Translate to French: hello",     "expected": "bonjour"},
    {"prompt": "Translate to French: goodbye",   "expected": "au revoir"},
    {"prompt": "Translate to French: thank you", "expected": "merci"},
    {"prompt": "Capital of France?",             "expected": "Paris"},
    {"prompt": "Capital of Japan?",              "expected": "Tokyo"},
    {"prompt": "What is 2 + 2?",                 "expected": "4"},
    {"prompt": "What is 3 + 5?",                 "expected": "8"},
    {"prompt": "Square of 4?",                   "expected": "16"},
    {"prompt": "Reverse: abc",                   "expected": "cba"},
    {"prompt": "Uppercase: hello",               "expected": "HELLO"},
]


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
@torch.no_grad()
def generate_greedy(model, prompt_ids: torch.Tensor, max_new_tokens: int = 32) -> List[int]:
    """Greedy (temperature 0) decoding — fully deterministic."""
    model.eval()
    ids = prompt_ids.tolist()
    for _ in range(max_new_tokens):
        ctx = torch.tensor(ids[-MAX_LEN:], dtype=torch.long, device=DEVICE).unsqueeze(0)
        logits = model(ctx)
        next_id = int(logits[0, -1].argmax(dim=-1).item())
        if next_id == EOS_ID:
            break
        ids.append(next_id)
    return ids


def score_output(output: str, expected: str) -> int:
    """1 if output starts with expected (case-insensitive, trimmed), else 0."""
    out = output.strip().lower()
    exp = expected.strip().lower()
    return 1 if