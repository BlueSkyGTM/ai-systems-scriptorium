# M4 VERIFY ledger — Module 4, Multi-Agent Systems

VERIFY ran as a 5-subagent fleet (one per chapter batch), each resolving its lessons' authority markers via the
Microsoft Learn connector + WebFetch, source-checking against `synthesis/source/module3/`, and full-reading
against STYLE. **All 15 lessons PASS (fix-applied). Zero residual markers** in student-facing text. Per-lesson
verdicts: `*-verdict.md` in this folder.

## Defects caught and fixed (the gate earning its place)
- **L01** — "order of magnitude more tokens" was false precision → corrected to the sourced ~4× (vs single agent); Anthropic research-system gain made precise (~90%).
- **L02** — FIPA-ACL "20 performatives → 22"; "2000, IEEE ratified → 2002, FIPA published; IEEE took FIPA over in 2005"; A2A RPC `tasks/send → message/send` (current spec); Agent Card path made concrete (`/.well-known/agent-card.json`).
- **L03** — MS Agent Framework **Magentic manager** confirmed via connector; hierarchical-failure claim softened to the sourced MAST data.
- **L04** — removed an unsourced "41–87% failure rate" → reworded to the verified figures (ChatDev ~25%, "well above 40%"); κ=0.88 / 14 modes / 42-37-21 families confirmed. **Naming standardized MASFT → MAST** (the paper's actual taxonomy name).
- **L05** — Temporal / LangGraph / Cloudflare Durable Objects / MS Agent Framework `CheckpointStorage` all confirmed; prose tightened to vendors' framing.
- **L06** — Azure "per-agent budgets" overstatement → corrected to the real Foundry Control Plane primitives (per-project TPM limits + token quotas + model router).
- **L07** — Cilium/eBPF kernel egress reroute confirmed; ACL expanded on first use.
- **L08** — Cloudflare `waitForApproval()` precision fix; **EU AI Act Article 14 reframed** so the statute (human oversight) and the engineering reading (queryable checkpoints / rehearsed rollback) are cleanly separated — no longer overstated as verbatim law.
- **L09** (verified hardest) — **real defect:** Constitutional AI tier 3 "Operator guidelines → Anthropic's guidelines" (per the Jan 2026 constitution); Emoji Smuggling confirmed exactly (arXiv 2504.11168, 100% ASR / six guard systems); Llama Guard 4 S1–S14 confirmed.
- **L10–11** — Microsoft Foundry **routines** confirmed via connector; loop war-story numbers traced verbatim to `loop-stories.md`; the `registry.schema.json` **formally validated** (jsonschema 4.26.0: valid draft-2020-12, malformed entry rejected, cadence regex matches).
- **L12–13** — 3-loop/5-agent threshold softened from "the field converged" to a working heuristic; Azure AI Foundry agent catalog / Entra identity / RBAC / budgets / approval gates confirmed; **de-dup verified at the import level** (`FleetBudgetGuard` imports L06 `TaskBudget`; `shared_inbox` imports L08 `propose`/`commit`); M7-seeding section kept.
- **L14–15** — every benchmark/vendor number re-checked via WebFetch; Gemini "~70% Online-Mind2Web" softened (headline 70%+, OMW-specific ~65.7%) + "as of 2025"; "browser-only → browser-focused"; SWE-bench+ "32.67% of resolved instances" precision; all other figures (OSWorld 38.1%/369, SWE-bench Verified 500/161, Pro 23–59%, GAIA 92/15, WebArena 812, ~450–600ms) confirmed.

## Cross-cutting checks
- **Antilibrary fence — CLEAN:** grep across ch02 for STaR/AlphaEvolve/DGM/RSP/FSF/METR-as-policy/CAIS → zero matches. No frontier-safety research/policy leaked into operational safety.
- **De-dup rule — held:** kill-switch / HITL / budget / verification defined once (ch02) and referenced/imported at fleet scale (ch03), never re-taught.
- **mdbook build — PASS** with all 15 M4 lessons live (M1–M4 render together).
