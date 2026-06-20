# Skill — Autonomous Research Agent

## What it proves

You can compose single agents into a governed team. A supervisor decomposes a
research question, sub-agents research each piece in isolated no-egress
sandboxes, a deterministic gate verifies every finding before it is used, and
the supervisor synthesizes a cited answer — the whole team under one shared cost
ceiling and a kill switch no agent can disable. It demonstrates that the
load-bearing engineering in a multi-agent system is the *governance* — the
verification gate, the shared budget, the kill switch — not the count of agents.

## What it does

Given a research question and an evidence corpus, the team:

1. **plans** — the supervisor decomposes the question into independent
   sub-questions (the ReWOO Planner: describe the work before any tool fires);
2. **dispatches** — runs one sub-agent per sub-question, each in a fresh context
   and its own sandbox, via direct tool calls (the M4 supervisor-worker fan-out —
   workers never see each other);
3. **verifies** — sends every finding through the verify gate; a finding enters
   the answer only when every citation it makes is grounded in evidence the
   sub-agent actually retrieved (the M3 CRITIC pattern — the verification gap closed);
4. **synthesizes** — the Solver stitches the *verified* findings into one cited
   answer, charging every model call to a **shared fleet budget** and reading a
   **kill switch** the operator owns before every action.

## How to invoke

```bash
python smoke.py            # the team on a fixed question with the deterministic mock
python -m pytest tests/    # the BUILD->TEST gate: composition + the operator surfaces
```

Offline, standard library + pytest. No API key, no Docker, no network.

## How to extend

- **Real model:** implement nothing new — `AnthropicLLM` in `client_llm.py`
  already wraps the Anthropic Messages API behind the same three seams the mock
  uses (`plan` / `respond` / `synthesize`). Install `anthropic`, set
  `ANTHROPIC_API_KEY`, swap `MockLLM()` for `AnthropicLLM()`.
- **Real retrieval:** replace the in-memory `ResearchSandbox.search` with a
  vetted index behind a read-only tool. The sub-agent reads `Evidence` records;
  the swap is local to one file, and the no-egress property is the contract.
- **Best-first tree search:** the capstone runs best-first search over candidate
  experiments. Here the plan is flat; make the supervisor expand a sub-question
  into follow-ups when a finding scores high, and the same gate/budget/kill
  surfaces govern the deeper tree.

## The portable seam

Three interfaces carry across every future build:

- **the model seam** — `plan` / `respond` / `synthesize` — makes the team
  model-agnostic;
- **the verification interface** — `verify(finding, evidence_ids) -> Verdict` —
  makes a finding's place in the answer a fact about grounded evidence, not a
  claim from the sub-agent;
- **the governance surfaces** — `FleetBudget`, `KillSwitch` — bound the team's
  cost and let an operator stop it.

## What M8 reuses

This team is a **node pattern** the Module 8 system points at a production
problem. The shape — *supervisor plans, sub-agents work in sandboxes, a gate
verifies each result, a shared budget and kill switch govern the whole* — is the
reusable unit. The finale fleet (M7 artifact 03) wires several such nodes under
one operator console; M8 configures the budget, holds the kill switch, reads the
verified/rejected split, and judges the synthesized answer against a rubric. The
verification gate is what makes that trustable: the report is built from grounded
findings, not promises.
