# Final Exam — Task Spec (worked sample)

A filled spec the smoke run uses to drive the exam offline. It scopes *a version
of* an autonomous coding agent (Ch16 #07) down to one feature the M7 fleet ships
on the deterministic mock — small enough for the gate, real enough to keep the
seam that makes it an agentic system: a planner, parallel coders, and a
test-gated, human-approved merge.

**Track:** agentic-system

**Reference architecture:** #07 Autonomous Coding Agent

**Version:** 1.0.0

**Feature:** addition operator

**Business problem:** A platform team wants a feature shipped by a governed agent fleet — planned, implemented in parallel, test-gated, and merged only on human approval — so a human stays accountable for every action the agents take.

## Acceptance criteria

- the produced system's acceptance suite passes (the fleet's verify gate ACCEPTs)
- the run stays within the team budget cap and no per-agent cap breaches
- the cross-agent audit answers all four accountability clauses for the run
- the merge is human-approved through the HITL inbox, never auto-merged
