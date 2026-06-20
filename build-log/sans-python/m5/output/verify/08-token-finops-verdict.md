# VERIFY verdict — M5 L08 · Token FinOps & Cost Optimization

**Verifier:** Sonnet VERIFY subagent · **Date:** 2026-06-19
**Draft:** `build-stages/m5/output/author/08-token-finops.md` (edited in place)
**Verdict:** **PASS** (markers resolved, claims sourced, batch discount confirmed, M4 cross-ref accurate)

---

## Claim ledger

| # | Claim | Authority | Result |
|---|-------|-----------|--------|
| 1 | Traditional cloud FinOps breaks on LLM spend: old-world cost = resource-uptime + tag-follows-VM; LLM cost = token-transactions, invoice arrives untagged; cost drivers (prompt length, context window, output length, tool-call count) are engineering decisions | aefs Ph17 L27 | **CONFIRMED** — L27: "costs are token-transactions not resource-uptime, tags don't auto-propagate to line items, and engineering decisions (prompt design, context window, output length) are financial decisions." |
| 2 | Instrument attribution at the call site on day one; stamp `user_id`, `task_id`+route, `tenant_id`; retroactive tagging always misses | aefs Ph17 L27 | **CONFIRMED** — L27: three attribution dimensions instrumented at call-site on day one (`user_id`, `task_id`+route, `tenant_id`); "retroactive tagging always misses." |
| 3 | Track token layers: prompt / tool-call / memory-context / response; one bucket hides the problem | aefs Ph17 L27 | **CONFIRMED** — L27: four token layers (prompt 40–60%, tool 20–40%, memory 10–30%, response 10–30%); "one bucket hides spend." Draft wisely omits the exact percentage bands — safe. |
| 4 | Unit metric: cost per resolved query / per artifact, not $/M tokens | aefs Ph17 L27 | **CONFIRMED** — L27 verbatim: "Unit metric is cost per resolved query / per artifact, not $/M tokens." |
| 5 | Azure: Cost Management groups spend by tag via tag inheritance + cost-allocation rules; Microsoft Foundry auto-stamps every project with a `project` tag; filter cost-analysis by project for showback/chargeback | MS Learn (connector) | **CONFIRMED** — `cost-management-billing/costs/cost-allocation-introduction`, `.../allocate-costs`, `.../enable-tag-inheritance`, `foundry/concepts/manage-costs`. Tag inheritance applies sub/RG tags to child usage records; allocation rules split shared costs; "Every Foundry project is automatically tagged with a `project` tag... filter the cost analysis view by the `project` tag." NOTE: Foundry project-level attribution is currently **Preview** — draft states it as established; acceptable at lesson altitude (non-blocking). |
| 6 | Provider prompt caching reuses attention state for stable prefix; cached reads a fraction of fresh-input price; mark system prompt + tool schemas cacheable | aefs Ph17 L14 | **CONFIRMED** — L14: Anthropic `cache_control` 10× cheaper reads ($0.30 vs $3.00/M); OpenAI auto-caches ≥1024 tokens ~90% discount. Draft keeps it qualitative ("a fraction") — safe. |
| 7 | Semantic caching skips the model: hash request, return stored answer for near-identical at zero tokens; hit rates single digits (open chat) → far higher (FAQ); traps = dynamic prefix content + parallel cold misses; stable part first = the cache key | aefs Ph17 L14 + L06 | **CONFIRMED** — L14: app-level semantic cache (Redis/GPTCache, cosine ≥0.95), hit rates 10% (open chat) → 70% (FAQ); two pitfalls = parallelization (N writes, 0 reads) + dynamic content in prefix → 0% hits. L06: prompt template IS a cache key (one deployment 7%→74% by moving dynamic text out of prefix). |
| 8 | Tiered routing: broker sends easy/high-volume work (classification, extraction, rubric score) to small model, escalates hard to frontier; meaningful cost reduction at equal quality; risk = cheap-model drift; gate on online quality signal, not offline eval alone | aefs Ph17 L16 | **CONFIRMED** — L16: dynamic broker / model cascading, 20–60% cost reduction at iso-quality; cheap-model drift ("route pushes 40% to weaker model, quality drops 3–5%, nobody notices for a quarter"); gate by online quality metrics not just offline eval. Draft keeps "meaningful cost reduction" qualitative rather than citing 20–60% — safe. |
| 9 | Batch tier ~half price, turnaround in hours; "if it isn't interactive, it belongs on batch"; triage into interactive / semi-interactive / batch; stack batch + caching → overnight pipeline drops toward a tenth of sync-uncached | aefs Ph17 L15 + WebSearch (OpenAI/Anthropic) | **CONFIRMED** — see batch-discount verdict below. aefs L15: 50% discount + ~24h (usually 2–6h) turnaround; three-lane triage; stack batch + caching → ~10% of sync-uncached ($2,000→$180/night). |
| 10 | Azure OpenAI quota: TPM per deployment + proportional RPM; exceed → 429 with `retry-after-ms`; watch `x-ratelimit-remaining-tokens` to throttle before the wall; three-cap pattern (per-tenant rate limit a few × peak, daily spend cap above, kill switch on spend z-score) | MS Learn (connector) + aefs L27 | **CONFIRMED** — `foundry/openai/how-to/quota`: TPM sets TPM+RPM limits, 429 on exceed, `retry-after-ms` header, `x-ratelimit-remaining-tokens` header to proactively throttle. aefs L27 enforcement ladder: rate limit (2–3× peak, 429+Retry-After) → daily spend cap (1.5–3× ceiling) → kill switch on spend z-score > 4. Matches the draft's three caps exactly. |

## Batch-discount verdict (CRITICAL)

**CONFIRMED ~50%.** OpenAI Batch API: flat 50% discount on input+output across every model, 24-hour guaranteed completion (most batches 1–6h). Anthropic Message Batches: 50% discount on input+output across all Claude models, up to 100k requests/batch, results within 24h (real-world minutes-to-hours). "Every major provider offers an async batch tier at roughly half price with a turnaround measured in hours" is accurate. The "drops toward a tenth" stacking claim is supported (aefs L15: ~10%; one secondary source cites ~5% with cached corpus) — "toward a tenth" is a safe, conservative characterization. No softening needed; marker removed.

## Markers resolved (3 / 3)

- L36 `[MS-Learn: Foundry cost attribution + Cost Management allocation]` → removed (claim #5 confirmed)
- L46 `[verify: batch-API discount ~50% / turnaround]` → removed (batch verdict above)
- L48 `[MS-Learn: Azure OpenAI quota TPM / 429 / retry-after / headers]` → removed (claim #10 confirmed)

Simulated rate card in code (`RATES = {"big": {"in": 3.00, "out": 15.00}, "small": {"in": 0.25, "out": 1.25}}`) is explicitly labeled "Simulated... shift — verify" in the comment — illustrative, not a live-pricing claim; verified-by-read per PLAN's code-gate note. The "$/1M tokens" framing is correct.

## Compliance-specifics check

**PASS.** Full grep (`20\d\d|€|%|Article|§|CFR|deadline|fine`) returns no matches — this lesson carries no compliance dates, fine thresholds, or statutory citations. Nothing to soften.

## M4 cross-ref (CRITICAL)

**ACCURATE.** Draft positions FinOps as the platform-scale read of Module 4's per-task budget governor — referenced, not rebuilt:
- L05: "Module 4 already gave you the governor: a per-task budget that caps one agent's spend, trips a kill switch on breach, and routes cheap steps to a cheap model. That defends one wallet. This lesson is the other altitude — the *platform* bill."
- L52: "You don't rebuild the governor here; you sum it."
- L60 (Core concepts): "FinOps is Module 4's budget governor read at platform scale... sum the governor, don't rebuild it."
- Exercise brief: "Reuse the Module 4 `TaskBudget` as the per-task cap underneath; do not rebuild it."

Matches PLAN's locked safety/ops thread ("M4 budgets/kill-switch → M5 FinOps/quotas/gateways") and the throughline rule. The three-cap quota escalation (per-tenant rate limit → daily spend cap → kill switch) is the platform-scale generalization of aefs L27's per-task enforcement ladder — consistent, not contradictory. Cross-ref is correct.

## STYLE pass

One H1; seam lead grabs ("The first time finance asks why the AI bill tripled... you will discover whether you can answer"); one `## Core concepts` (4 props as claims); handoff div present and well-scoped; FinOps / TPM / RPM expanded on first use; second person / present tense / active voice held. Ending (L54: "The platform engineer who can answer 'why did the bill triple' in one query is the one who gets to decide what to do about it") closes the loop with the lead as a consequence — NOT the banned literal "An AI Platform Engineer who…" opener, and it earns its shape. Non-blocking note: it leans on a "platform engineer who…" cadence; acceptable here as a single instance tied to the hook.

## Defects fixed

None beyond marker removal. Prose accurate and well-hedged as drafted.

## FLAGGED

None blocking. (Minor/non-blocking: Foundry project-level cost attribution is a Preview feature; draft states it as settled — fine at lesson altitude.)
