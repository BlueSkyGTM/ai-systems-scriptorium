# Skill Specification: `skill-instruct`

> Module 7 — Instruction-Tuned LLM with Behavioral Regression Suite
> Artifact: `module7-instruct/outputs/skill-instruct.md`
> Skill version: `1.0.0`
> Base: synthetic 2-layer GPT-like Transformer (CPU, stdlib + torch only)
> Adapter: `outputs/adapter/lora.pt`

---

## 1. Skill Identity

| Field | Value |
|---|---|
| Skill name | `skill-instruct` |
| Skill type | generative instruction-following |
| Task family | single-turn prompt → short deterministic answer |
| Output contract | string-prefix match on expected continuation |
| Modality | text-only |
| Language | English |
| Tuning method | LoRA (rank=8, alpha=16) on attention projections |

This is **not** a general chatbot. It is a *behaviorally pinned* skill: a small, auditable
set of prompt/response pairs the model must reproduce deterministically after LoRA tuning,
without losing any behavior the base model already had.

---

## 2. Intended Behavior

Given a prompt of the form

```
INSTRUCTION: <verb phrase>
RESPONSE:
```

the tuned model must emit the canonical response string as a *prefix* of its continuation.
The base model does **not** do this; that delta is the skill.

### 2.1 Canonical behaviors (the 20 core skills)

Each row is one JSONL training example (`chat` format) and one regression test.

| # | Instruction | Canonical response (prefix) |
|---|---|---|
| 1 | greet | hello there |
| 2 | say goodbye | goodbye friend |
| 3 | confirm | yes |
| 4 | deny | no |
| 5 | thank | thank you |
| 6 | name color | blue |
| 7 | name shape | circle |
| 8 | name number | forty two |
| 9 | name animal | cat |
| 10 | name fruit | apple |
| 11 | start | begin |
| 12 | stop | end |
| 13 | agree | okay |
| 14 | disagree | nope |
| 15 | apologize | sorry |
| 16 | praise | well done |
| 17 | warn | be careful |
| 18 | encourage | keep going |
| 19 | relax | calm down |
| 20 | count | one two three |

### 2.2 Format contract

```
INSTRUCTION: greet
RESPONSE: hello there
```

- Prompt terminator: `RESPONSE: `
- Test asserts: `model_output.startswith("hello there")`
- Decoding: greedy (argmax), temperature = 0, max_new_tokens = 8.

---

## 3. Anti-Regression Contract

The adapter is only acceptable if it does **not** break behaviors the base model
already performs. The regression suite (`regress.py`) enforces a strict monotonicity
rule on `N >= 5` base-preserved cases:

```
For each test case i in 1..N:
    score_base[i]   in {0, 1}
    score_tuned[i]  in {0, 1}
    require: score_tuned[i] >= score_base[i]
```

Overall gate: `min_i (score_tuned[i] - score_base[i]) >= 0`.

A tuned model that gains the skill but *also* breaks a base behavior is **BLOCK**,
not PASS.

### 3.1 Base-preserved cases (`N = 5`)

| Case | Prompt | Keyword that must appear |
|---|---|---|
| B1 | `The capital of France is` | `Paris` |
| B2 | `Once upon a` | `time` |
| B3 | `Two plus two equals` | `four` |
| B4 | `The sky is` | `blue` |
| B5 | `Roses are red, violets are` | `blue` |

These are *keyword* matches (lowercased substring), which the base model satisfies
trivially on a small GPT-like checkpoint and which the adapter must not erode.

---

## 4. Data Format

Training file: `outputs/train.jsonl` (one JSON object per line, 20–50 lines).

```json
{"prompt": "INSTRUCTION: greet\nRESPONSE: ", "completion": "hello there"}
{"prompt": "INSTRUCTION: confirm\nRESPONSE: ", "completion": "yes"}
```

- 20 canonical examples (Sec 2.1).
- Optional 10–30 augmentation examples drawn by templating the same verb/instruction
  with minor lexical variation. No semantic novelty — the goal is *stability*, not
  coverage.

Tokenization: character-level BPE-free char tokenizer implemented inline in
`tune.py` (vocab = 128 ASCII, deterministic).

---

## 5. Training Recipe

| Hyperparameter | Value |
|---|---|
| Optimizer | AdamW |
| Learning rate | `5e-3` (LoRA-only) |
| Batch size | 4 |
| Epochs | 8 |
| Max steps | 40 (10-sample smoke fixture: 20) |
| LoRA rank `r` | 8 |
| LoRA alpha `α` | 16 |
| LoRA dropout | 0.0 |
| LoRA targets | `q_proj`, `v_proj` of both layers |
| Base frozen? | yes — only adapter grads flow |
| Sequence length | 64 chars |
| Seed | `42` (`torch.manual_seed`, `random.seed`) |
| Wall-clock target | < 90 s on CPU (full), < 45 s (smoke) |

Loss: cross-entropy on completion tokens only (prompt tokens masked).

---

## 6. Evaluation Protocol

### 6.1 Skill pass (the new behavior)

```python
skill_pass = all(
    tuned.generate(p, greedy=True).startswith(expected)
    for p, expected in CANONICAL_20
)
```

### 6.2 Regression gate (the old behavior)

```python
regression_ok = all(
    keyword.lower() in tuned.generate(p, greedy=True).lower()
    and keyword.lower() in base.generate(p, greedy=True).lower()
    for p, keyword in BASE_PRESERVED_5
)
# stronger monotonic form (used by regress.py):
regression_ok = all(s_tuned >= s_base for s_tuned, s_base in paired_scores)
```

### 6.3 Ship decision

| `skill_pass` | `regression_ok` | Result |
|---|---|---|
| True  | True  | **PASS** (exit 0) |
| True  | False | **BLOCK** (exit 1) |
| False | True  | **BLOCK** (exit 1) |
| False | False | **BLOCK** (exit 1) |

All metrics and the ship decision are logged to MLflow
(`sqlite:///outputs/mlruns.db`, run name `skill-instruct-regress`).

---

## 7. Negative Control

`smoke.py` includes a negative case: an adapter with random weights of the same
shape (`torch.randn_like` on each LoRA tensor). This adapter **must** fail the
regression monotonicity check (because it destroys base behaviors). The smoke test
asserts that this failure is *detected* — proving the gate is not vacuous.

```python
# negative case in smoke.py
bad_adapter = {k: torch.randn_like(v) for k, v in good_adapter.items()}
assert run_regression(bad_adapter)["ship"] == "BLOCK"
```

---

## 8. Limitations & Non-Goals

- **No semantic generalization claims.** Pass = exact-prefix on known prompts.
  Out-of-distribution prompts are out of scope and untested.
- **No human alignment.** The skill is a deterministic lookup, not a value system.
- **No multi-turn dialogue.** Prompts are single-turn.
- **No GPU requirement.** Everything runs on CPU; if a GPU is present it is unused.
- **Tiny base, tiny data.** The artifact is a *teaching artifact*: the regression
  pattern is the lesson, not the absolute quality of the responses.

---

## 9. Reproducibility

- Seed: `42` (`torch.manual_seed(42)`, `random.seed(42)`, `numpy` not used).
- Deterministic decoding: `torch.use_deterministic_algorithms(True)` where supported.
- Adapter fingerprint: SHA-256 of `torch.save(state_dict, buffer)`, logged to MLflow
  as `adapter_sha256`.
- Re-running `tune.py` with the same seed and data MUST reproduce the adapter
  bit-for-bit on the same CPU + torch version.

---

## 10. File Map

```
module7-instruct/
├── tune.py
├── regress.py
├── smoke.py
├── tests/
│   └── test_regression.py
├── README.md
└── outputs/
    ├── adapter/
    │   └── lora.pt
    ├── train.jsonl
    ├── mlruns.db                  # MLflow offline backend
    ├── regress.log                # last regression run
    └── skill-instruct.md          # <-- this file
```

---

## 11. Changelog

| Version | Date | Notes |
|---|---|---|
| 1.0.0 | M7 ship | Initial skill. 20 canonical + 5 base-preserved cases. Monotonic regression gate. Negative control in smoke. |