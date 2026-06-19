# Visuals — Mermaid Diagrams

> Mermaid diagrams from fleet-engineering markdown. Plus 2 images copied to `output/visuals/` (cobus-greyling.jpg, fleet-engineering-header.jpg).


## `README.md` — Anatomy of a Fleet (Mermaid)
```mermaid
flowchart TB
    subgraph Registry
        R[Agent Registry<br/>manifests + owners]
    end
    subgraph Identity
        I[Credentials model<br/>Claw vs Assistant]
        P[Permissions<br/>clone · run · edit]
    end
    subgraph Operations
        L1[Loop A]
        L2[Loop B]
        L3[Loop C]
    end
    subgraph Control
        IN[Shared Inbox<br/>HITL]
        AU[Audit / Traces]
        EC[Budgets & Quotas]
        KS[Kill Switch]
    end
    R --> L1 & L2 & L3
    I --> L1 & L2 & L3
    P --> L1 & L2 & L3
    L1 & L2 & L3 --> IN
    L1 & L2 & L3 --> AU
    EC --> L1 & L2 & L3
    KS --> L1 & L2 & L3
```

## `docs/concepts.md` — Concept Map
```mermaid
flowchart TB
    CE[Context Engineering] --> HE[Harness Engineering]
    HE --> LE[Loop Engineering]
    LE --> FE[Fleet Engineering]
    FE --> R[Registry]
    FE --> I[Identity]
    FE --> P[Permissions]
    FE --> IN[Inbox]
    FE --> AU[Audit]
    FE --> EC[Economics]
    FE --> SC[Sovereign Control]
```

## `docs/pattern-picker.md` — Which Fleet Pattern When?
```mermaid
flowchart TD
    A[What hurts?] --> B{Don't know what agents exist?}
    B -->|yes| C[Team Agent Registry]
    B -->|no| D{Risky actions without approval?}
    D -->|yes| E[Shared Inbox HITL]
    D -->|no| F{Too many manager/worker handoffs failing?}
    F -->|yes| G[Hierarchical Delegation]
    F -->|no| H{One good agent, many teams want it?}
    H -->|yes| I[Agent Clone & Fork]
    H -->|no| J{Token bill surprise?}
    J -->|yes| K[Fleet Budget Guard]
    J -->|no| L{Compliance / incident review?}
    L -->|yes| M[Cross-Agent Audit]
    L -->|no| C
```

## `docs/primitives.md` — Primitive Dependency Graph
```mermaid
flowchart TD
    REG[Registry] --> ID[Identity]
    REG --> PERM[Permissions]
    ID --> INBOX[Inbox]
    PERM --> INBOX
    INBOX --> AUD[Audit]
    AUD --> ECO[Economics]
    ECO --> SOV[Sovereign Control]
```

## `docs/stack.md` — The Agent Engineering Stack
```mermaid
flowchart LR
    P[Prompt Engineering] --> C[Context Engineering]
    C --> H[Harness Engineering]
    H --> L[Loop Engineering]
    L --> F[Fleet Engineering]
```
