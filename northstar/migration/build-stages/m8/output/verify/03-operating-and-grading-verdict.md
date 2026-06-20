# VERIFY verdict — 03-operating-and-grading.md

Subagent: Sonnet VERIFY (M8 capstone guides). Gate: guide prose (claims, STYLE, coherence).
This guide carries TWO of the three coherence checks: rubric==checker and runbook==surfaces.

## Coherence check (b) — RUBRIC == CHECKER

Guide table (03 lines 37–45) vs `rubric.py` `CRITERIA` tuple (lines 32–40). Same ids, same order, same intent:

| id | Guide "passes when" | rubric.py check | Match |
|----|---------------------|-----------------|-------|
| R1 RUNS | fleet shipped end to end (merge committed) | `exam.status == "merged"` | ✓ |
| R2 EVAL-GATED | merge passed tester ACCEPT and reviewer gate | `status=="merged" and merge_inbox_id is not None` (merge only proposed after both gates) | ✓ intent |
| R3 AUDITED | cross-agent audit answers all four clauses | `bool(clauses.get("complete"))` | ✓ |
| R4 BUDGET-BOUNDED | team spend within team cap; no per-agent breach | `status != "budget_breach" and cap>0 and spent<=cap` | ✓ |
| R5 HITL-GOVERNED | merge human-approved through inbox by id, never auto-merged | `bool(merge_approved_by) and merge_inbox_id is not None` | ✓ |
| R6 PROBLEM-FRAMED | spec names track, ref architecture, business problem | `spec.has_framing()` (track ∧ ref_arch ∧ business_problem) | ✓ |
| R7 TESTED+VERSIONED | spec declares acceptance criteria and a version | `spec.declares_tests() and spec.is_versioned()` | ✓ |

Guide's "deficient run fails the criterion it offends" examples (unapproved merge → R5+R1; trip kill switch →
whole run fails; thin spec → R6+R7) all hold against the code paths. The guide and rubric.py are one rubric in
two forms, and rubric.py's own docstring asserts the same. **PASS — no drift.**

## Coherence check (c) — RUNBOOK == REAL SURFACES

Against the shipped M7 fleet: `exercises/module7/03-governed-multi-agent-fleet/` (fleet.py, registry.yaml,
governance/{fleet_budget,inbox,audit,killswitch}.py).

- **Registry + dual budgets.** Guide: registry.yaml fields `id`/`owner`/`autonomy_tier`/`permissions`/
  `budget_daily_usd` + `team_daily_usd` + `fleet_gates: merge: human`; malformed entry fails schema first;
  budget caps two ways (per-agent + team). MATCHES registry.yaml exactly and FleetBudgetGuard (per-agent
  TaskBudget under team ceiling; charge raises on either wall). ✓
- **HITL inbox.** Guide: `fleet.inbox.pending()`, `fleet.inbox.approve(inbox_id, by=..., reason=...)`,
  `fleet.commit_merge(run, approver=...)`, `fleet.inbox.reject(...)`; approval with no named principal is
  refused; commit re-reads the gate. MATCHES inbox.py (pending/approve/reject/is_approved; `by` required →
  InboxError) and fleet.py commit_merge (re-reads `is_approved`). ✓
- **Audit four clauses.** Guide: `fleet.audit.answers_four_clauses(run.correlation_id)`; clauses
  which/authority/task/evidence threaded by one correlation id; `complete` True only when every record carries
  all four. MATCHES audit.py (answers_four_clauses + the `complete` boolean). ✓
- **Kill switch.** Guide: one file the operator owns, every loop reads, no agent can write; read-only boundary;
  exposed as `run_exam(spec, kill_first=True)`; live = `touch` on the registry's kill-switch path. MATCHES
  killswitch.py (KillSwitch.tripped() only; OperatorKillSwitch.engage/clear) + run_exam.py kill_first +
  registry.yaml `kill_switch: .FLEET_KILL`. ✓

**PASS — runbook matches the real surfaces.**

## Claim ledger
| # | Claim | Source | Result |
|---|-------|--------|--------|
| 1 | "the merge is the one irreversible action ... no agent may auto-execute" | registry (no can_merge:true); fleet.py (proposes, suspends) | VERIFIED |
| 2 | five-agent chain threaded by one correlation id | fleet.py (new_correlation_id, single corr through all A2A tasks) | VERIFIED |
| 3 | grade reproducible / computed, not judged | rubric.py grades captured ExamRun, never re-runs fleet | VERIFIED |
| 4 | distributed-systems vocab (load balancing, caching, sharding/federation, async/queues, CAP) assumed-not-taught, deviation D6 | standard CS definitions; D6 is internal-curriculum | VERIFIED (no external citation needed) |

No platform markers; no unsourced external claims. The vocabulary note is correctly framed as assumed
background with standard definitions, not as sourced external claims.

## STYLE result
- H1 `# Operating and Grading`. ✓  Seam lead: "The fleet ships the system. You run the fleet." — hooks, present, second person. ✓
- `## Core concepts` present (4 propositions). ✓
- Unity: second person + present tense throughout; no "we"/"the student". ✓
- HITL now expanded on first use in guide 01 (this guide reuses the established acronym). ✓
- "just this once" (line 19) is quoted dialogue — intentional, not a filler qualifier. ✓
- No banned template ending. Closer — aphorism: "Knowing the word is the floor; knowing which seam needs it is the job." — varied shape, lands. ✓

## FLAGGED
- None. (Note: guide writes `run_exam(spec, kill_first=True)`; the actual first positional param is
  `spec_path`. This is illustrative prose naming the arg generically — not a defect; left as-is.)

## VERDICT: PASS
Both coherence checks pass with no drift: the guide rubric is clause-for-clause the rubric.py checker, and the
operator runbook matches every real M7 surface (registry/dual-budgets, inbox four-move, audit four-clauses,
read-only kill switch). STYLE clean. No fixes required in this guide.
