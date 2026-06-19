# Autonomous Systems & Operational Safety

> **Migrated from** `aefs-module3-agent-engineering` (Ph15, operational-safety half). The research/policy half
> (STaR, AlphaEvolve, DGM, RSP, FSF, METR, CAIS) → [Antilibrary](../antilibrary.md). This is **how you
> *operate* agents safely = platform engineering.**

The qualitative break: agents that run minutes-to-hours, where every single-turn assumption (context, trust,
failure modes, cost, observability) breaks. The operational stack:

- **Durable execution** — long-horizon agents don't run in `while True`: every LLM call becomes an activity
  with checkpoint, retry, replay (Temporal, LangGraph→Postgres, Cloudflare Durable Objects). Sessions pause
  on human input, survive deploys, resume from the latest checkpoint by `thread_id`.
- **Action budgets & cost governors** — defend "Denial of Wallet" with limits at every time scale:
  `max_tokens`, per-task token/dollar budgets, per-tool caps, iteration caps, velocity limits (>$50/10min →
  cut), tiered routing, kill-switch on breach. Different failure modes need different time scales.
- **Kill switches, circuit breakers, canary tokens** — a kill switch the agent reads but cannot write
  (feature flag / Redis / signed config); a circuit breaker (closed/open/half-open, trips on patterns like
  five identical calls); canary tokens (honeypot credentials an agent has no reason to touch). eBPF/Cilium
  can reroute a quarantined pod's egress at the kernel layer.
- **HITL: propose-then-commit** — persist the proposed action with an idempotency key, surface intent /
  lineage / blast-radius / rollback, commit only on positive acknowledgement, verify after. The canonical
  failure is the rubber-stamp — mitigate with challenge-and-response checklists. (LangGraph `interrupt()`,
  MS Agent Framework `RequestInfoEvent`, Cloudflare `waitForApproval()`.)
- **Checkpoints & rollback** — idempotency key + precondition check + post-action verify + rollback-on-fail;
  without all four, a retry can double-execute an approved action. EU AI Act Art. 14 makes queryable
  checkpoints/rehearsed rollbacks mandatory for high-risk systems.
- **Guardrails** — Constitutional AI (four-tier priority: safety/oversight → ethics → guidelines →
  helpfulness; hardcoded prohibitions vs operator-adjustable defaults) and Llama Guard 3/4 input/output
  classification. Honest caveat: classifiers are a *layer*, not a solution (Emoji Smuggling hit 100% ASR on
  six guard systems) — layer them with hard limits that don't bend.

## Forward

The autonomous-coding-agent landscape (OpenHands, Cline, Claude Code permission modes / Auto Mode) and the
browser-agent attack surface (indirect prompt injection "cannot be fully patched") set up the M6/M7 agent
artifacts.
