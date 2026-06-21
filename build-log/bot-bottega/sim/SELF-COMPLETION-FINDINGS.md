# agent-os-starter — Self-Completion Findings (first-person agent POV)

Method (Ray's idea): the engine is recursive — the agent builds the very environment it will then operate,
so ask the agent bluntly what it needs. Two cold Sonnet agents read ONLY `BOOT-KIT.md` and reported in
first person: one as the **builder who will operate what it builds**, one as the **operator handed the
result and told to run it**.

## Core result: the kit is blind to the operator, and the operator is a cold, memoryless self

Both agents, independently:

- The kit frames the agent as building for a **human** successor, not for **a cold instance of itself**.
  Builder: *"the kit knows how to hand something off to a human; it does not know that the person
  receiving the handoff is me."*
- That blindness **changes what gets built**. Builder: a single sentence at the top of the kit — *"this
  system will be operated by a cold AI agent with no memory of this build session"* — *"would have changed
  my entire posture while reading."* Without it, the agent defaults to building for a human reader.
- The build→operate handoff has **no ceremony**. Operator: *"The kit ends at 'system built and handed
  off.' It has no exit ceremony... I arrive blind."* *"A recipe card that does not tell me what was
  cooked, whether it was eaten, or what to do if it's cold."*
- The unsafe moment both named: a cold operator with no run log **re-runs an already-run or partially-run
  action** — which the action-class taxonomy does NOT catch (re-running a local action is not
  "external-mutation"). The danger is memorylessness, not permission.

## What the agents say they need (their list, not ours)

1. **Awareness primitive:** the bootloader states up front that the operator is a cold, memoryless agent —
   build for it.
2. **`OPERATOR.md`:** a fixed-path, build-time-generated self-description read first every boot — purpose,
   current state + where to read it, last-run summary, next expected action, forbidden actions, gate
   triggers. The system must "explain itself the way a bootloader explains itself to a CPU."
3. **Structured run log / STATUS:** last-run metadata (when, what ran, succeeded/failed/pending) so the
   cold operator knows whether it is fresh, mid-run, or broken.
4. **Standing authorization record:** the builder's per-system action-class calls recorded as standing
   rules, not a framework the operator re-derives (re-derivation risks crossing a fenced line).
5. **Async gate protocol:** a gate-pending file (gate type, decision required, safe default) for when no
   human is live — checkable and resumable, not just "halt."
6. **Operational dud criterion:** can't read state / last run failed with no recovery path → declare an
   operational dud and halt rather than guess (the kit's dud is build-phase only).
7. **Recovery runbook + an exit/handoff ceremony** as the build's mandatory final step — and the operator
   produces the same handoff for the NEXT operator. The recursion continues.

## The big one: the agents just defined "AI Operating System"

The autoplan reviewers said "AI OS" was unfalsifiable. The first-person agents gave the falsifiable
definition by stating what they need to operate:

> A system is **agent-operable** iff a cold, memoryless agent can read one fixed file, learn the current
> state, know what is allowed, run or recover safely, and hand off again.

So the engine's real deliverable per gig is **that operating environment** (`OPERATOR.md` + run log +
standing rules + handoff ceremony), not just the working system. Generating it is the build's final,
mandatory step. This is also the concrete form of the reviewers' "instrument it" and "narrow the
definition."

## What it means for the design

Ray's recursion insight is the design center: `agent-os-starter` builds **self-describing,
self-resumable operating environments for a cold successor-self.** The 7-domain punch-list (authorization
refinements, discovery step, rollback) all fold under this. And the method is validated: asking the agent
what it needs produced a sharper, more structural spec than outside analysis did. Keep co-designing with
the agent.
