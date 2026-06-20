# Module 3 · Fleet Stories
> Source: `stories/`. Real incidents that motivate fleet governance.

## Budget Cap Stopped a Runaway Loop [THREAD: safety]
- **What happened:** A manager loop spawned 12 sub-agent retries on a flaky API, spending 8× normal by 6am. The `budget_daily_tokens` cap on the manager manifest paused the run at 100%, but sub-agents had no individual caps, allowing the manager to absorb all spend.
- **Fleet pattern demonstrated:** Fleet Budget Guard (F1).
- **What the student learns:** Fleet Budget Guard without per-agent attribution hides runaway delegation trees; cap the manager and the workers.

## Inbox Bypass — "Just This Once" [THREAD: safety]
- **What happened:** An on-call engineer approved a deploy agent via DM instead of the configured shared inbox. Incident review could not answer "evidenced by what?" and compliance flagged it as a policy bypass, leading to a ban on DM approvals and a requirement for `IN-*` ticket IDs for destructive tools.
- **Fleet pattern demonstrated:** Shared Inbox HITL (F1).
- **What the student learns:** An inbox nobody uses is worse than no inbox because it creates false confidence; week one means approving only through the channel.

## LangSmith Fleet → Git Registry Backup [THREAD: safety]
- **What happened:** A platform team using LangSmith Fleet needed git-backed disaster recovery. They implemented a weekly export of the workspace agent list to `agents/registry.yaml` with drift diffs in PR comments, successfully restoring two agents after an accidental delete.
- **Fleet pattern demonstrated:** Team Agent Registry + Cross-Agent Audit (F1).
- **What the student learns:** Platform registry plus git backup is the F1 minimum for enterprises; neither alone satisfies the full accountability sentence.

## Registry Before Inbox — Honest Win
- **What happened:** A team with 12 agents across Slack and IDE lacked a central list. A two-hour inventory surfaced four duplicate "weekly report" agents with different credentials, leading to retiring two and naming owners for the rest. They purposefully skipped setting up a Shared Inbox until the registry was complete.
- **Fleet pattern demonstrated:** Team Agent Registry (F1).
- **What the student learns:** Fleet engineering week one is boring catalog work, and that is the point.

## Shadow Agents Found in Audit — Honest Failure
- **What happened:** A team had 8 "official" agents in LangSmith but 14 actually running across IDE configs. Running `fleet-audit` scored 32/100 (F0+), revealing 6 shadow agents with shared API keys and no owner, which forced the team to retire 4 shadows and register 10 with owners.
- **Fleet pattern demonstrated:** Team Agent Registry (F1).
- **What the student learns:** Audit score is a governance instrument, not a vanity metric; F1 means 100% active agents in registry, not just writing a FLEET.md.
