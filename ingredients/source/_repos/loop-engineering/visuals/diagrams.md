# Visuals — Mermaid Diagrams

> Mermaid from loop-engineering markdown. Plus 6 images copied to `output/visuals/`.


## `README.md` — Anatomy of a Loop (Mermaid)
```mermaid
flowchart LR
    A[Schedule / Automation] --> B[Triage Skill]
    B --> C[Read + Write STATE / Memory]
    C --> D[Isolated Worktree]
    D --> E[Implementer Sub-agent]
    E --> F[Verifier Sub-agent<br/>tests + gates]
    F --> G[MCP / Git / Tickets]
    G --> H{Human Gate?}
    H -->|safe / allowlisted| I[Commit / PR / Action]
    H -->|risky / ambiguous| J[Escalate to human<br/>with full context]
    I --> A
    J --> A
```

## `docs/concepts.md` — Concept Map
```mermaid
flowchart TB
  subgraph human [Human — highest leverage]
    Design[Design loop]
    Judgment[Encode judgment in skills + verifiers]
    Gate[Human gates for high-risk work]
  end

  subgraph loop [Loop system]
    Schedule[Scheduler /loop cron Action]
    Triage[Triage skill]
    State[(STATE.md / Linear)]
    Impl[Implementer sub-agent]
    Verify[Verifier sub-agent]
    MCP[MCP connectors]
  end

  Design --> Schedule
  Schedule --> Triage
  Triage --> State
  State --> Impl
  Impl --> Verify
  Verify --> MCP
  MCP --> State
  Verify --> Gate
  Judgment --> Triage
  Judgment --> Verify
```

## `docs/pattern-picker.md` — Which Pattern When?
```mermaid
flowchart TD
    A[What hurts right now?] --> B{CI red?}
    B -->|yes| C[CI Sweeper]
    B -->|no| D{PRs stalling?}
    D -->|yes| E[PR Babysitter]
    D -->|no| F{Morning chaos or noisy issues?}
    F -->|yes| G[Daily Triage + Issue Triage]
    F -->|no| H{Dependabot / CVE noise?}
    H -->|yes| I[Dependency Sweeper]
    H -->|no| J{Merge debt / TODOs piling up?}
    J -->|yes| K[Post-Merge Cleanup]
    J -->|no| L{Release notes / changelog stale?}
    L -->|yes| M[Changelog Drafter]
    L -->|no| N{Tight token budget?}
    N -->|yes| M
    N -->|no| G
```
