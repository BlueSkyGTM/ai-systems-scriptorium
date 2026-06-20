# Skill — Final Systems Engineering Exam (operate a governed fleet, judge a system)

## What it proves

You can run a fleet of agents as governed infrastructure to ship a production
system, and judge what it ships against a real bar. This is the AI Platform
Engineering job, demonstrated end to end: you frame a problem against a reference
architecture, point the governed M7 fleet at it, operate it under the console
(registry, budgets, HITL inbox, cross-agent audit, kill switch), and grade the
result with a seven-criterion acceptance rubric. The fleet builds; you operate and
judge. No new agent code — the exam reuses the shipped M7 fleet whole and adds the
operator-and-grader layer on top.

## What it does

Given a task spec (chosen track + Ch16 reference architecture + acceptance
criteria), the exam:

1. **resolves the real fleet** — the adapter walks up to the shipped
   `exercises/module7/03-governed-multi-agent-fleet/` and imports its `load_fleet`
   / `ship_feature`; nothing is rebuilt;
2. **points the fleet at the spec** — the driver runs `ship_feature` so the team
   plans, the coders implement (the M6 loop), the tester ACCEPTs, the reviewer
   gates, and the merge is PROPOSED to the HITL inbox;
3. **operates the console** — it suspends at the inbox, approves the merge by id
   (the only legal path), holds the kill switch, and stays under the fleet budget;
4. **captures the run** — status, the human approver, the four-clause audit, the
   budget, the plan — into a record the rubric reads;
5. **grades the system** — `rubric.py` checks seven criteria (runs, eval-gated,
   audited, budget-bounded, HITL-governed, problem-framed, tested+versioned) and
   prints a pass/fail-per-criterion verdict.

## How to invoke

```bash
python smoke.py            # ship the sample system with the M7 fleet, then grade it
python -m pytest tests/    # the BUILD->TEST gate: ship + grade + every operator surface
```

Offline, standard library + pytest. No API key, no Docker, no network — the exam
reuses the M7 fleet's stdlib-only mock smoke path.

## How to extend

- **Pick a different track:** write a new spec against any of the 20 Ch16 case
  studies — eval-gated CI/CD, multi-tenant RAG, or an agentic system.
- **Retarget the fleet:** edit `registry.yaml` in the M7 fleet dir — a tighter
  budget, a stricter gate, a new agent — and the orchestrator runs it unchanged.
- **Run a real model:** pass `models={"coder-1": AnthropicLLM()}` to `run_exam`;
  the smoke path stays on the deterministic mock.
- **Harden the rubric:** add a criterion (e.g. require two inbox approvers) in
  `rubric.py` — and document it in `03-operating-and-grading.md` so the guide and
  the code stay one rubric.

## The portable seams

- **the spec contract** — a markdown task spec the fleet is pointed at: the
  problem is an input, not code;
- **the fleet adapter** — resolve-and-import of the shipped artifact: the exam
  reuses the real fleet, it does not fork it;
- **the rubric** — a pass/fail-per-criterion grade computed from the captured run:
  the verdict is reproducible from the record, not a matter of opinion.

## Where it sits in the arc

This is the terminal node of the compounding arc: single agent (M6) → team (M7
composition) → governed fleet (M7 finale) → production system, operated and judged
(M8). The exam is the portfolio capstone — proof you can run a governed fleet to
ship a system and stay accountable for every action it takes.
