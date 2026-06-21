# Module 4 — Unified Memory — Build Plan

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN`).** Self-locked under Ray's "finish the job"
directive (decisions stated below for override). Fourth authoring stage for Local Metal (M1-M3
shipped 2026-06-21). M4 confronts the models that do NOT fit on-card and the latency cost of
spilling them across GPU VRAM + system DDR5; it is where the `aipe` quantization ore enters in depth.

## The stage in one line

M3 kept the model 100% on-card and treated overflow as failure. M4 reframes overflow as a deliberate
choice: a 32B-70B model is smarter than a 14B but does not fit in 16GB, so Ollama splits it across the
GPU and the 64GB of DDR5, trading speed for capability. The rig's real memory budget is VRAM + RAM as
one pool; this module measures the cost of using the slow half so you can choose models on numbers,
not vibes. Seam: M3 proved the fast path; M4 measures the slow path and gives you the latency baseline
(tok/s, TTFT) every later tuning decision (M7) is measured against.

## Settled decisions (from the blueprint + the SPEC + aipe ore)

1. **Stage = module.** Same shape as M1-M3; writes `build-log/local-metal/m4/output/{...}`.
2. **Held to the three contracts**; every worker brief carries them + the shipped M1-M3 lessons as the
   locked voice exemplar.
3. **The portfolio repo grows a 4th document.** M1 `HARDWARE.md`, M2 `SETUP.md`, M3 `MODELS.md`, now
   M4 `LATENCY.md` (the measured baseline per model). The runnable code spine `ollama_client.py`
   (M3) still carries to M5/M6; M4 adds the standalone measurement tool `bench.py` (the family of
   standalone tools: `breakeven.py`, `partition_plan.py`, `stack_check.py`, now `bench.py`).
4. **aipe ore enters in depth here.** Quantization quality/size/speed tradeoffs (Q4 vs Q8 vs F16),
   why a tighter quant lets a bigger model fit, and the VRAM-vs-DDR5 bandwidth gap that makes offload
   slow. The deepest GPU-profiling / KV-cache / throughput-under-load material stays in M7.

## Locked decisions (all accepted; stated for override)

1. **Reference big model.** `qwen2.5-coder:32b` (Q4_K_M, ~20 GB; does not fit 16GB, so it splits
   across GPU+DDR5) as the "smarter but slower" contrast to M3's on-card 14B. Swap-ins named:
   `llama3.1:70b` (Q4, ~40 GB, heavier split) and staying on the 14B. Grounded against Ollama library.
2. **Throughline artifacts: `LATENCY.md` + `check_latency.py` + standalone `bench.py`.** `bench.py`
   measures tok/s (eval rate) and TTFT (time to first token) from Ollama's native `/api/generate`
   timing fields; ships a `--selftest` that computes both from a sample response offline (machine
   checkable pre-hardware). `LATENCY.md` records a row per model (model, quant, GPU/CPU split, TTFT,
   tok/s); `check_latency.py` gates completeness + positive-numeric metrics (the same validator family
   as `check_models.py`).
3. **Machine-checkable done-when without hardware:** `bench.py --selftest` (offline metric math) +
   `check_latency.py` completeness/positivity gate. Live mode hits `localhost:11434`.
4. **Quantization depth: deep enough to choose a model, not to retrain one.** Q4/Q8/F16
   size+quality+speed tradeoff and the fit-vs-quality decision; deep KV-cache/profiling stays in M7.
5. **"Unified memory" framing.** On this discrete-GPU rig it means treating VRAM + DDR5 as one pool
   Ollama splits a model across (layer offload), NOT Apple-style shared silicon; the lesson says so
   explicitly to avoid the miscue.

## Proposed M4 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind |
|---|---------------|----------|------|
| 0 | `00-overview` | Overflow is not always failure: when you want a model too big for 16GB, the rig splits it across VRAM + DDR5; measure the cost. | concept |
| 1 | `when-a-model-doesnt-fit` | What Ollama does when a model exceeds VRAM: offloads layers to system RAM; `ollama ps` shows the CPU/GPU split; DDR5 bandwidth is a fraction of VRAM bandwidth, so the split half is slow. | build |
| 2 | `quantization-tradeoffs` | aipe depth: Q4 vs Q8 vs F16 (size, quality, speed); a tighter quant lets a bigger model fit more on-card; how to choose the quant for a target card. | concept/build |
| 3 | `measure-latency` | Build `bench.py`: read `/api/generate` timing fields to compute tok/s and TTFT; compare a 14B on-card vs a 32B split. | build |
| 4 | `record-the-baseline` | Record `LATENCY.md` (per-model tok/s, TTFT, split) and validate with `check_latency.py`; the module's done-when and the baseline M7 tunes against. | build |

## Sources (three-source rule)

1. **Ingredient:** the SPEC (Ryzen 7 7700X, 64GB DDR5-6000, RTX 4060 Ti 16GB) + the `aipe` ore
   (`vault/ai-performance-engineering/`) for quantization depth and memory-bandwidth framing.
2. **External grounding:** Ollama docs (layer offload / `num_gpu`, `/api/generate` timing fields,
   model library sizes), llama.cpp / Hugging Face quantization references, DDR5-6000 vs GDDR6
   bandwidth figures; cite real URLs, capture to `vault/local-metal/m4-sources/PROVENANCE.md`. USE
   THE TOOLS (Haiku fetch tier + MS-Learn where it has coverage).
3. **Editorial seam framing** in every lead.

## The fleet plan

Conductor-direct, tiered (the M3 pattern that worked): 3 Haiku source-fetchers (Ollama offload/timing;
quant tradeoffs + bandwidth; big-model library sizes, incl. a local `aipe` vault survey) feeding 4
Sonnet lesson authors. Conductor writes the overview, owns + tests the code artifacts (`bench.py`,
`check_latency.py`) so what ships is byte-identical to what is tested, reviews every draft, reconciles
artifacts, and runs the gates before ship.

On ship: VERIFY (voice + grounding), BUILD/TEST (`mdbook build` + `bench.py --selftest` +
`check_latency.py`), then `GATE-APPROVE-SHIP` (cleared under "finish the job"), commit + push.
