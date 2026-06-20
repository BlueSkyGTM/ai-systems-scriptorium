# VERIFY verdict — M5 L06 · Observability & SRE-for-AI

**Verdict: PASS (edited in place).** All seven markers resolved. The OTel `gen_ai.*` attribute names verified against the authoritative OpenTelemetry semantic-conventions registry — every name used is real and current. No invented attributes.

## Claim ledger

| Claim | Status | Authority |
|---|---|---|
| Three pillars: logs / metrics / traces; AI adds quality, token economics, non-determinism as first-class signals | CONFIRMED | asdg Ch14.02 verbatim ("three pillars … treating output quality, non-determinism, and token economics as first-class metrics") |
| Distributed trace stitches one request (retrieval → rerank → prompt → model → tool) into parent/child spans | CONFIRMED | asdg Ch14.02 (RAG pipeline instrumentation, OTel tracing) |
| **OTel GenAI semantic conventions = agreed span/attribute names** | CONFIRMED | OTel semconv registry + MS Learn (Agent Framework / Semantic Kernel emit per OTel GenAI semconv) |
| **`gen_ai.usage.input_tokens`** | CONFIRMED — exact, current | OTel registry: "number of tokens used in the GenAI input (prompt)" |
| **`gen_ai.usage.output_tokens`** | CONFIRMED — exact, current | OTel registry: "number of tokens used in the GenAI response (completion)" |
| **`gen_ai.request.model`** (added in edit) | CONFIRMED — exact, current | OTel registry: "name of the GenAI model a request is being made to" |
| **`gen_ai.operation.name`** (added in edit) | CONFIRMED — exact, current | OTel registry: "name of the operation being performed" |
| **Azure Monitor agent observability is based on OTel GenAI semantic conventions** | CONFIRMED verbatim | MS Learn "Monitor AI agents with Application Insights": "Azure Monitor Agent Observability is based on OpenTelemetry Generative AI Semantics" |
| `configure_azure_monitor` + model-SDK instrumentation → spans to App Insights | CONFIRMED | MS Learn (azure-monitor-opentelemetry / Azure Monitor OpenTelemetry distro; `configure_azure_monitor` is the documented entry point) |
| **`OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` gates message content, off by default** | CONFIRMED | OTel openai-v2 instrumentation docs ("not captured by default … set OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT to true"); MS Learn Foundry troubleshooting shows the same var |
| Prometheus scrapes a metrics endpoint; Grafana renders panels | CONFIRMED | aefs ch18 (Prometheus/Grafana/OTel in production stack); industry default |
| **Grafana reads Azure Monitor as a data source** | CONFIRMED verbatim | MS Learn "Visualize Azure Monitor data with Grafana": "All versions of Grafana include the Azure Monitor datasource plug-in" |
| Quality drift: healthy infra + degrading answers; caught only by sampled LLM-as-judge vs baseline | CONFIRMED | asdg Ch14.02 ("quality drift detection … statistical baselines + LLM-as-a-judge sampling"); aefs ch16 (cheap-model drift) |
| SLOs richer than uptime: p99 TTFT ceiling, goodput floor, cost/query cap, live-quality floor | CONFIRMED | aefs ch08 (multi-constraint SLOs) + asdg Ch14.02 (operational + quality + budget thresholds); SRE framing standard |
| **AI-SRE: RAG over logs/runbooks/topology; agent investigates, human approves; auto-remediation narrow (restart pod / revert deploy / scale within policy)** | CONFIRMED verbatim | aefs ch23: "grounds LLMs in infrastructure data (logs, runbooks, service topology) via RAG … human approves before any action — auto-remediation stays narrow (restart pod, revert specific deploy, scale within policy) and anyone selling 'set it and forget it' is overselling" |
| "Denial-of-Wallet" framing for broad unsupervised action | CONFIRMED (reasonable) | aefs ch27 (kill-switch / spend caps) supports the cost-risk framing; "DoW" is an editorial label, not a quoted figure |

## Markers resolved (7/7)
1. `[verify: OTel gen_ai.* names]` → removed. Names verified against OTel registry. Added the two real attribute names the draft had described generically (`gen_ai.request.model`, `gen_ai.operation.name`) for precision.
2. `[MS-Learn: Azure Monitor agent observability on OTel GenAI semconv]` → removed; confirmed verbatim.
3. `[MS-Learn: configure_azure_monitor + OpenAI instrumentation → App Insights]` → removed; confirmed.
4. `[MS-Learn: OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT off by default]` → removed; confirmed.
5. `[verify: Prometheus scrape + Grafana pattern]` → removed; confirmed.
6. `[MS-Learn: Grafana integrates with Azure Monitor as data source]` → removed; confirmed verbatim, named the data source plug-in.
7. `[verify: AI-SRE RAG-over-runbooks + human-approved narrow remediation]` → removed; confirmed verbatim against aefs ch23.

## OTel attribute-name check (the critical item)
All `gen_ai.*` names used are REAL and CURRENT per the OpenTelemetry semantic-conventions registry:
- `gen_ai.usage.input_tokens` ✓ current
- `gen_ai.usage.output_tokens` ✓ current
- `gen_ai.request.model` ✓ current (added in edit)
- `gen_ai.operation.name` ✓ current (added in edit)
- No invented attributes present.
- **Note for the editor:** `gen_ai.system` is now DEPRECATED in the registry in favor of `gen_ai.provider.name`. The draft never used `gen_ai.system`, so no correction was needed — flagging only so any future expansion uses `gen_ai.provider.name`.
- Caveat on the env var value: Azure docs accept `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=SPAN_AND_EVENT` as well as `true`. The draft only claims the var "gates capture, off by default," which is accurate and unaffected.

## TTFT/TPOT number decision
N/A — no reference perf figures claimed. TTFT/TPOT appear only as named dashboard panels and an SLO threshold, no values. (Both terms were defined in L04 of the same chapter; not re-expanded here, per STYLE §2 anti-clutter — acceptable as established chapter terms.)

## STYLE pass
- H1 present; lead grabs (one shot to reconstruct a bad answer); one `## Core concepts` block (4 props); handoff div well-formed.
- Ending lands as an aphoristic reframe ("A prediction without an actuator is a dashboard, and a remediation without a human is a liability") — not a template, no banned opener.
- Acronyms: SRE expanded ("site reliability engineering," line 25); SLO expanded ("service-level objectives," line 25). "OpenTelemetry" written in full throughout (the "OTel" abbreviation is not used in body prose, so no expansion needed). TTFT/TPOT are established from L04.
- Unity: second person, present tense, one voice. Clean.

## FLAGGED for editor (non-blocking)
- Future-proofing only: if the lesson or exercise later emits a provider attribute, use `gen_ai.provider.name` (current), not the deprecated `gen_ai.system`.
