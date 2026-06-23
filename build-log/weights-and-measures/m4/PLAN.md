# Module 4 — Adapters and the Fine-Tune Build — Build Plan

Status: **PLAN LOCKED 2026-06-21** (self-cleared; W&M M3–M8 straight-through). Fourth stage (M1–M3 shipped).

## The stage in one line

M3 produced a clean dataset; M4 trains on it without retraining the whole model. This is the
adapter-based fine-tune build: why full fine-tuning is the wrong default, how LoRA freezes the base and
trains a low-rank delta, what QLoRA and mixed precision buy you, and the end-to-end build that wraps a
model, trains only the adapter with the M2 `fit()` loop, and proves the freeze worked.

## THE locked decision: teach LoRA's mechanism in pure torch, reference `peft` as production

The M1 grounding rule holds: the reader learns the real mechanism, not a black box. So M4's runnable
spine is a **from-scratch `LoRALinear`** (frozen `nn.Linear` base + trainable low-rank `A`,`B`; forward
= base(x) + (alpha/r)·B(A(x))), trained by the existing `fit()` loop. The Hugging Face `peft` library
(`LoraConfig`, `get_peft_model`, `target_modules`, `merge_and_unload`) is shown as the production tool
the from-scratch version demystifies, but it is NOT required to run the book (keeps CPU-verifiable, no
heavy model download). The M1 trainable-vs-total param check now *demonstrates* the freeze: trainable
<< total.

## Locked decisions

1. Stage = module; `build-log/weights-and-measures/m4/`. Consumes M3's clean dataset; the adapter +
   the trained-checkpoint discipline feed M5 (eval gate) and M6 (the tuned-classifier artifact).
2. STYLE + STANDARDS; overview + 4 lessons + 4 exercises.
3. Grounded: `aipe` Ch 13 (AMP / `autocast` / `GradScaler`, `torch.compile`, memory) + HF `peft` docs
   (LoRA config + merge) + PyTorch AMP docs + MS-Learn Azure ML LoRA/PEFT if present. From-scratch LoRA
   is Sonnet-written + RUN; `peft`/QLoRA snippets are shown as reference, clearly labeled.
4. CPU-verifiable: `LoRALinear` + the wrap + a fit() run on the tiny model runs on CPU in < 30s.

## M4 split (overview + 4 lessons + 4 exercises)

| # | Lesson (slug) | The move |
|---|---------------|----------|
| 0 | `00-overview` | Adapters as the default fine-tune; the four lessons; what feeds forward to M5/M6. |
| 1 | `why-adapters` | Full fine-tune vs adapters: the memory/storage/forgetting costs of updating every weight; the adapter idea (freeze the base, train a small delta); one adapter per task, swap not retrain. |
| 2 | `lora-from-the-inside` | LoRA mechanics: the low-rank decomposition `dW = B·A` (rank r), the `alpha/r` scaling, which layers get adapters; build `LoRALinear` in pure torch; read the trainable-vs-total ratio to confirm the freeze. |
| 3 | `quantization-and-mixed-precision` | QLoRA (quantize the frozen base to 4-bit, train adapters in higher precision) as a memory lever; AMP (`autocast` + `GradScaler`) and `torch.compile` for single-GPU efficiency; the memory math. QLoRA/bitsandbytes shown as reference. |
| 4 | `the-fine-tune-build` | The payoff: wrap the model with LoRA, train ONLY the adapter via the M2 `fit()` loop + early stopping, save/merge the adapter, verify trainable << total. `peft` as the production path. The module deliverable. |

## Throughline (extend the spine)

- `exercises/spine/trainer.py` gains `LoRALinear(nn.Module)` (frozen base + low-rank A/B + scaling) and
  `wrap_with_lora(model, r, alpha)` that swaps a model's `nn.Linear` for `LoRALinear` and freezes the
  base; a `__main__` LoRA demo: wrap `TinyClassifier`, show trainable<<total, `fit()` the adapter, print
  the (still descending) trajectory. M1/M2/M3 code byte-identical.
- `exercises/spine/check_loop.py` gains `--module 4`: on top of M1/M2 checks, require an adapter/freeze
  signal (a frozen base, `requires_grad=False`, plus a trainable low-rank adapter present). No flag /
  lower `--module` values stay byte-identical. `--selftest` covers it.

## Fleet
Round 1: 1 Haiku (aipe Ch 13 AMP/compile/memory + aefs Phase 07) + 1 Haiku (HF peft LoRA + PyTorch AMP +
MS-Learn). Round 2: 1 Sonnet spine-engineer builds + RUNS `LoRALinear` + `wrap_with_lora` + `check_loop
--module 4` (torch-CPU, from-scratch, no peft/model download required) + FREEZE-VERIFIED; 5 Sonnet
authors. Opus designs the schema + reviews, does NOT hand-code. VERIFY -> BUILD (selftests + mdbook) ->
SHIP (atomic commit in a window).
