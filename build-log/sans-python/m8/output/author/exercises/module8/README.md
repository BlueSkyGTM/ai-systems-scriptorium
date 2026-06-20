# Final Systems Engineering Exam — operate the fleet, ship a system, judge it

The course capstone. You do not write new agent code. You point the **Module 7
governed fleet** — the five-agent SWE team you shipped in artifact 03 — at a
production-grade systems problem, operate it under the console, and judge what it
ships against an acceptance rubric. The fleet builds; you operate and grade.

This is the AI Platform Engineering job description, demonstrated: a fleet of
agents run as governed infrastructure, building a production system, judged
against real reference architectures.

## What's here

| File | Role |
|------|------|
| `spec_template.md` | the task spec you fill — chosen track, reference architecture, acceptance criteria |
| `sample_spec.md` | a worked spec (agentic-system / #07) the smoke run uses |
| `spec.py` | the spec parser (stdlib field reader, no front-matter dep) |
| `fleet_adapter.py` | resolves and imports the **real** M7 fleet by walking up to `exercises/module7/03-governed-multi-agent-fleet/` |
| `run_exam.py` | the driver — points the M7 fleet at a spec under the operator console, captures the run |
| `rubric.py` | the acceptance-rubric checker — grades a run against the seven criteria |
| `smoke.py` | the worked example — ship the sample, grade it, print the result |
| `tests/test_smoke.py` | the BUILD->TEST gate |
| `outputs/skill-final-exam.md` | the skill artifact |

There is **no `fleet.py` here**. The exam reuses the shipped fleet — it is reuse,
not a rebuild. The adapter imports `load_fleet` / `ship_feature` from the real M7
artifact on disk.

## How to run

No API key, no Docker, no network. Standard library + pytest only — the M7 fleet's
smoke path is stdlib-only on a deterministic mock, and this exam reuses it.

```bash
# Ship the sample spec's system with the M7 fleet, then grade it:
python smoke.py

# The BUILD->TEST gate: ship + grade + every operator surface
python -m pytest tests/
```

`smoke.py` loads the sample spec, points the real M7 fleet at it, lets the team
plan / implement (the M6 loop) / test / gate the merge, approves the merge through
the HITL inbox, then runs the rubric and prints a pass/fail-per-criterion report.

## The exam (what you do)

1. **Frame the problem and pick the reference architecture.** Choose one of the
   three tracks and one of the 20 Ch16 case studies under it (see
   `02-reference-architectures.md`). Build *a version of* it — scoped small enough
   that the fleet ships it on the gate, with the seam that makes it that
   architecture kept intact.
2. **Write the task spec.** Fill `spec_template.md`: track, reference architecture,
   version, the feature the fleet ships, the business problem, and the acceptance
   criteria you will judge against.
3. **Operate the fleet.** Run it against your spec, then work the console below.
4. **Judge the output.** Run `rubric.py` over the captured run. The seven criteria
   are the strong-project bar applied to a system; the grade is by code, not
   opinion.
5. **Intervene on failure.** Reject a bad merge, tighten a budget, halt the fleet.

## The operator runbook (the M7 console)

Every surface below is a real control on the shipped fleet. The runbook in
`03-operating-and-grading.md` is the same, in prose.

- **Configure the registry / budgets.** `registry.yaml` (in the M7 fleet dir) is
  the contract: five agents, each with `owner`, `autonomy_tier`, least-privilege
  `permissions`, and `budget_daily_usd`, plus a `team_daily_usd` ceiling and the
  `merge: human` gate. Edit it to retarget the team or tighten a cap. The
  orchestrator reads the contract; nothing else changes.
- **Work the HITL inbox.** The merge is the one irreversible action, so it is the
  one human gate. The run suspends with a proposal in `fleet.inbox.pending()`;
  approve it by id — `fleet.inbox.approve(inbox_id, by="you", reason="...")` — then
  `fleet.commit_merge(run, approver="you")`. There is no off-channel approval and
  no auto-merge.
- **Read the audit's four clauses.** After a run,
  `fleet.audit.answers_four_clauses(run.correlation_id)` reconstructs *which agent,
  what authority, what task, what evidence* across all five agents and the human
  merge. `complete: True` means the fleet can answer all four; an empty clause
  means it is unattended, not governed.
- **Use the kill switch.** It is a file the operator owns and every loop reads
  before every action. Trip it (the driver's `kill_first=True`, or `touch` the
  kill-switch path) and the fleet halts before its next action and ships nothing.
  No agent can clear its own stop.

## The acceptance rubric (seven criteria)

`rubric.py` grades a captured run. These are the same seven the guide documents —
the code and the guide are one rubric in two forms.

| # | Criterion | Passes when |
|---|-----------|-------------|
| R1 | RUNS | the fleet shipped the system end to end (merge committed) |
| R2 | EVAL-GATED | the merge passed the tester ACCEPT and the reviewer gate |
| R3 | AUDITED | the cross-agent audit answers all four accountability clauses |
| R4 | BUDGET-BOUNDED | team spend stayed within the team cap; no per-agent breach |
| R5 | HITL-GOVERNED | the merge was human-approved through the inbox by id (no auto-merge) |
| R6 | PROBLEM-FRAMED | the spec names the track, the reference architecture, and the problem |
| R7 | TESTED+VERSIONED | the spec declares acceptance criteria and a version |

A deficient run fails the criterion it offends: an unapproved merge fails R5 and
R1, an incomplete audit fails R3, a blown budget fails R4, a thin spec fails R6/R7.

## Run a real model (opt-in)

The fleet swaps a live model onto any node behind the same `respond(messages)`
seam. Pass it through the driver:

```python
from run_exam import run_exam
# (build an AnthropicLLM per client_llm.py in the M7 fleet dir)
exam = run_exam("my_spec.md", models={"coder-1": AnthropicLLM()})
```

The smoke path stays on the mock so the gate is deterministic and offline.

## Done-when

- [x] `python smoke.py` ships the sample system with the **real** M7 fleet and the
      rubric PASSES the honest run
- [x] `python -m pytest tests/` is green offline (stdlib + pytest)
- [x] the rubric FAILS a deliberately-deficient run (merge unapproved; kill switch
      tripped; thin spec)
- [x] the harness imports the shipped M7 fleet — no `fleet.py` rebuilt here
- [x] the rubric in code == the rubric in `03-operating-and-grading.md`
- [x] ships `outputs/skill-final-exam.md`
