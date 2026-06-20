# Exercise 06 — Observability & SRE-for-AI

## Goal

Instrument `module5-serving/` with OpenTelemetry spans using the GenAI semantic conventions, expose a Prometheus-scrapeable `/metrics` endpoint, stand up a local dashboard, and add a sampled LLM-as-judge quality check that alerts when a declared SLO is breached — all local, mock metrics fine.

## Why

When a user reports a bad answer, you get one shot to reconstruct the request — model, prompt, retrieved chunks, tokens, per-hop latency. You capture it before you need it, in the OpenTelemetry shape every backend reads, and you watch quality continuously, because a stack can be perfectly healthy while the answers quietly get worse. This is the eval outer loop made durable.

## Steps

1. **Trace one request end to end.** Add `module5-serving/obs/tracing.py` that wraps a request in an OpenTelemetry trace with parent and child spans for each hop (retrieval stub → prompt assembly → model call). Use the GenAI semantic conventions for the model span: emit `gen_ai.usage.input_tokens` and `gen_ai.usage.output_tokens` and a model-name attribute. Gate message-content capture behind an explicit opt-in flag (mirror `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`) — off by default. Export to a console or local OTLP collector; no cloud.

2. **Prometheus-scrapeable metrics.** Expose `module5-serving/obs/metrics.py` serving a `/metrics` endpoint in Prometheus text format with TTFT, TPOT, throughput, and goodput (reuse the recorder from exercise 04). Confirm a local Prometheus scrape — or a raw `GET /metrics` — returns valid metric lines.

3. **Local dashboard.** Stand up a minimal dashboard that reads `/metrics` and renders the percentile and goodput panels. A local Grafana wired to the scrape is ideal; a small static HTML page polling `/metrics` is an acceptable no-Grafana substitute. Mock metric values are fine — the wiring is the deliverable, not real traffic.

4. **Sampled quality check.** Add `module5-serving/obs/quality.py` that runs an LLM-as-judge *stub* (a deterministic scorer, no real model needed) over a configurable fraction of requests, records the pass rate, and compares it to a baseline. This is the Module 2 inner-loop judge, now sampled in production — the outer loop made continuous.

5. **SLOs and alerts.** Declare SLOs richer than uptime: a p99 TTFT ceiling, a goodput floor, and a live-quality floor. When any is breached, fire an alert (log line plus an alert record). Prove that quality drift — pass rate falling below the floor while latency and error rate stay nominal — fires the alert that infrastructure metrics alone would miss.

6. **Narrow remediation, human in the seat.** Add one toy auto-remediation that stays narrow (e.g. flip the rollout flag from exercise 05 back to `stable` on a quality breach) and require an explicit approval step before it acts. Document in a comment why broad unsupervised remediation is a Denial-of-Wallet risk and stays banned.

## Done when

- A request produces a distributed trace with parent/child spans, and the model span carries `gen_ai.usage.input_tokens` / `output_tokens` per the GenAI semantic conventions, with content capture off by default.
- `/metrics` returns valid Prometheus-format lines and a local dashboard renders the percentile and goodput panels.
- The sampled LLM-as-judge stub tracks pass rate against a baseline, and a deliberate quality drop fires an SLO-breach alert while latency and error metrics stay green — proving the catch infrastructure monitoring is blind to.
- Auto-remediation is narrow and gated behind an explicit human approval; it never takes broad action on its own.
- Everything runs locally — no Azure resource, no cloud collector, no API key.

## Stretch

Add a drift detector on the *input* distribution (e.g. a shift in mean prompt length or topic mix) so you cover both "the answers got worse" and "the world changed." Export the traces to a real local OTLP collector and confirm the `gen_ai.*` attributes survive the round-trip intact.
