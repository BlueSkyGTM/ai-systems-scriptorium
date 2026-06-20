# Exercise 15 — The Workbench Surfaces II and the Pack

## Goal

Complete the workbench with verification, review, and handoff, then package all seven surfaces into `agent-workbench-pack/` — the drop-in artifact the M6 terminal coding agent imports.

## Why

Without verification and review, the agent grades its own work; without a handoff, every new session pays the full context-recovery cost. The pack turns seven surfaces into one installable artifact — and M6 imports it without rebuilding it.

## Steps

1. **Verification gate.** Implement `module3-agent/workbench/verify_agent.py` with a `verify(scope_report, rule_report, feedback_log, diff) -> dict` function. Run four block-severity checks: `scope_held` (scope report passed), `rules_passed` (rule report passed), `feedback_present` (feedback log non-empty), `acceptance_exit_zero` (last feedback record has `exit_code == 0`). Emit `.workbench/verification_report.json` with `{"verdict": "PASS"|"FAIL", "checks": [...], "blocked_by": [...]}`. Any block-severity failure sets verdict to `FAIL`.

2. **Reviewer rubric.** Write `module3-agent/docs/reviewer_checklist.md` defining five scoring dimensions (problem fit, scope discipline, assumptions, verification quality, handoff readiness) with a 0–2 scale description for each. Implement `module3-agent/workbench/reviewer.py` with a `review(diff, scope_report, verification_report, handoff) -> dict` function. Use `claude-haiku-4-5` as the judge model (it receives the rubric as the system prompt and the four artifacts as user content). Parse the response as JSON and emit `.workbench/review_report.json` with fields: `scores` (dict of dimension → int), `total`, `open_risks` (list of strings), `next_action` (string).

3. **Handoff generator.** Implement `module3-agent/workbench/generate_handoff.py` with a `generate(task_id, output_path) -> None` function. Read `agent_state.json`, `verification_report.json`, `review_report.json`, and `feedback_record.jsonl`. Produce a seven-field JSON packet: `task_id`, `summary`, `changed_files` (from `git diff --name-only <rollback_commit>`), `commands_run` (count), `failed_attempts` (list of `{argv, exit}` for non-zero exits), `open_risks`, `next_action`, `verdict_pointer` (path to `verification_report.json`).

4. **Integration run.** Write `module3-agent/workbench/integration_run.py`. It must: initialize state for a toy task; run two commands via `run_with_feedback` (one that succeeds, one that fails then a corrected retry); run `scope_checker`, `verify_agent`, `reviewer`, and `generate_handoff` in sequence; print the final verdict and the handoff `next_action` field.

5. **Assemble the pack.** Create `agent-workbench-pack/` at repo root with the folder layout from the lesson: `AGENTS.md`, `docs/` (agent-rules.md, reviewer_checklist.md), `schemas/` (both JSON Schemas), `scripts/` (all six Python scripts), `bin/install.sh`. The installer must be idempotent — running it twice on the same target produces no errors and no duplicate files.

6. **Prove the drop-in.** Run `bash agent-workbench-pack/bin/install.sh /tmp/test-repo` on a fresh directory. Confirm all files are present. Run `install.sh` a second time and confirm it prints "skipped (exists):" for each file.

## Done when

- `python integration_run.py` exits 0 and prints a `"verdict": "PASS"` line followed by a non-empty `next_action` string.
- A fabricated `scope_report.json` with `"passed": false` causes `verify_agent.py` to emit `"verdict": "FAIL"` and name `scope_held` in `blocked_by`.
- The reviewer loop produces a `review_report.json` with all five dimension keys present and scores in 0–2.
- `bin/install.sh` is idempotent: second run prints only "skipped (exists):" lines, no errors.
- `agent-workbench-pack/` contains all 11 files (AGENTS.md + 2 docs + 2 schemas + 6 scripts + install.sh).

## Stretch

Wire the verification verdict as a GitHub Actions gate: add `.github/workflows/agent-verify.yml` that reads `.workbench/verification_report.json` and exits non-zero if `verdict` is `"FAIL"`. Use `jq` to parse the file. The workflow should run on pull requests and block merge on failure. Use `claude-opus-4-8` as the builder model in the integration run's model call if you add one.
