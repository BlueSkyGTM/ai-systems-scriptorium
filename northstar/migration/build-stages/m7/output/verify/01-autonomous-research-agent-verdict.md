# VERIFY verdict — 01 Autonomous Research Agent

Artifact: `build-stages/m7/output/author/01-autonomous-research-agent.md`
Scaffold: `build-stages/m7/output/author/exercises/module7/01-autonomous-research-agent/`
Gate: GUIDE PROSE (claims + STYLE + guide-matches-scaffold). Code already passed BUILD→TEST.

## Verdict: **PASS** (no edits required to the guide; 0 markers; 0 defects)

---

## Markers resolved

The guide contains **no `[MS-Learn:]` / `[verify:]` / TODO markers** — it shipped clean.
The framing markers the task flagged were checked for *consistency*, not bracket-removal:

- **ReWOO / CRITIC / MAST framing** — consistent with the established M3/M4 usage. ReWOO
  is named as M3 plan-and-execute (Planner brackets a parallel middle, Solver synthesizes);
  CRITIC as M3 "route the check through an external signal the generator cannot hallucinate
  around"; MAST as Berkeley's multi-agent failure study where the verification gap is the
  largest cause after specification. No new unsourced claim is introduced. The MAST figures
  (spec ~42% / coord ~37% / verification ~21%) live only in the scaffold fixture
  (`corpus.py` S1), not as a load-bearing guide claim; the guide's softer statement
  ("largest single cause after specification") is consistent with that ordering.
- **Anthropic pricing / API claim** — the guide makes **no hardcoded pricing claim**. Its
  only Anthropic claim is the one-line model swap (mock → `AnthropicLLM`) opt-in via `.env`.
  Verified against the claude-api reference: current model is `claude-opus-4-8` (used
  consistently in `client_llm.py`), and Opus 4.8 pricing is $5/$25 per 1M tokens — which
  matches the `_PRICE_IN/_OUT` constants in `client_llm.py` ($5.00 / $25.00). The scaffold's
  `client_llm.py` carries its own `[verify: pricing]` author-notes, but those are CODE
  comments out of scope for guide-prose VERIFY; they are accurate as written.

## Guide-matches-scaffold confirmation

Every composition claim in the guide is present in the scaffold:

- **Sub-agent = M6 worker loop** → `subagent.py` (`run_subagent`): observe/think/act under
  shared budget + kill switch, one `search` tool, never self-verifies. ✔
- **Supervisor = M4 supervisor-worker, direct tool calls (no library)** → `supervisor.py`
  (`run_team`): plan → dispatch (fresh `ResearchSandbox` per sub-agent) → verify → synthesize. ✔
- **Planning = M3 ReWOO** → `mock_llm.plan()` / `synthesize()`; `client_llm` mirrors the seams. ✔
- **Verify gate = M3 CRITIC, deterministic, default REJECT** → `verify_gate.py`: accepts only
  when every `[S#]` citation is in retrieved `evidence_ids`; rejects empty / uncited /
  fabricated. ✔
- **Shared fleet budget** → `budget.py` (`FleetBudget`): one pool, `max_usd` + `max_calls`,
  per-agent ledger via `by_agent()`. ✔
- **Kill switch, read-only to agents** → `killswitch.py`: agents get `KillSwitch` (read-only
  `tripped()`); only `OperatorKillSwitch` writes. ✔
- **Operator surfaces** (shared budget / per-result verification gate / kill switch) and
  **BUILD→TEST claims** (composition completes as a team; unverified finding rejected; fleet
  budget breach stops the team; kill switch halts) all map to `tests/test_smoke.py`. ✔
- File names referenced in the handoff and tables (`supervisor.py`, `subagent.py`,
  `sandbox.py`, `verify_gate.py`, `budget.py`, `killswitch.py`, `mock_llm.py`,
  `client_llm.py`, `corpus.py`, `smoke.py`, `tests/`,
  `outputs/skill-autonomous-research-agent.md`) all exist. ✔
- `data-exercise="exercises/module7/01-autonomous-research-agent/"` resolves. ✔

## STYLE result (full read)

- H1 present ("# The Autonomous Research Agent"). ✔
- Seam lead: opens on the business problem (lone agent grades its own homework), pulls the
  reader in; no throat-clearing. ✔
- `## What you build` + `## Core concepts` present, in order, immediately before the handoff. ✔
- `claude-handoff` div present, correct `data-exercise`, opens and closes. ✔
- Acronyms expanded / glossed (MAST, ReWOO, CRITIC carried from earlier modules; second
  person, present tense throughout). ✔
- No banned template ending — "What M8 reuses" closes on a node-pattern reframe, not the
  banned "An AI Platform Engineer who…" opener. ✔
- Core concepts are propositions, not terms. ✔

## Defects fixed
None. Guide was already clean and accurate.

## FLAGGED (non-blocking)
- The MAST quantitative split (42/37/21) appears in the scaffold fixture `corpus.py`, framed
  as "Cemri et al., 2025." The guide does not assert these numbers, so no guide-prose action;
  noted only so a future fact-check of the *scaffold* knows where the figure lives.
