# Observability & SRE-for-AI

When a user reports a bad answer, you get one shot to reconstruct what happened — which model, which prompt version, which retrieved chunks, how many tokens, how long each hop took. If that data was not captured at the moment of the request, it is gone, and you are debugging a non-deterministic system with print statements. Observability is the decision to capture it before you need it, in a shape the whole industry can read.

## Three signals, one standard

Traditional observability rests on three pillars — logs (what happened), metrics (how much, aggregated), and traces (the path of one request through every component). AI observability keeps all three and adds the concerns a normal service never had: output *quality*, *token economics*, and *non-determinism* become first-class signals alongside latency and error rate.

The trace is the load-bearing one. A single AI request is rarely a single call — it is a retrieval, a rerank, a prompt assembly, a model call, maybe a tool invocation and a second model call. A **distributed trace** stitches those into one timeline of parent and child spans, each span carrying what it received, what it returned, how long it took, and what it cost. Without it, a slow or wrong end-to-end response is an unattributable mystery; with it, you see the step that failed.

The thing that makes this durable instead of bespoke is **OpenTelemetry's GenAI semantic conventions** — an agreed set of span and attribute names for model calls, so a trace emitted by your code means the same thing to any backend that reads it. Token usage rides on `gen_ai.usage.input_tokens` and `gen_ai.usage.output_tokens`; the model is named on `gen_ai.request.model` and the operation on `gen_ai.operation.name`; message content is captured only when you opt in. The payoff is that you instrument once against the convention, not once per vendor. Azure Monitor's agent observability reads exactly these conventions — its Application Insights views are built directly on the OpenTelemetry GenAI semantics, so a correctly instrumented app lights up the portal with no Azure-specific tracing code. In Python the wiring is small: call `configure_azure_monitor` and instrument the model SDK, and spans flow to Application Insights. Message content is off by default and gated behind the `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` switch, because prompts and completions are sensitive data you opt into recording, not something you spill by accident.

## Metrics and dashboards: Prometheus and Grafana

Traces explain one request; metrics tell you the shape of all of them. The open-source default is **Prometheus** to collect and store time-series metrics and **Grafana** to visualize them — the serving engine exposes a metrics endpoint Prometheus scrapes on an interval, and Grafana renders the TTFT, TPOT, throughput, and goodput percentiles from lesson 04 as panels you watch live. Grafana reads Azure Monitor as a data source too, through the Azure Monitor data source plug-in, so an Azure-hosted deployment can sit in the same dashboard as a self-hosted one. The dashboard is not decoration. It is the surface where a canary's metrics (lesson 05) are watched, where a soak test's slow memory leak finally shows, and where the on-call engineer looks first at 3 a.m.

## Quality and drift: the half a CPU graph misses

Here is the line that separates AI observability from ordinary SRE. A serving stack can be perfectly healthy — latency nominal, error rate zero, GPUs warm — while the answers quietly get worse. The corpus shifted, an upstream model updated, the traffic mix changed, and the model is now confidently wrong on a class of inputs it used to handle. No infrastructure metric moves. This is **quality drift**, and catching it needs the eval thread running continuously, not just at deploy.

The mechanism is the Module 2 inner loop, sampled in production: run the LLM-as-judge over a small percentage of live traffic, track the pass rate against a statistical baseline, and alert when it degrades beyond noise. This is the outer loop made concrete — the same judges that gated development now monitor production, and they catch the regression that infrastructure monitoring is structurally blind to. Pair it with operational drift detection (a shift in the input distribution itself) and you cover both "the world changed" and "the answers got worse."

## SLOs and SRE-for-AI

The discipline that ties it together is borrowed from site reliability engineering: define **service-level objectives** — explicit targets your service promises to hit — and run against an error budget. For an AI service the SLOs are richer than uptime: a p99 TTFT ceiling, a minimum goodput, a maximum cost per resolved query, and a floor on the live quality score. The SLO is what turns a wall of graphs into a decision — you are not staring at metrics, you are watching whether you are inside budget, and the canary gates, the alerts, and the rollback triggers all hang off those thresholds.

SRE-for-AI extends into incident response, where the 2026 pattern grounds an LLM in your own infrastructure data — logs, runbooks, service topology — over retrieval, so an agent can automate the first stretch of investigation: gather the evidence, propose a hypothesis, and hand a human the decision. Auto-remediation stays deliberately narrow — restart a pod, revert a specific deploy, scale within a policy — because a model that can take broad unsupervised action on your production stack is a Denial-of-Wallet incident waiting for a trigger. Anyone selling fully autonomous "set it and forget it" remediation is overselling; the human stays in the approval seat. A prediction without an actuator is a dashboard, and a remediation without a human is a liability.

## Core concepts

- AI observability is the three pillars — logs, metrics, traces — plus three new first-class signals: output quality, token economics, and non-determinism; the distributed trace is load-bearing because one AI request fans out across retrieval, model calls, and tools.
- OpenTelemetry's GenAI semantic conventions (the `gen_ai.*` span and attribute names) make instrumentation portable — you instrument once against the convention, and backends like Azure Monitor read it natively, with message content gated behind an explicit opt-in.
- Quality drift is the regression infrastructure monitoring cannot see: a stack with nominal latency and zero errors can still get worse, caught only by running the Module 2 LLM-as-judge over a sample of live traffic against a baseline — the eval outer loop made continuous.
- SLOs for an AI service are richer than uptime — a p99 TTFT ceiling, a goodput floor, a cost-per-query cap, and a live-quality floor — and they are the thresholds the canary gates, alerts, and rollback triggers all hang off; SRE-for-AI automates investigation but keeps remediation narrow and human-approved.

<div class="claude-handoff" data-exercise="exercises/module5/06-observability-sre-for-ai/">

**Build It in Claude Code** — instrument `module5-serving/` with OpenTelemetry spans using the GenAI semantic conventions (emit `gen_ai.usage.input_tokens` / `output_tokens` and a model attribute per call), expose a Prometheus-scrapeable `/metrics` endpoint, and stand up a local dashboard that reads it. Add a sampled quality check that runs an LLM-as-judge stub over a fraction of traffic, tracks pass rate against a baseline, and fires an alert when a declared SLO (p99 TTFT, goodput, or quality) is breached. Mock metrics are fine. Open the repo and run the exercise for this lesson.

</div>
