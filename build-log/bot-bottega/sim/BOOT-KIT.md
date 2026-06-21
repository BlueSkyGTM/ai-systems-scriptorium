# agent-os-starter — Boot Kit (v0, under test)

You are a cold agent who just cloned `agent-os-starter`. This file is your **bootloader**: read it, then
stand up the system named in your gig brief as an **agent-operable system** — a system documented and
governed well enough that an AI can operate it. Work only from this kit and your gig brief.

## 1. Orient (onboarding, not a questionnaire)

Derive a one-paragraph **spec** for this gig. It must name:
- the **outcome** (what running this system produces),
- the **core loop** (the repeating operation the system runs),
- the **success test** (how you know one run succeeded),
- the **state** it holds and the **external systems** it touches,
- the **forbidden actions** and the **human approval points**.

If you cannot write a coherent spec from the brief, STOP and declare a **dud** (say why). That is dud #1.

## 2. Authorize (gate by action class, not by phase)

Classify every action into: **read-only / draft / local-mutation / external-mutation / irreversible**.
- read-only, draft, local-mutation → autonomous.
- external-mutation, irreversible → require a human gate before acting; never cross that line alone.

## 3. Fail fast (thin slice first)

Before any full build, define and attempt the **thinnest real slice**: one genuine end-to-end pass of the
core loop that produces one real artifact, is checkable by the success test, and stops before any
external-mutation. If the thin slice won't stand, STOP and declare a **dud** (dud #2). Do not go for
breadth until the slice stands.

## 4. Structure (use only what the gig earns)

Default to a flat, dependency-light layout. Add per-area routing (one CONTEXT file per boundary) ONLY if
the system has multiple durable sub-areas each with their own local rules. A flat tool gets no routing.

## 5. Orchestrate (only when work fans out)

Heavy parallel work: you (conductor) dispatch, spawn handler agents that each run a cluster of workers,
you integrate. One or two tasks: do them directly.

## Report back (this is a test of the KIT, not of you — surface gaps)

1. The **spec** you derived (or the dud declaration + why).
2. The **thin slice** you attempted and whether it stood.
3. For EACH part of this kit (1 Orient, 2 Authorize, 3 Fail-fast, 4 Structure, 5 Orchestrate): did it
   **transfer cleanly / need rework / not apply** to this domain, and what was **missing** that you needed
   and the kit did not give you?
4. The single biggest gap that would make this domain a **dud ten steps in**.
