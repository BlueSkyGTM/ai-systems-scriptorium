# Exercise 03 — The Optimization Levers: Quantization, Speculative Decoding, Disaggregation

## Goal

Add an optimization layer to `module5-serving/` that simulates all three levers — quantization, speculative decoding, and disaggregated prefill/decode — each with the regime where it turns net-negative, then run one workload through each and print the metric it wins and the metric it costs.

## Why

Every serving optimization is a trade, and each fails the same way: a win on the watched metric paid for by a regression on the unwatched one. Simulating the levers — including the regimes where they backfire — is how a Production AI Engineer learns to pull them in order of blast radius and stop the moment the SLO and the quality score both clear.

## Steps

1. **Quality score.** Give `MockEngine` a `quality` baseline (a single number standing in for an eval-set score). Levers will move TTFT/TPOT/throughput *and* this number, so wins and costs are both visible.

2. **Quantization lever.** Add a `quantization` setting (e.g. `fp16` baseline, `fp8`, `awq_int4`) that lowers per-token decode cost and KV-memory footprint but also lowers `quality` by a per-format amount. Model the two traps: a `calibration_domain` that, when it mismatches the workload domain, drops `quality` further; and a KV-cache footprint that does **not** shrink when only weights are quantized — so report weight memory and KV memory separately and show the cache dominating at batch.

3. **Speculative-decoding lever.** Add a `speculative` mode with a tunable `acceptance_rate`. Accepted drafts produce multiple tokens per target pass (lower TPOT); every rejected draft charges a second target pass. Implement the break-even so that below a threshold acceptance (around 0.55) the mode is net-negative — throughput drops below baseline. Track p99 per-token latency separately from the mean and show the tail worsening on rejection-heavy runs even as the mean improves.

4. **Disaggregation lever.** Add a `disaggregated` mode that splits prefill and decode onto separate simulated pools, each sized for its own bottleneck, and charges a KV-transfer tax (a function of prompt length) on the handoff. Show short prompts losing to the tax and long prompts at scale winning.

5. **Run the sweep.** Send one fixed workload through baseline and each lever. Print a table: TTFT, TPOT, throughput, quality, weight-MB, KV-MB per configuration. Then run each lever in its bad regime — quantization with a mismatched calibration domain, speculative decoding below the acceptance threshold, disaggregation on short prompts — and show the net-negative result.

## Done when

- The sweep prints a per-lever table showing each lever's win **and** its cost on the same workload (e.g. quantization: faster + smaller weights, lower quality and unchanged KV memory).
- Speculative decoding is faster above the acceptance threshold and provably net-negative below it, with p99 per-token latency reported alongside the mean.
- Disaggregation wins on a long-prompt/high-scale workload and loses to the transfer tax on short prompts — both shown.
- No GPU and no real model — every lever is a simulated adjustment to the latency/memory/quality model.

## Stretch

Add a `recommend(workload, slo, quality_floor)` that pulls levers in blast-radius order — quantization first, then speculative decoding, then disaggregation — stopping at the first configuration that meets the SLO without breaching the quality floor, and prints the reasoning. This is the decision discipline of the lesson, executable.
