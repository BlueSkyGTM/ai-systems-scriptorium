# M8 BUILD→TEST gate ledger — Module 8, Final Systems Engineering Exam

The exam harness was run **locally, offline, stdlib-only**, both at author-stage and **after relocation to its
shipped location** (`exercises/module8/`, sibling to `exercises/module7/`). Re-run by Opus.

| Check | Result |
|---|---|
| `python smoke.py` (shipped location) | exit 0 — the **real M7 fleet** ships the sample system (status: merged, audit complete across 6 agents, $0.11/$1.00 budget); the rubric grades **7/7 PASS** |
| `python -m pytest tests/` | **9 passed** |
| Reuses the real M7 fleet (not a rebuild) | confirmed — no `fleet.py` in the exam dir; `fleet_adapter.py` walks up to `exercises/module7/03-governed-multi-agent-fleet/` and imports `load_fleet`/`ship_feature` |
| Rubric fails deficient runs | confirmed — unapproved merge (R5+R1 fail; fleet refuses auto-merge), kill-switch tripped (nothing ships), thin spec (R6+R7 fail) |
| Operator surfaces work | kill-switch halts before spend; HITL inbox is the only merge path |

This is the **full composition chain** running end to end: M6 nodes → M7 governed fleet → M8 exam grades it.
Offline/stdlib-only, no cloud/GPU/Docker.
