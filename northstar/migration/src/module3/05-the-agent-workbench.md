# The Agent Workbench

> **Migrated from** `aefs-module3-agent-engineering` (Ph14 31–42). A single-agent **operational** thread —
> the surfaces that decide whether an agent ships. **Seeds the M6 terminal coding-agent artifact.**

The insight: a frontier model dropped into a real repo fails not on the language but on *the work* — no idea
what "done" means, where it can write, which tests are authoritative. The workbench is **model-independent**:
swap the model and keep the surfaces, but not the reverse.

## The seven surfaces

1. **Instructions** — a short `AGENTS.md` router (not a 3000-line manual) + `docs/agent-rules.md` as
   machine-checkable rules (Startup / Forbidden / Definition-of-done / Uncertainty / Approval).
2. **State** — the repo is the system of record, chat is volatile: `agent_state.json` + `task_board.json`
   under JSON Schema, persisted atomically, diff-friendly. Survives multi-session work without chat history.
3. **Scope** — a per-task `scope_contract.json` (allowed/forbidden files, acceptance criteria, rollback);
   a `scope_checker.py` compares the final diff and flags creep — the most under-monitored failure mode.
4. **Feedback** — `run_with_feedback.py` wraps every command, persisting argv / stdout-tail / exit code /
   duration so the agent reacts to facts, not its prediction of facts. Kills "all tests pass" with no record.
5. **Verification** — the agent does not mark its own work done: a deterministic `verify_agent.py` reads
   scope/rules/feedback/diff and emits one verdict that CI and the reviewer both read.
6. **Review** — a second loop with a different prompt and read-only access scores a five-dimension rubric
   (problem fit, scope discipline, assumptions, verification quality, handoff readiness). Catches "solved the
   wrong half of the bug."
7. **Handoff** — `generate_handoff.py` turns an hour of work into a productive next session: summary,
   changed files, commands run, failed attempts, open risks, next action, verdict pointer.

## The capstone

Package the seven surfaces into a drop-in `agent-workbench-pack/` (AGENTS.md + schemas + scripts +
`bin/install.sh`) that lays into any repo idempotently. Proven on a real FastAPI app (prompt-only vs
workbench-guided, measured). **This pack is the foundation of the M6 coding agent.**
