# Metrics, Observability & Rollout

> **Migrated from** `aefs-module4-infrastructure-production` (Ph17 metrics/rollout) + `asdg-module4-deploy-
> chapters` (Ch14 eval & observability). The **outer loop** of eval-driven development (the inner loop was
> M2).

The production quality control plane:

- **Inference metrics** — TTFT / TPOT / ITL / goodput / P99 → **load testing** → observability-stack
  selection.
- **Progressive rollout** — observability → **shadow traffic → canary → A/B testing**. Rollback via registry
  + flags.
- **Model routing → AI gateways** — routing / fallback / secrets management.
- **SRE-for-AI → chaos engineering** — the resilience sub-thread (detects infra degradation, distinct from
  output-quality eval).

**Inbound:** M2 LLM-as-judge and RAG-evaluation (the eval thread). **Versioning thread (Gap 3):** the full
lifecycle is formalized here — staging, promotion, rollback. **Relocated artifact:** the LLM observability &
eval dashboard (11) is built here.

This is the same eval discipline as Module 2, at production scale — the inner loop (development) hands off to
the outer loop (monitoring).
