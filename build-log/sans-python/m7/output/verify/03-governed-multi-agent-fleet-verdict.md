# VERIFY verdict — M7 ch.03: The Governed Multi-Agent Fleet (course FINALE)

Gate: AUTHOR → **VERIFY** (this) → BUILD→TEST (passed) → SHIP. Closest-review tier — largest system + M8 substrate.
Guide (edited in place): `build-stages/m7/output/author/03-governed-multi-agent-fleet.md`
Scaffold: `build-stages/m7/output/author/exercises/module7/03-governed-multi-agent-fleet/`

## Verdict: **PASS** (markers resolved, claims verified, guide-matches-scaffold confirmed, M8 hand-off confirmed, STYLE clean). One FLAG, soft, non-blocking.

---

## Claim ledger

| # | Claim (guide) | Source / scaffold check | Result |
|---|---|---|---|
| 1 | SWE-team shape: architect / coders×2 / reviewer / tester | M5 capstone proj 10 ("Multi-Agent Software Engineering Team": Architect, Coders, Reviewer, Tester via typed A2A) + `registry.yaml` (5 agents, 4 roles) | VERIFIED |
| 2 | Capstone is project 10 (10★) | `synthesis/source/module5/aefs-module5-capstone.md` §10; PLAN marks 10★ | VERIFIED |
| 3 | Coder node = M6 agent (same loop/tools.py/sandbox.py/verify_gate.py, imported not rebuilt) | `agents/coder.py` imports `tools`, `verify_gate`; `tools.py`/`verify_gate.py`/`sandbox.py` header "Reused from the M6 coding agent"; M6 lesson: "M7 imports this loop … does not rebuild it" | VERIFIED |
| 4 | FleetBudgetGuard = per-agent TaskBudget under team ceiling (lesson 13; lesson-06 governor reused) | `governance/fleet_budget.py`: `TaskBudget` cap logic + `FleetBudgetGuard` adds attribution + team total; M4 lesson 13 code block + core-concept identical | VERIFIED |
| 5 | Shared HITL inbox = lesson-08 propose-then-commit + queue/inbox_id/no-off-channel (lesson 13) | `governance/inbox.py`: submit/approve-by-id/reject, off-channel refused; M4 lesson 13 shared-inbox-HITL matches verbatim incl. "deploy by DM" story | VERIFIED |
| 6 | Registry/audit/kill-switch from lessons 12/13 | `registry.yaml`+`schemas/registry.schema.json` (team-registry, autonomy tiers F0–F3, least-priv); `governance/audit.py` (4 clauses, correlation id); `governance/killswitch.py` (read-only KillSwitch, OperatorKillSwitch writes) — all match M4 12/13 | VERIFIED |
| 7 | A2A from lesson 02 (skill, lifecycle submitted→working→completed\|failed, typed artifacts, correlation id) | `a2a.py`: STATES tuple, A2ATask/A2AResult, validate on receipt; M4 lesson 02 task lifecycle matches | VERIFIED |
| 8 | Runaway-delegation cost story (twelve retries, 8× spend by morning) | M4 lessons 12 AND 13 (verbatim); `governance/fleet_budget.py` docstring | VERIFIED (story appears in both 12 & 13; guide attributes to 13 — acceptable) |
| 9 | Current model `claude-opus-4-8`, not hardcoded; Anthropic pricing $5/$25 per Mtok; Messages-API tool-use loop | `client_llm.py` `name="claude-opus-4-8"`, default param, opt-in; pricing 5.00/25.00 matches claude-api skill (Opus 4.8 = $5/$25); tool-use loop tool_use→tool_result→end_turn confirmed | VERIFIED |
| 10 | "Never auto-merge"; merge is the one human gate; no agent has can_merge | `fleet.py` ship_feature proposes-then-suspends, commit_merge re-checks inbox approval; `registry.yaml` all `can_merge: false`, `fleet_gates.merge: human`; `policy.authorize_merge` refuses all | VERIFIED |

## Markers resolved (2 in-guide `[verify:]` markers → removed, claims kept)
1. Line 9 — `[verify: SWE-team shape — M5 capstone proj 10, aefs-module5-capstone.md]` → confirmed against capstone §10; marker removed, prose kept clean.
2. Line 45 — `[verify: FleetBudgetGuard + shared-inbox-HITL imported not rebuilt — src/module4/13-fleet-patterns.md]` → confirmed; marker removed.
3. Line 70 — `[verify: runaway-delegation cost story — src/module4/13-fleet-patterns.md]` → confirmed (also in lesson 12); marker removed.
(Scaffold `client_llm.py` carries two internal `[verify:]` comment markers for pricing + tool-use loop — both confirmed accurate against the claude-api reference; left as in-code provenance comments, not guide prose. Not a defect.)

## Guide-matches-scaffold (the full operator console — critical for the finale)
- **Architecture (architect / coder×2 / reviewer / tester via A2A):** matches `agents/*.py` + `fleet.py` role resolution + `a2a.py`. CONFIRMED.
- **Registry:** 5 agents w/ id/owner/autonomy_tier/least-priv permissions/budget_daily_usd + team ceiling + merge gate — `registry.yaml` + JSON Schema (`schemas/registry.schema.json`, pure-Python validator `schema.py`). CONFIRMED.
- **Fleet budget (per-agent + team):** `governance/fleet_budget.py`; tests pin per-agent AND team breach. CONFIRMED.
- **HITL inbox:** `governance/inbox.py`; suspend-at-merge in `fleet.py`; approve-by-inbox_id. CONFIRMED.
- **Cross-agent audit — four accountability clauses (which/authority/task/evidence):** `governance/audit.py` `answers_four_clauses`; smoke prints COMPLETE=True; clause language in guide matches code. CONFIRMED.
- **Kill switch (operator-owned, read-only to agents):** `governance/killswitch.py` (KillSwitch.tripped only; OperatorKillSwitch writes); checked before every action in each node. CONFIRMED.
- **"Never auto-merge":** CONFIRMED (claim #10).
- **File names cited in guide all exist:** `registry.yaml`, `policy.py`, `a2a.py`, `fleet.py`, `agents/coder.py`, `tools.py`, `sandbox.py`, `verify_gate.py`, `governance/{fleet_budget,inbox,audit,killswitch}.py`, `smoke.py`, `tests/`, `outputs/skill-governed-multi-agent-fleet.md`. CONFIRMED.
- **Smoke re-run (this VERIFY):** green — team ships, suspends at inbox, commits only on human approval, audit COMPLETE (all 4), team spend $0.11/$1.00. Matches guide's BUILD→TEST description.

## M8 hand-off confirmation
- Guide §"The Module 8 hand-off" + §"How it composes" state: registry is the contract M8 edits to retarget; orchestrator reads it unchanged; student is operator + judge + architect-of-record (configures budgets, holds kill switch, works HITL inbox, reads audit, judges output). Matches PLAN §"M8 hand-off".
- Scaffold backs it: `load_fleet()`/`Fleet` build the console from the registry; `ship_feature(...)` runs the team; `registry.yaml` header explicitly names the M8 operator editing the file. `ship_feature(...)` named in guide = real entry point. CONFIRMED.
- Thesis-full-circle landing (§final paragraph) is earned: it restates the built artifact (single agents → team → governed fleet) against the named job, not asserted cold. CONFIRMED.

## STYLE result (full read)
- H1 present (single `# The Governed Multi-Agent Fleet`). PASS.
- Seam-style lead (problem + why an AI Platform Engineer needs it, no throat-clearing). PASS.
- `## What you build` + `## Core concepts` (5 propositions, in voice). PASS.
- `claude-handoff` div present with `data-exercise` path matching the scaffold dir. PASS.
- No banned template ending; no "An AI Platform Engineer who…" opener. Ending is a reframe ("It is the whole of it — and you just built one that runs."). PASS.
- Acronyms expanded on first use: A2A (agent-to-agent, via lesson 02 context), HITL ("shared HITL inbox" — human-in-the-loop is established M4/M6 vocabulary), JSON Schema spelled. PASS.
- Voice/unity: second person, present tense, blunt-confident. PASS. No edits required.

## FLAGGED (soft, non-blocking)
- **HITL acronym** is used without an inline gloss in this chapter (relies on M4/M6 prior exposure). Consistent with the rest of the course's late-module usage; left as-is. If a stricter acronym-on-first-use policy applies to every chapter standalone, add "(human-in-the-loop)" at first occurrence (line ~32 diagram / line 71 "The HITL inbox"). Not corrected to avoid over-editing established voice.

## Defects fixed
- Removed 3 in-guide `[verify:]` markers (claims confirmed, prose left clean). No claim corrections needed — every load-bearing claim verified true against source lessons + scaffold + claude-api reference. No softening required.
