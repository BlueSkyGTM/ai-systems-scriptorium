# Local Metal — Module 5 Source Provenance

Cited-resource record for Module 5 ("The Routing Layer"). Per the authoring directive, every external
resource a lesson cites is captured here as tracked ore: the URL, what it grounds, the source type,
and the retrieval date. The shipped book cites the URLs; this manifest preserves the underlying fact
against link rot. Retrieved 2026-06-21 by the M5 source-fetch tier (two Haiku fetchers) and the
authoring fleet (Sonnet workers + conductor), grounded via vendor docs (LiteLLM, Ollama, Anthropic),
engineering write-ups, and the shipped M3/M4 artifacts.

## Routing signals + hybrid pattern (Lessons 1-2: the-routing-decision, signals-and-thresholds)

| Fact grounded | Source | Type |
|---|---|---|
| LLM router/gateway directs requests by cost/latency/quality/complexity | https://docs.litellm.ai/docs/routing | LiteLLM (vendor docs) |
| Core routing signals: cost, latency, context window, task complexity | https://www.truefoundry.com/blog/what-is-llm-router | engineering blog |
| Hybrid local+cloud: route simple/small/private local, escalate complex/large/high-stakes | https://www.mindstudio.ai/blog/hybrid-ai-architecture-local-models-cloud-frontier | engineering blog |
| Local inference amortized hardware (near-zero per token) vs cloud per-token metered | https://pooya.blog/blog/local-ai-ollama-benchmarks-cost-2026/ | engineering blog (benchmark) |
| Semantic routing (classify request to pick a model) as an advanced pattern | https://llm-semantic-router.readthedocs.io/en/latest/overview/semantic-router-overview/ | project docs (vLLM semantic router) |

Note: the fetch tier flagged that **privacy/sensitivity is not a well-sourced standard routing
signal** (sources emphasize cost/latency/context/complexity). The lessons frame sensitivity honestly
as a local-first rule the reader chooses to enforce on their own rig, not as an industry-standard
lever.

## Context windows + pricing (the escalation rationale)

| Fact grounded | Source | Type |
|---|---|---|
| Ollama `num_ctx` default 2048 (Modelfile) / 4096 (runtime); `OLLAMA_CONTEXT_LENGTH` override | https://docs.ollama.com/faq , https://github.com/ollama/ollama/blob/main/docs/modelfile.mdx | Ollama (authoritative) |
| KV cache grows with context and competes with weights for VRAM; ~4K-8K practical context for a 14B Q4 on 16GB | https://lyceum.technology/magazine/kv-cache-memory-calculation-llm/ | community technical guide |
| Claude context window 200K, up to 1M tokens (Opus 4.8 / Sonnet 4.6) | https://platform.claude.com/docs/en/docs/build-with-claude/context-windows | Anthropic (authoritative) |
| Claude pricing is per-token metered (e.g. Opus 4.8 $5/MTok in, $25/MTok out) | https://platform.claude.com/docs/en/docs/about-claude/pricing | Anthropic (authoritative) |

## Building + recording the router (Lessons 3-4: build-the-router, record-the-policy)

| Fact grounded | Source | Type |
|---|---|---|
| Ollama OpenAI-compatible call (the local arm `route.py` wraps via `ollama_client.py`) | https://docs.ollama.com/api/openai-compatibility | Ollama (authoritative) |
| Router/gateway design reference | https://docs.litellm.ai/docs/routing | LiteLLM (vendor docs) |

## Reference policy (the thresholds the lessons quote)

The reference `ROUTING.md` sets the local context limit at 8192 tokens (grounded in the 4K-8K
practical context for a 14B Q4 on the 16GB RTX 4060 Ti) and a 2000 ms interactive latency budget
(grounded in the M4 baseline: ~30 tok/s on-card, sub-250 ms TTFT). The local arm is
`qwen2.5-coder:14b`; the cloud arm is "claude (frontier)" with a 200K-1M context. Thresholds are
written with the words "over"/"under" rather than the symbols, because the throughline validator
`check_routing.py` treats angle brackets as placeholder tokens (the same placeholder family as the
M3/M4 validators). The reader tunes the numbers to their own card; the validator gates structure and
completeness, not the specific thresholds.
