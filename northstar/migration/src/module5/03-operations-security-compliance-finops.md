# Operations: Security, Compliance, FinOps

> **Migrated from** `aefs-module4-infrastructure-production` (Ph17 ops) + `asdg-module4-deploy-chapters`
> (Ch12 security/access, Ch13 reliability/safety) + `mwml-module4-deploy-scripts` (CI/serving subset). The
> "runs in a regulated enterprise" layer.

- **Security** — secrets / vault / rotation / egress control; RBAC / ABAC, multi-tenant isolation. Continues
  M2 guardrails / prompt-injection into the infra layer.
- **Compliance** — SOC2 / HIPAA / GDPR / EU-AI-Act / ISO-42001. The reliability & safety material
  (guardrails, red-teaming) lands here as **deployed infrastructure**, not concept.
- **FinOps** — per-user / per-task / per-tenant attribution, spend caps, kill switches; caching economics +
  batch APIs (50% discount) → cost optimization.

This cluster is the **clearest AI-Platform-Engineering-specific material** — finops-for-tokens and
AI-specific compliance don't exist in generic platform engineering.

**Relocated artifact:** the MCP server with registry & governance (13) is built here; its governance also
feeds the M7 fleet finale. **mwml deploy/serving/CI** material stays; its model-centric training-pipeline
material is in the [Antilibrary](../antilibrary.md).

**Safety callout (Gap 4):** red-teaming + guardrail infrastructure is the M5 surface of the distributed
safety thread.
