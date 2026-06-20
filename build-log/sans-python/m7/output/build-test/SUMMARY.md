# M7 BUILD→TEST gate ledger — Module 7, Multi-Agent Artifacts

Each composition's scaffold was run **locally, offline, stdlib-only** (deterministic mocks; no Docker/cloud/GPU).
Re-run and confirmed by Opus. The smoke must prove a **team coordinates**, not a single agent.

| Artifact | `python smoke.py` | `python -m pytest tests/` | Team + operator surfaces proven |
|---|---|---|---|
| 01 autonomous-research-agent | exit 0 (supervisor plans 3 sub-questions → 3 sandboxed sub-agents → each verified → synthesized, shared budget) | **6 passed** | a supervisor + 3 sub-agents coordinate; unverified sub-result rejected; shared budget breach stops the team; kill-switch halts |
| 02 devops-k8s-agent | exit 0 (read-only diagnose → propose → HITL blocks auto-apply → approved apply → recovery, fully audited) | **6 passed** | supervisor + 3 read-only specialists; write attempt refused; HITL gate blocks unapproved change; approved change applies once + audited; kill-switch halts |
| 03 governed-multi-agent-fleet (FINALE) | exit 0 (architect→coders→reviewer→tester via A2A; HITL inbox approves merge; audit four clauses COMPLETE; $0.11/$1.00 team budget, per-agent) | **12 passed** | a governed 5-agent SWE team; per-agent AND team budget cap; HITL inbox blocks unapproved/off-channel merge; off-registry agent refused; audit answers which/authority/task/evidence; never auto-merges; kill-switch halts |

**Total: 3/3 smoke PASS, 24/24 tests PASS**, all offline/stdlib-only. Each artifact **composes** M6 nodes + M4
governance (imported, not rebuilt — verified in the verdicts). The finale is the governed fleet M8 operates.
