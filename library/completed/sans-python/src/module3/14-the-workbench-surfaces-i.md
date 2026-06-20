# The workbench surfaces I: instructions, state, scope, feedback

Drop a frontier model into a real repo and it fails — not on the language, but on the work. It has no idea what "done" means, where it can write, or which tests are authoritative. The workbench fixes that. Swap the model and keep the surfaces; never the reverse.

## What you build

You build the first four of seven workbench surfaces inside `module3-agent/workbench/`: an `AGENTS.md` router, a machine-checkable rules file, a durable state layer under JSON Schema, a per-task scope contract, a scope checker, and a feedback runner. Each surface is a Python script or a structured file the agent reads at every turn.

## Instructions: the router and the rules

The agent's first read is `AGENTS.md`. Keep it short — one screen. A long manual no one reads; a short router they actually follow. The router names the repo, the entry point, the test command, and a pointer to `docs/agent-rules.md`. That's it.

```
# AGENTS.md
repo: acme-api
entry: src/main.py
test: pytest -x -q
rules: docs/agent-rules.md
state: .workbench/agent_state.json
board: .workbench/task_board.json
```

`docs/agent-rules.md` is where the actual constraints live — away from the root, versioned alongside the code. Organize it under five headings the workbench checks at runtime:

| Section | Example rule |
|---------|-------------|
| **Startup** | Load state before the first tool call. Fail loud if state is absent. |
| **Forbidden** | Never write to `README.md`, `scripts/release.sh`, or any file outside `src/`. |
| **Definition-of-done** | All acceptance tests pass. Scope report shows no creep. Verification verdict is PASS. |
| **Uncertainty** | Stop and emit a structured question. Do not guess. |
| **Approval** | Any write to a file in `db/migrations/` requires a human approval step. |

Prose wishes ("be careful," "test thoroughly") have no runtime teeth. Machine-checkable rules do. A `rule_checker.py` reads the rules file and emits a diff-friendly `rule_report.json` the verification step reads — turning your intentions into a ledger.

Azure AI Foundry's [Task Adherence](https://learn.microsoft.com/azure/ai-services/content-safety/concepts/task-adherence) signal detects when a planned tool invocation deviates from the user's intent — the runtime counterpart to the rule ledger you maintain locally.

## State: the repo is the system of record

Chat is volatile. When the session ends, the agent loses everything — unless you wrote it down somewhere that survives. The repo is that place.

Two files carry all durable state:

```
.workbench/
  agent_state.json   # current task, last-known-good commit, active flags
  task_board.json    # queue of tasks, status per task, owner, timestamps
```

Both live under a JSON Schema so a bad write is caught before it corrupts the workbench. The `StateManager` loads, validates, mutates, and persists atomically — it writes to a `.tmp` file first, then renames it, so a crash mid-write leaves the prior state intact.

```python
# module3-agent/workbench/state_manager.py
import json, os, tempfile
import jsonschema

class StateManager:
    def __init__(self, state_path: str, schema_path: str):
        self.state_path = state_path
        self.schema = json.loads(open(schema_path).read())

    def load(self) -> dict:
        with open(self.state_path) as f:
            data = json.load(f)
        jsonschema.validate(data, self.schema)
        return data

    def save(self, data: dict) -> None:
        jsonschema.validate(data, self.schema)          # validate before write
        dir_ = os.path.dirname(self.state_path)
        with tempfile.NamedTemporaryFile("w", dir=dir_, delete=False, suffix=".tmp") as tmp:
            json.dump(data, tmp, indent=2)
            tmp_path = tmp.name
        os.replace(tmp_path, self.state_path)           # atomic rename
```

The schema enforces the shape — required fields, types, enum values — so state drift is a loud error, not a silent corruption. Every field is diff-friendly: git history becomes a complete audit of what the agent believed at each step.

A task that spans three sessions costs nothing extra. The next session reads state, not chat history, and picks up where the prior one stopped.

In CI, the same JSON files become pipeline artifacts. Azure Pipelines' [PublishPipelineArtifact](https://learn.microsoft.com/azure/devops/pipelines/artifacts/pipeline-artifacts?view=azure-devops) task lets a later stage download exactly the state a prior stage wrote — the same cross-session contract, scaled to a build system.

## Scope: the contract that prevents creep

Scope creep is the most under-monitored single-agent failure mode. The agent sets out to add a validation function and ends up touching the ORM layer, the migration scripts, and three unrelated tests. Each change looked locally reasonable. Together they make review impossible.

A `scope_contract.json` is created fresh for each task, before the agent starts:

```json
{
  "task_id": "task-042",
  "allowed_files": ["src/validators.py", "tests/test_validators.py"],
  "forbidden_files": ["README.md", "scripts/release.sh", "db/migrations/**"],
  "acceptance_criteria": [
    "pytest tests/test_validators.py -q passes with exit 0",
    "No new imports outside stdlib and project deps"
  ],
  "rollback_commit": "a3f9c12"
}
```

The `scope_checker.py` runs after the agent finishes. It compares the actual git diff against the contract and flags any file touched that wasn't in `allowed_files`, plus any `forbidden_files` path that appears in the diff:

```python
# module3-agent/workbench/scope_checker.py
import subprocess, json, fnmatch

def check(contract_path: str) -> dict:
    contract = json.load(open(contract_path))
    diff_files = subprocess.check_output(
        ["git", "diff", "--name-only", contract["rollback_commit"]]
    ).decode().split()

    allowed  = set(contract["allowed_files"])
    forbidden = contract["forbidden_files"]

    violations = []
    for f in diff_files:
        if f not in allowed:
            violations.append({"file": f, "reason": "not in allowed_files"})
        for pattern in forbidden:
            if fnmatch.fnmatch(f, pattern):
                violations.append({"file": f, "reason": f"matches forbidden pattern {pattern}"})

    return {"task_id": contract["task_id"], "violations": violations, "passed": not violations}
```

The report goes to `.workbench/scope_report.json`. Downstream, the verification gate reads it. A violation blocks the verdict. The agent cannot edit the scope contract — only you can.

Azure's [AI-4 security guidance](https://learn.microsoft.com/security/benchmark/azure/mcsb-v2-artificial-intelligence-security#ai-4-apply-least-privilege-for-agent-functions) frames the same principle at the platform layer: define a capability manifest that allows only the tools the agent needs, apply RBAC, and audit every invocation. The scope contract is the local expression of that posture.

## Feedback: react to facts, not predictions

The most common single-agent lie: "all tests pass." Said with no record. No log. No exit code. Just the model's confident prediction of what probably happened when it called `pytest`.

`run_with_feedback.py` wraps every shell command and persists a structured record:

```python
# module3-agent/workbench/run_with_feedback.py
import subprocess, time, json

def run(argv: list[str], log_path: str, agent_note: str = "") -> dict:
    t0 = time.monotonic()
    result = subprocess.run(argv, capture_output=True, text=True)
    duration_ms = int((time.monotonic() - t0) * 1000)

    record = {
        "argv":        argv,
        "exit_code":   result.returncode,
        "stdout_tail": result.stdout[-2000:],   # deterministic truncation
        "stderr_tail": result.stderr[-500:],
        "duration_ms": duration_ms,
        "agent_note":  agent_note,
    }

    with open(log_path, "a") as f:
        f.write(json.dumps(record) + "\n")

    return record
```

The agent calls `run_with_feedback` for every command — `pytest`, `ruff check`, `git diff`, anything. The record goes to `.workbench/feedback_record.jsonl`. The loop reads the actual `exit_code` back into its context before the next reasoning step.

The loop refuses to mark a task complete if the feedback log is empty. "Tests pass" backed by a `feedback_record.jsonl` entry with `exit_code: 0` is a fact. "Tests pass" with no record is a hallucination. You enforce the difference at the loop level, not the prompt level.

Azure Pipelines surfaces the same discipline at scale: the [Publish Pipeline Artifacts](https://learn.microsoft.com/azure/devops/pipelines/artifacts/pipeline-artifacts?view=azure-devops) task and stage [gates](https://learn.microsoft.com/azure/devops/pipelines/release/approvals/gates?view=azure-devops) let downstream stages read the feedback log before they advance — the same "no record, no pass" rule enforced by the pipeline itself.

## The thread so far

Instructions constrain what the agent may do. State makes multi-session work cheap. Scope locks the blast radius. Feedback anchors every claim to a real execution record. Together the four surfaces turn a capable model into a predictable one — without changing the model at all.

The next lesson adds the three surfaces that close the loop: verification (the agent doesn't grade its own work), review (a second loop catches what verification misses), and handoff (the capstone that packages all seven into the `agent-workbench-pack/` the M6 coding agent imports).

## Core concepts

- A short `AGENTS.md` router plus machine-checkable `docs/agent-rules.md` rules outperform a long manual because the agent reads the router every turn and the workbench enforces the rules as a ledger, not prose.
- Durable state lives in the repo as JSON Schema-validated files written atomically; chat history is volatile and survives nothing.
- A per-task `scope_contract.json` combined with a post-run `scope_checker.py` diff is the only reliable defense against scope creep — the most under-monitored single-agent failure mode.
- `run_with_feedback.py` turns every shell command into a persisted fact (argv, exit code, stdout tail, duration); a loop that refuses to advance without a feedback record eliminates "all tests pass" with no evidence.

<div class="claude-handoff" data-exercise="exercises/module3/14-the-workbench-surfaces-i/">

**Build It in Claude Code** — add the first four workbench surfaces to `module3-agent/workbench/`: write `AGENTS.md` and `docs/agent-rules.md` with all five rule sections; implement `StateManager` with atomic writes and JSON Schema validation for `agent_state.json` and `task_board.json`; implement `scope_checker.py` that diffs against a `scope_contract.json` and emits `scope_report.json`; implement `run_with_feedback.py` that wraps a subprocess and appends to `feedback_record.jsonl`. A smoke-test script must run all four surfaces against a sample task and print a summary.

</div>
