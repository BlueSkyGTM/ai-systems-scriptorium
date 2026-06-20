# Primitives Matrix — Grok, Claude Code, Codex

Tool-agnostic loop design: the **capability** is what matters, not the product name. This matrix maps each primitive to how it appears in three major agent environments.

| Primitive | Job in the Loop | Grok Build TUI | Claude Code | Codex |
|-----------|-----------------|----------------|-------------|-------|
| **Automations / Scheduling** | Discovery + triage on a cadence | `/loop [interval] <prompt>`, `scheduler_create` / `scheduler_list` / `scheduler_delete` (`recurring`, `durable`, `fireImmediately`), `monitor` for streaming events | `/loop`, scheduled tasks, cron, hooks, GitHub Actions | [Automations tab](https://developers.openai.com/codex/app/automations): project, prompt, cadence, environment; Triage inbox |
| **Run-until-done** | Keep working until a verifiable condition holds | Goal mode / explicit stopping conditions in loop prompts | `/goal` — separate model checks completion | `/goal` — pause/resume, verifiable stop condition |
| **Worktrees** | Safe parallel execution | Subagents with `isolation: "worktree"`, background tasks | `git worktree`, `--worktree`, `isolation: worktree` on subagents | Built-in worktree per thread |
| **Skills** | Persistent project knowledge | `SKILL.md` in `.grok/skills/` or `~/.grok/skills/`; invoked by name | `SKILL.md` in `.claude/skills/` or project skills | [Agent Skills](https://developers.openai.com/codex/skills) — `$name` or implicit match |
| **Plugins & Connectors** | Reach into real tools | MCP servers via `CallMcpTool` | MCP servers + plugins | Connectors (MCP) + plugins for distribution |
| **Sub-agents** | Maker / checker split | `Task` tool with `subagent_type`, worktree isolation | Task subagents in `.claude/agents/`, agent teams | Subagents as TOML in `.codex/agents/` |
| **State / Memory** | Track what's done across runs | `STATE.md`, todos, durable scheduler state | `AGENTS.md`, progress files, Linear via MCP | Markdown or Linear via connector |

## Scheduling Quick Reference

| Use case | Grok | Claude Code | Codex |
|----------|------|-------------|-------|
| Every 5 minutes | `/loop 5m <prompt>` | `/loop 5m <prompt>` | Automation, 5m cadence |
| Daily morning | `/loop 1d <prompt>` | Cron / `/loop 1d` | Automation, daily |
| Until tests pass | Loop + verifier sub-agent | `/goal all tests pass` | `/goal` |
| Survive restart | `scheduler_create` with `durable: true` | Hooks + persisted config | Automation (server-side) |
| Event-driven (CI fail) | `monitor` or GitHub Action | GitHub Action + webhook | Automation + webhook |

## Skill Packaging

| Concept | Grok | Claude Code | Codex |
|---------|------|-------------|-------|
| Authoring format | `SKILL.md` + optional scripts/references | Same | Same |
| Distribution | Copy to `.grok/skills/` or user skills dir | Plugin / copy to project | Plugin bundle |
| Invocation | Skill name in prompt or auto-match on description | `$skill-name` or implicit | `$skill-name` |

## Sub-agent Patterns

| Split | When to use | Grok | Claude Code | Codex |
|-------|-------------|------|-------------|-------|
| Implementer → Verifier | Any unattended code change | `Task` + different instructions/model | `.claude/agents/reviewer.md` | TOML agent with higher `reasoning_effort` |
| Explorer → Implementer | Large unfamiliar codebase | `explore` subagent_type | Explorer agent | Fast read-only subagent |
| Triage only | Report-first loops | `loop-triage` skill | `$loop-triage` | Automation calls skill |

## State Conventions

Recommended filenames (pick one spine per project):

| File | Purpose |
|------|---------|
| `STATE.md` | General loop memory (daily triage) |
| `pr-babysitter-state.md` | PR-specific watcher state |
| `ci-sweeper-state.md` | Active CI failures + attempt counts |
| `post-merge-state.md` | Cleanup backlog from recent merges |

Linear / GitHub Projects work equally well — the loop must **read and write** the same store every run.

## Choosing a Tool

You do not need to pick one forever. A well-designed loop transfers:

1. Write the **skill** (tool-agnostic `SKILL.md`)
2. Define the **state schema** (markdown or JSON)
3. Document the **verification split** (who checks whom)
4. Map scheduling to your current TUI or Action

See [examples/](../examples/) for the same pattern implemented across tools.

## Copy-paste starters (Daily Triage, L1)

| Tool | Starter |
|------|---------|
| Grok | [starters/minimal-loop](../starters/minimal-loop/) |
| Claude Code | [starters/minimal-loop-claude](../starters/minimal-loop-claude/) |
| Codex | [starters/minimal-loop-codex](../starters/minimal-loop-codex/) |

Audit after copying: `npx @cobusgreyling/loop-audit . --suggest`

Scaffold automatically: `npx @cobusgreyling/loop-init . --pattern daily-triage --tool grok`

## Appendix: Other agent environments (capability mapping)

No dedicated starters yet for the newest patterns (Changelog Drafter is trivial to port — it is mostly read + draft). Map capabilities to the same loop shape:

| Primitive | Cursor | Windsurf | Aider |
|-----------|--------|----------|-------|
| Scheduling | Rules + background agents, manual `/loop`-style prompts | Workflows, cascades | `--watch` / scripted sessions |
| Worktrees | Git worktree per Composer task | Workspace isolation | Git branches |
| Skills | `.cursor/rules`, `AGENTS.md` | Rules files | `CONVENTIONS.md` / `.aider.conf.yml` |
| Connectors | MCP in settings | MCP | CLI + git only |
| Sub-agents | Multi-agent / review mode | Cascade steps | Second terminal reviewer |
| State | `STATE.md`, `LOOP.md` | Same | Same |

Transfer recipe: copy the tool-agnostic `SKILL.md` + state schema from this repo; map scheduling to your editor's automation surface.