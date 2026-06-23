# Adapters Catalog — Weights and Measures M4 Reference Ingredient

Distilled 2026-06-21 (Haiku fetch tier) from HF `peft` docs + PyTorch AMP/`compile` docs + `aipe` Ch 13.
The schema M4 authors fill. (MS-Learn PEFT page 404'd at fetch time; M4 grounds on HF + PyTorch.)

**Grounding rule:** the reader learns LoRA's mechanism in pure torch (a from-scratch `LoRALinear`), then
sees `peft` as the production library that does it for them. The `peft` / QLoRA / `bitsandbytes`
snippets are REFERENCE (shown, clearly labeled, not required to run the book); the runnable, verified
spine is from-scratch torch on CPU.

## Doc anchors

| Topic | URL | Facts |
|---|---|---|
| PEFT LoRA | https://huggingface.co/docs/peft/en/quicktour | `LoraConfig(r, lora_alpha, target_modules=["q_proj","v_proj"], lora_dropout, task_type)`; `get_peft_model(model, cfg)`; `model.print_trainable_parameters()`; `merge_and_unload()`. dW = B·A, A is d×r, B is r×d, r << d; B init to ZERO (delta starts at 0), A Kaiming; only A,B train; effective scale = `lora_alpha/r`; adapter file ~6-7 MB for a 350M model. |
| QLoRA / 4-bit | https://huggingface.co/docs/peft/en/task_guides/lora_based_methods/qlora | `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)`; quantize the FROZEN base to 4-bit, train adapters in bf16; big VRAM cut, minimal accuracy loss. |
| PyTorch AMP | https://docs.pytorch.org/tutorials/recipes/recipes/amp_recipe.html | `with torch.autocast(device_type, dtype=torch.float16/bfloat16):` forward; `scaler = torch.amp.GradScaler(...)`; `scaler.scale(loss).backward(); scaler.step(opt); scaler.update()`. bf16 has wider exponent (often no scaler); fp16 needs the scaler. 1.5-3x speedup. |
| torch.compile | https://docs.pytorch.org/docs/stable | `model = torch.compile(model)`; graph capture + kernel fusion; modes default / reduce-overhead / max-autotune; best on recent CUDA, CPU experimental. |

## L1 — `why-adapters`
- Full fine-tune updates every weight: gradients + Adam's 2 optimizer-state copies + the activation
  cache => roughly 4x the model in memory, one full-size checkpoint per task, and catastrophic
  forgetting risk. Levers: gradient checkpointing (recompute activations on backward, ~O(sqrt) peak),
  gradient accumulation (smaller per-step activation footprint), optimizer-state offload.
- Adapters flip the default: freeze the base, train a small delta; one ~MB adapter per task, swap not retrain.

## L2 — `lora-from-the-inside`
- LoRA replaces W -> W + (alpha/r)·B·A, with A in R^{d×r}, B in R^{r×d}, r << d (typ. 8-16). Only A,B
  train; the base W is frozen. B starts at ZERO so the model begins identical to the base.
- Where: the attention projections (q,k,v,o; MHA holds 4·d^2 params); `target_modules=["q_proj","v_proj"]`
  is the common minimal set. `all-linear` adapts every linear.
- Read the freeze off the param counts: `print_trainable_parameters()` => trainable% ~0.19% (HF example).

## L3 — `quantization-and-mixed-precision`
- QLoRA: quantize the frozen base to 4-bit (`nf4`), keep adapters in bf16. Memory per element: fp32 4B,
  fp16/bf16 2B, int4 0.5B. The base shrinks 8x; the trainable adapter stays full precision.
- AMP: run the forward under `autocast`; cast logits back to fp32 before the loss; fp16 needs a
  `GradScaler` (underflow), bf16 usually does not. `torch.compile` fuses kernels for more throughput.

## L4 — `the-fine-tune-build` (capstone)
- Wrap the model with LoRA (freeze base + insert adapters), train ONLY the adapter with the M2 `fit()`
  loop + early stopping, save the adapter, optionally `merge_and_unload()` to fold it back into the base
  for inference, and confirm trainable << total. `peft` is the production path; the from-scratch
  `LoRALinear` is what makes it legible.

## Throughline (the spine-engineer builds + freezes; pure torch, CPU, NO peft/model download)

- `exercises/spine/trainer.py` gains:
  - `class LoRALinear(nn.Module)`: holds a FROZEN base `nn.Linear` (base.weight/bias `requires_grad=False`)
    + `lora_A = nn.Linear(in, r, bias=False)` + `lora_B = nn.Linear(r, out, bias=False)` with `lora_B`
    weight init to ZERO; `self.scaling = alpha / r`; `forward(x) = base(x) + scaling * lora_B(lora_A(x))`.
    A `merge()` returning a plain `nn.Linear` with `weight = base.weight + scaling * (B.weight @ A.weight)`.
  - `wrap_with_lora(model, r=8, alpha=16)`: replace `nn.Linear` submodules with `LoRALinear`, freeze bases,
    return the model; a helper to count trainable vs total.
  - `__main__` LoRA demo: wrap `TinyClassifier`, print trainable<<total (base frozen), `fit()` the adapter,
    show the still-descending loss; show `merge()` produces an equivalent plain Linear.
- `exercises/spine/check_loop.py` gains `--module 4`: on top of M1/M2 checks, require a freeze signal
  (`requires_grad = False` / `requires_grad=False`) AND a low-rank adapter signal (`lora`/`LoRA`/`adapter`
  with a rank `r`). Lower `--module` values stay byte-identical; `--selftest` covers module 4.
