# Exercise 14 — The Workbench Surfaces I

## Goal

Add the first four workbench surfaces to `module3-agent/workbench/`: an `AGENTS.md` router, machine-checkable rules, a durable state layer under JSON Schema, a per-task scope contract with a diff checker, and a feedback runner that wraps every shell command.

## Why

A capable model dropped into a real repo without these surfaces has no idea what "done" means, where it can write, or whether its commands actually ran — this is the gap between a demo and a shippable agent.

## Steps

1. **Instructions.** Create `module3-agent/AGENTS.md` (one screen: repo name, entry point, test command, pointers to rules/state/board). Create `module3-agent/docs/agent-rules.md` with all five sections: Startup, Forbidden, Definition-of-done, Uncertainty, Approval. At least two rules per section.

2. **State schemas.** Write `module3-agent/workbench/schemas/agent_state.schema.json` and `task_board.schema.json` (JSON Schema draft 2020-12). `agent_state` must have required fields: `task_id` (string), `status` (enum: `idle | active | blocked | done`), `rollback_commit` (string), `task_summary` (string). `task_board` must have a `tasks` array with per-task `id`, `status`, `owner`, `created_at`.

3. **StateManager.** Implement `module3-agent/workbench/state_manager.py` with `load()` (validates on read) and `save(data)` (validates then atomic write via `.tmp` + `os.replace`). Raise `jsonschema.ValidationError` on any schema violation — never silently corrupt state.

4. **Scope contract.** Write a sample `module3-agent/workbench/sample_scope_contract.json` for a toy task (two allowed files, two forbidden glob patterns, two acceptance criteria, a rollback commit of `HEAD~1`). Implement `module3-agent/workbench/scope_checker.py` with a `check(contract_path) -> dict` function that runs `git diff --name-only <rollback_commit>`, compares against allowed/forbidden, and writes `.workbench/scope_report.json` with `{"task_id": ..., "violations": [...], "passed": bool}`.

5. **Feedback runner.** Implement `module3-agent/workbench/run_with_feedback.py` with a `run(argv, log_path, agent_note="") -> dict` function. Persist one JSON line per call to `log_path` with fields: `argv`, `exit_code`, `stdout_tail` (last 2000 chars), `stderr_tail` (last 500 chars), `duration_ms`, `agent_note`. Return the record.

6. **Smoke test.** Write `module3-agent/workbench/smoke_test_surfaces_i.py`. It must: initialize state with `StateManager`, write a valid `agent_state.json`; run `echo hello` through `run_with_feedback` and confirm the record has `exit_code: 0`; run the scope checker against the sample contract; print a one-line PASS/FAIL summary for each surface.

## Done when

- `python smoke_test_surfaces_i.py` exits 0 and prints four PASS lines.
- Deliberately writing an invalid field to `agent_state.json` via `StateManager.save()` raises `jsonschema.ValidationError`.
- Running `scope_checker.py` with a diff that includes a forbidden file produces `"passed": false` and names the violation.
- The `feedback_record.jsonl` produced by the smoke test contains one line with `exit_code: 0` and a non-zero `duration_ms`.

## Stretch

Write a `rule_checker.py` that reads `docs/agent-rules.md`, confirms all five section headings are present, and emits `rule_report.json` — a dict of `{"section": ..., "rule_count": ..., "passed": bool}` per section. Wire it into the smoke test as a fifth PASS check.
