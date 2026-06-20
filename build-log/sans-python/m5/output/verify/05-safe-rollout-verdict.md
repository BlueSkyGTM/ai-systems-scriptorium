# VERIFY verdict — M5 L05 · Safe Rollout: Shadow, Canary, A/B + AI Gateways

**Verdict: PASS (edited in place).** All four markers resolved. The `llm-token-limit` policy name and the APIM 429/Retry-After behavior verified verbatim against MS Learn. No invented facts.

## Claim ledger

| Claim | Status | Authority |
|---|---|---|
| Model rollout has no failing unit test; failure modes diffuse + delayed | CONFIRMED | aefs ch20 ("no unit tests, diffuse failure modes, delayed signals"); asdg Ch11.02 |
| Run-to-run output non-determinism from FP non-associativity + batch-size variance; "stable" = within variance | CONFIRMED | aefs ch20 ("up to 15% accuracy variation … GPU FP non-associativity + batch-size variance"); external (Thinking Machines "Defeating Nondeterminism": kernels not batch-invariant, reduction order shifts with batch size) |
| Shadow mode = mirror prod traffic, discard response, diff; catches operational regressions (cost/latency/length) NOT quality | CONFIRMED | aefs ch20 verbatim |
| Canary = real-user traffic sliver 1%→10%→25%→50%→…, gated on latency percentiles, cost/req, error+refusal rate, output-length, user feedback | CONFIRMED | aefs ch20 (the five gating metrics, the percentage ladder) |
| A/B answers product question (do users prefer A or B); randomized user-level assignment; evals ask "can the model do the job," A/B asks "do users care" | CONFIRMED | aefs ch21 verbatim ("evals answer can the model do the job; A/B tests answer do users care") |
| Eval thread: M2 LLM-as-judge inner loop → live canary quality gate (outer loop) | CONFIRMED | PLAN threads + asdg Ch14 online eval; accurate cross-ref |
| AI gateway = one stable API in front of many backends; routing weights in config; flip in seconds | CONFIRMED | aefs ch19 ("gateway … OpenAI-compatible API … provider routing/fallback/retries/rate limits/secret refs/cost attribution") |
| Gateway consolidates routing, 429 fallback, retries, per-consumer rate limits, vault secret refs, cost attribution | CONFIRMED | aefs ch19 (the seven features) |
| **Azure APIM: built-in backend pools, load balancing, circuit breaking across multiple Azure OpenAI deployments** | CONFIRMED | MS Learn "AI gateway in API Management" + "Backends in API Management" (pools up to 30; round-robin/weighted/priority/session-aware; circuit breaker honors Retry-After) |
| **APIM smart load balancer reroutes on 429, reads Retry-After, by priority not blind round-robin** | CONFIRMED | MS Learn openai-aca-lb / openai-apim-lb ("aware of Retry-After and 429 … priority groups … fallback to lower priority"); circuit breaker "applies values from the Retry-After header" |
| **`llm-token-limit` policy enforces per-consumer TPM and token quota** | CONFIRMED — exact policy name correct | MS Learn "Limit large language model API token usage": `<llm-token-limit counter-key tokens-per-minute token-quota token-quota-period>`; 429 on rate, 403 on quota |
| Rollback: policy in flags, model in registry pinned to digest; revert in seconds | CONFIRMED | aefs ch20 verbatim ("policy lives in flags, model lives in registry with pinned digests") |

## Markers resolved (4/4)
1. `[verify: run-to-run variance from GPU FP non-associativity + batch-size variance]` → removed; rewritten with the precise mechanism (non-associative FP + non-batch-invariant kernels, reduction order shifts with batch size, batch shifts with load). Confirmed.
2. `[MS-Learn: APIM backend pools / load balancing / circuit breaking]` → removed; confirmed verbatim.
3. `[MS-Learn: APIM smart load balancing reroutes on 429 by priority]` → removed; confirmed, and tightened to name the `Retry-After` header explicitly (which the docs emphasize).
4. `[MS-Learn: llm-token-limit per-consumer TPM + quota]` → removed; confirmed, exact policy name correct.

## TTFT/TPOT number decision
N/A for this lesson — no reference perf figures. (p99 appears only as an exercise gating metric, no claimed value.)

## STYLE pass
- H1 present; lead grabs ("most dangerous deploy you will ever do"); one `## Core concepts` block (4 props); handoff div well-formed.
- Ending lands as a reframe ("the property that lets you ship at all") — not a template, no banned opener.
- Acronyms: A/B, AI gateway, LLM, CI all course-level / self-explanatory; none on the TTFT/TPOT/SLO/OTel/SRE expand-list appear needing expansion. (`429` is a status code, fine.)
- Unity: second person, present tense, one blunt voice. Clean.

## FLAGGED for editor (non-blocking)
- None of substance. The lesson is the strongest-sourced of the three — its Azure claims map one-to-one onto current MS Learn pages.
