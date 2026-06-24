# Skill Specification: `skill-instruct`

> Module 7: Instruction-Tuned LLM with Behavioral Regression Suite
> Base: 2-layer from-scratch Transformer (CPU, stdlib + torch only)
> Adapter: `outputs/adapter/adapter.pt`

---

## 1. Skill Identity

| Field | Value |
|---|---|
| Skill name | `skill-instruct` |
| Skill type | generative instruction-following |
| Task family | single-turn prompt to short deterministic answer |
| Output contract | exact-match on the decoded response |
| Tuning method | LoRA (rank=8, alpha=16) on attention projections |

This is **not** a general chatbot. It is a *behaviorally pinned* skill: a small, auditable
set of prompt/response pairs the model must reproduce deterministically after LoRA tuning,
without losing any behavior the base model already had.

---

## 2. Intended Behavior

Prompts take the fixed form `<bos> VERB NAME <sep>`, and the tuned model must greedily
decode the exact response `RESPONSE NAME <eos>`:

```
<bos> greet alice <sep>   ->   hello alice
```

The base model handles `thank` and `bye`; it has never seen `greet`. The adapter adds
`greet -> hello`. That delta is the skill.

### 2.1 The three skills

| Verb | Response | Learned by |
|---|---|---|
| `thank` | `thanks` | base pretraining |
| `bye` | `goodbye` | base pretraining |
| `greet` | `hello` | LoRA adapter (the new skill) |

---

## 3. Anti-Regression Contract

The adapter is acceptable only if it does **not** break behaviors the base already
performs. The regression suite (`regress.py`) scores each case 0 or 1 (exact match) for
both models and requires:

```
For each case i:  score_tuned[i] >= score_base[i]   (no regression)
And:              sum(score_tuned) > sum(score_base) (at least one improvement)
```

A tuned model that gains `greet` but breaks `thank` or `bye` is **BLOCK**, not PASS.

The suite mixes the new skill with the two old skills, on held-out names the model never
trained on:

| Case | Prompt | Expected |
|---|---|---|
| greet alice | `<bos> greet alice <sep>` | `hello alice` |
| greet ivan  | `<bos> greet ivan <sep>`  | `hello ivan` |
| thank bob   | `<bos> thank bob <sep>`   | `thanks bob` |
| bye carol   | `<bos> bye carol <sep>`   | `goodbye carol` |

---

## 4. Training Recipe

| Hyperparameter | Value |
|---|---|
| Optimizer | Adam |
| LoRA rank `r` | 8 |
| LoRA alpha | 16 |
| LoRA targets | query + value projections of both blocks |
| Base frozen? | yes, only adapter grads flow |
| Seed | `42` (`torch.manual_seed`, `random.seed`) |
| Wall-clock | a few seconds on CPU |

Loss: cross-entropy on the response span only (the prompt tokens are masked out).

---

## 5. Negative Control

`smoke.py` swaps the trained adapter for random weights of the same shape
(`torch.randn_like` on each LoRA tensor) and asserts the gate BLOCKS it. The gate is not
vacuous: it can fail, so a green run is evidence.

---

## 6. Limitations & Non-Goals

- **No semantic generalization.** Pass = exact match on the pinned prompts.
- **No multi-turn dialogue.** Prompts are single-turn.
- **Tiny base, tiny data.** This is a teaching artifact; the regression pattern is the
  lesson, not the quality of the responses.

---

## 7. Reproducibility

Re-running `tune.py` with the same seed and torch version reproduces the adapter. Seeds
are pinned in every entry point; no network calls, no HuggingFace, CPU only.
