# loop-engineering — Inventory
> Module 3 · agentic loop patterns. Supplements phases 14/15. No antilibrary — all content is seam.

## Structure

| Section | Files | Purpose |
|---|---|---|
| `patterns/` | 10 | The pattern registry (`registry.yaml`, `registry.schema.json`) and reference guides (`README.md`, `changelog-drafter.md`, `ci-sweeper.md`, `daily-triage.md`, `dependency-sweeper.md`, `issue-triage.md`, `post-merge-cleanup.md`, `pr-babysitter.md`). |
| `skills/` | 6 | Specialized agent skills (`glm-extractor`, `loop-budget`, `loop-triage`, `loop-verifier`, `minimal-fix`). |
| `templates/` | 8 | Reusable markdown and configuration templates (`SKILL.md.*`, `STATE.md.template`, `loop-*.md.template`, `pattern-template.md`). |
| `stories/` | 11 | Field reports and failure stories (`README.md`, `changelog-drafter-week-one.md`, `daily-triage-report-only.md`, `dependency-sweeper-week-one.md`, `l1-to-l2-graduation.md`, `loop-budget-example.md`, `loop-run-log-example.md`, `multi-loop-collision.md`). |
| `docs/` | 16 | Documentation, concepts, and visual assets (`GITHUB_PAGES.md`, `RELEASE.md`, `_config.yml`, `adopters.md`, `anti-patterns.md`, `assets`, `concepts.md`, `failure-modes.md`). |
| `examples/` | 33 | Tool-specific implementations and examples (`README.md`, `claude-code`, `codex`, `github-actions`, `grok`, `mcp`). |
| `tools/` | 39 | CLI utilities for loop management (`loop-audit`, `loop-cost`, `loop-init`). |
| `starters/` | 58 | Starter loop projects (`README.md`, `changelog-drafter`, `ci-sweeper`, `dependency-sweeper`, `minimal-loop`, `minimal-loop-claude`, `minimal-loop-codex`, `post-merge-cleanup`). |
| `root/` | 6 | Top-level governance and reference files (`LOOP.md`, `loop-budget.md`, `loop-run-log.md`, `AGENTS.md`, `STATE.md`, `README.md`). |

## Meta (AGENTS.md, STATE.md)

**AGENTS.md**
Establishes the repository conventions for humans and loops. It defines the build and verify commands using the `loop-audit` CLI, CI workflows (`validate-patterns` and `audit`), and review norms (emphasizing that patterns must remain tool-agnostic and failure stories must include token cost/root cause). It defines the operational levels: daily triage via the `loop-triage` skill (L1 report-only) and PR-based human-reviewed fixes via `minimal-fix` and `loop-verifier` (L2), with git worktrees used for isolation.

**STATE.md**
Tracks the real-time operational state of the repository's own agentic loops. It records the last automated daily-triage run, the current loop readiness score (100, Level L3), and high-priority maintenance tasks such as keeping npm packages current. It also maintains a watch list for expanding failure stories and validates scaffolds, explicitly logging recent ignored noise to maintain signal-to-noise ratio.

## Notes

*   `starters/` = starter loop projects for fast deployment.
*   `patterns/registry.yaml` + `registry.schema.json` = pattern registry.
*   `loop-budget` (in `skills/` and `templates/`) = kill switch / loop safety.
*   6 images + Mermaid diagrams in 3 files (under `docs/` and `docs/assets`).
