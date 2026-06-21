# Module 7 — Perf and Tuning — Build Plan

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN`).** Self-locked under Ray's "finish the job"
directive (decisions stated for override). Seventh and FINAL authoring stage for Local Metal (M1-M6
shipped 2026-06-21). M7 is the aipe-depth capstone: it profiles the running stack, applies the tuning
levers, and proves the improvement against the Module 4 baseline.

## The stage in one line

M4 measured the baseline; M7 beats it. The rig is serving, routed, and wired into Claude Code, but at
stock settings. This module profiles where the time goes, applies the levers that matter on a single
consumer GPU (KV-cache quantization, flash attention, parallelism, context sizing), measures throughput
under concurrent load, and records a before/after that proves the tuning was worth it. Seam: a
production engineer does not stop at "it works," they measure, tune, and prove the gain; M7 is where
Local Metal makes that loop explicit and leaves the reader with a before/after artifact.

## Settled decisions

1. **Stage = module.** Same shape as M1-M6; writes `build-log/local-metal/m7/output/{...}`.
2. **Held to the three contracts**; every worker brief carries them + the shipped M1-M6 lessons as the
   locked voice exemplar.
3. **The compounding spine extends one last time.** M4's `bench.py` measured one stream; M7 adds
   `loadbench.py` (concurrent load -> aggregate throughput + tail latency). The 7th portfolio document
   is `TUNING.md` (baseline vs tuned, with the levers applied), gated by `check_tuning.py`. The
   before-number comes from M4's `LATENCY.md`.
4. **aipe depth, honestly scoped.** The levers are the ones that actually move the needle on a single
   RTX 4060 Ti: `OLLAMA_FLASH_ATTENTION`, `OLLAMA_KV_CACHE_TYPE` (q8_0/q4_0, mainly a VRAM/context
   win), `OLLAMA_NUM_PARALLEL` (aggregate throughput under load), and `num_ctx` sizing. Framed with
   their real tradeoffs, not as universal speedups.

## Locked decisions (all accepted; stated for override)

1. **Throughline artifacts: `loadbench.py` + `TUNING.md` + `check_tuning.py`.** `loadbench.py` fires N
   concurrent generations (stdlib threads) at `/api/generate` and reports aggregate tokens/sec and the
   slowest request; `--selftest` validates the aggregation math offline. `TUNING.md` records the
   baseline (from M4) and the tuned result plus the levers applied; `check_tuning.py` gates it and
   asserts the tuned aggregate throughput is at least the baseline (a proven, non-regressing change).
2. **Machine-checkable done-when without hardware:** `loadbench.py --selftest` (offline aggregation
   math) + `check_tuning.py` (completeness + tuned >= baseline). Both offline.
3. **The headline before/after is throughput under load via `OLLAMA_NUM_PARALLEL`.** It is the cleanest
   honest improvement on one GPU (one stream vs several concurrent streams raises aggregate tok/s up to
   a saturation point). KV-cache quant is framed as the VRAM/context win it actually is; flash
   attention as a modest single-stream gain. No inflated single-stream speedups.
4. **Tuning is measured, never assumed.** Every lever in `TUNING.md` is paired with the number it
   moved; the lesson's rule is "change one thing, measure, keep it only if the number improved."

## Proposed M7 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind |
|---|---------------|----------|------|
| 0 | `00-overview` | The stock rig is the starting line, not the finish; profile, tune, and prove the gain. | concept |
| 1 | `where-the-time-goes` | Profiling: read GPU utilization and memory bandwidth under load (`nvidia-smi dmon`); generation is bandwidth-bound, so that is what you watch. | concept |
| 2 | `the-tuning-levers` | The levers that matter on one GPU: flash attention, KV-cache quantization, parallelism, context sizing, each with its real tradeoff. | concept/build |
| 3 | `throughput-under-load` | Build `loadbench.py`: fire concurrent generations, measure aggregate tok/s and tail latency; the metric stock single-stream benchmarks miss. | build |
| 4 | `record-the-tuning` | Record `TUNING.md` (baseline vs tuned + levers) and gate it with `check_tuning.py` asserting tuned >= baseline; the module's and the book's done-when. | build |

## Sources (three-source rule)

1. **Ingredient:** the SPEC + the shipped M4 artifacts (`bench.py`, `LATENCY.md`) + the `aipe` ore
   (`vault/ai-performance-engineering/`) for profiling, KV-cache, throughput depth.
2. **External grounding:** Ollama performance env vars (`OLLAMA_FLASH_ATTENTION`,
   `OLLAMA_KV_CACHE_TYPE`, `OLLAMA_NUM_PARALLEL`, `num_ctx`), `nvidia-smi dmon` GPU profiling, and any
   real RTX 4060 Ti tuning numbers; cite real URLs, capture to
   `vault/local-metal/m7-sources/PROVENANCE.md`. USE THE TOOLS (Haiku fetch tier + local aipe survey).
3. **Editorial seam framing** in every lead.

## The fleet plan

Conductor-direct, tiered: 3 Haiku source-fetchers (Ollama perf env vars; nvidia-smi profiling + real
4060 Ti tuning numbers; local aipe ore survey) feeding 4 Sonnet lesson authors. Conductor writes the
overview, owns + tests `loadbench.py` + `check_tuning.py` (byte-identical to ship), reviews, reconciles,
runs the gates.

On ship: VERIFY (voice + grounding), BUILD/TEST (`mdbook build` + `loadbench.py --selftest` +
`check_tuning.py`), then `GATE-APPROVE-SHIP` (cleared under "finish the job"), commit + push. **This
ship completes the seven-module book**; after it, the remaining step is the cataloguing move of the
book toward `library/completed/` (no gate) once Ray confirms the book is content-complete.
