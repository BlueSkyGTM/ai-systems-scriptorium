# The Workbench Surfaces II: Verification, Review, Handoff — and the Pack

The previous four surfaces constrain the agent and capture facts. These three close the loop: the agent does not grade its own work, a second loop catches what verification misses, and a handoff packet makes the next session productive from its first minute. Then you package all seven into the artifact M6 imports.

## What you build

You build the final three surfaces — `verify_agent.py`, a reviewer loop, and `generate_handoff.py` — then package all seven surfaces into a drop-in `agent-workbench-pack/` that installs into any repo with a single script. That pack is the foundation of the M6 terminal coding agent; M6 imports it, not rebuilds it.

## Verification: the agent does not mark its own work done

An agent that decides it is finished is not done — it is optimistic. Self-grading is structurally unreliable: the agent generated the code, predicted the tests would pass, and now evaluates whether its prediction was correct. That is not verification; it is a second guess.

`verify_agent.py` is a deterministic program — no model, no judgment — that reads four artifacts and emits one verdict:

```python
# module3-agent/workbench/verify_agent.py
import json, sys

def verify(scope_report: str, rule_report: str, feedback_log: str, diff: str) -> dict:
    scope  = json.load(open(scope_report))
    rules  = json.load(open(rule_report))
    checks = []

    # Block: scope must have passed
    checks.append({
        "name": "scope_held",
        "passed": scope["passed"],
        "severity": "block",
        "detail": scope.get("violations", []),
    })

    # Block: rules must have passed
    checks.append({
        "name": "rules_passed",
        "passed": rules["passed"],
        "severity": "block",
        "detail": rules.get("failures", []),
    })

    # Block: feedback log must be non-empty (commands actually ran)
    with open(feedback_log) as f:
        records = [json.loads(l) for l in f if l.strip()]
    checks.append({
        "name": "feedback_present",
        "passed": bool(records),
        "severity": "block",
        "detail": "No commands recorded in feedback log." if not records else "",
    })

    # Block: last acceptance command must have exited 0
    if records:
        last_exit = records[-1]["exit_code"]
        checks.append({
            "name": "acceptance_exit_zero",
            "passed": last_exit == 0,
            "severity": "block",
            "detail": f"Last command exited {last_exit}",
        })

    blocked = [c for c in checks if c["severity"] == "block" and not c["passed"]]
    verdict  = "PASS" if not blocked else "FAIL"

    return {"verdict": verdict, "checks": checks, "blocked_by": [c["name"] for c in blocked]}
```

The output goes to `.workbench/verification_report.json`. CI reads the same file. The human reviewer reads the same file. One source of truth — no ambiguity about whether "the agent said it was done" and "the verification passed" mean the same thing.

Wire the verdict as a CI gate: a GitHub Actions step that reads `verification_report.json` and exits non-zero on `"verdict": "FAIL"` means a failed agent cannot merge.

Azure Pipelines makes this a native step: [deployment gates](https://learn.microsoft.com/azure/devops/pipelines/release/approvals/gates?view=azure-devops) let you configure pre-deployment conditions that read an external source — including a REST API that returns your `verification_report.json` — and block stage promotion until the signal is green.

Azure AI Foundry's [agent evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators#system-evaluation) — Task Adherence, Task Completion, Intent Resolution — operate on the same principle at the platform layer: structured scores per run, integrated into the CI/CD pipeline via the [AI Agent Evaluation extension](https://learn.microsoft.com/azure/foundry/how-to/evaluation-azure-devops) for Azure DevOps.

## Review: a second loop with a different prompt

Verification is deterministic and fast. It cannot catch "solved the wrong half of the bug" — a task where every check passes but the solution misunderstands the problem. That is what the reviewer catches.

The reviewer is a second agent loop, a different system prompt, and read-only access to everything the builder produced. It cannot write files. It reads the diff, the scope contract, the verification report, and the handoff, then scores five dimensions:

| Dimension | Question |
|-----------|----------|
| **Problem fit** | Does the diff address the stated task, or a simpler adjacent task? |
| **Scope discipline** | Did the agent stay within the contract? (Redundant check; the reviewer should agree with the verifier.) |
| **Assumptions** | What did the agent assume that isn't in the rules? Are those assumptions sound? |
| **Verification quality** | Did the acceptance commands test the right thing, or just run without failing? |
| **Handoff readiness** | Could a new session start productively from the handoff packet alone? |

Each dimension scores 0–2. The rubric is in `docs/reviewer_checklist.md`. The reviewer loop emits `review_report.json`:

```python
# module3-agent/workbench/reviewer.py  (sketch — full loop in exercise)
import anthropic, json

REVIEWER_PROMPT = open("docs/reviewer_checklist.md").read()

def review(diff: str, scope_report: str, verification_report: str, handoff: str) -> dict:
    client = anthropic.Anthropic()
    payload = f"DIFF:\n{diff}\n\nSCOPE:\n{scope_report}\n\nVERIFY:\n{verification_report}\n\nHANDOFF:\n{handoff}"

    response = client.messages.create(
        model="claude-haiku-4-5",         # cheap pass for rubric scoring
        max_tokens=1024,
        system=REVIEWER_PROMPT,
        messages=[{"role": "user", "content": payload}],
    )
    return json.loads(response.content[0].text)
```

Use `claude-haiku-4-5` for the rubric-scoring pass — it is fast and cheap, and the rubric constrains the judgment enough that a smaller model is reliable. Reserve `claude-opus-4-8` for the builder loop where reasoning depth matters.

The reviewer cannot be the builder. Run them as separate processes with separate prompts. An agent that reviews its own code consistently scores it higher than a second agent does — because it is still executing the same goal.

Azure AI Foundry's [rubric evaluators](https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators) work the same way at scale: define weighted dimensions, set a pass threshold (0.0–1.0), and let the LLM judge score every response. The five-dimension reviewer rubric here follows the same pattern — portable to Foundry once you graduate beyond the single agent.

## Handoff: turn an hour into a productive next minute

A handoff packet exists because the next session starts cold. Without one, the new session probes the repo, reads the diff, guesses at what was tried, and wastes the first ten minutes reconstructing context the prior session held.

`generate_handoff.py` reads the workbench artifacts and writes a structured packet — not a long narrative, a short one with seven fields:

```python
# module3-agent/workbench/generate_handoff.py
import json, subprocess

def generate(task_id: str, output_path: str) -> None:
    state   = json.load(open(".workbench/agent_state.json"))
    verify  = json.load(open(".workbench/verification_report.json"))
    review  = json.load(open(".workbench/review_report.json"))
    records = [json.loads(l) for l in open(".workbench/feedback_record.jsonl") if l.strip()]

    changed = subprocess.check_output(
        ["git", "diff", "--name-only", state["rollback_commit"]]
    ).decode().split()

    failed_cmds = [r for r in records if r["exit_code"] != 0]

    packet = {
        "task_id":        task_id,
        "summary":        state.get("task_summary", ""),
        "changed_files":  changed,
        "commands_run":   len(records),
        "failed_attempts": [{"argv": r["argv"], "exit": r["exit_code"]} for r in failed_cmds],
        "open_risks":     review.get("open_risks", []),
        "next_action":    review.get("next_action", ""),
        "verdict_pointer": ".workbench/verification_report.json",
    }

    with open(output_path, "w") as f:
        json.dump(packet, f, indent=2)
```

The packet makes the next session's first action deterministic. A session that starts by reading `handoff.json` recovers in under a minute; a session that starts from scratch pays five to ten minutes every time, for the life of the task.

## The capstone: `agent-workbench-pack/`

The seven surfaces exist in `module3-agent/workbench/`. Now package them so any repo can adopt them without rebuilding from scratch.

```
agent-workbench-pack/
├── AGENTS.md                          # the router template
├── docs/
│   ├── agent-rules.md                 # five-section rules template
│   └── reviewer_checklist.md          # five-dimension rubric
├── schemas/
│   ├── agent_state.schema.json        # JSON Schema for agent_state.json
│   └── task_board.schema.json         # JSON Schema for task_board.json
├── scripts/
│   ├── state_manager.py
│   ├── scope_checker.py
│   ├── run_with_feedback.py
│   ├── verify_agent.py
│   ├── reviewer.py
│   └── generate_handoff.py
└── bin/
    └── install.sh                     # idempotent installer
```

`bin/install.sh` copies the pack into the target repo without overwriting files that already exist — idempotent, so running it twice is safe:

```bash
#!/usr/bin/env bash
set -euo pipefail
PACK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-.}"

install_file() {
    local src="$PACK_DIR/$1"
    local dst="$TARGET/$1"
    mkdir -p "$(dirname "$dst")"
    if [ ! -f "$dst" ]; then
        cp "$src" "$dst"
        echo "installed: $dst"
    else
        echo "skipped (exists): $dst"
    fi
}

install_file "AGENTS.md"
install_file "docs/agent-rules.md"
install_file "docs/reviewer_checklist.md"
install_file "schemas/agent_state.schema.json"
install_file "schemas/task_board.schema.json"
install_file "scripts/state_manager.py"
install_file "scripts/scope_checker.py"
install_file "scripts/run_with_feedback.py"
install_file "scripts/verify_agent.py"
install_file "scripts/reviewer.py"
install_file "scripts/generate_handoff.py"
```

The pack is model-independent. The scripts never call a model; the reviewer loop takes a model name as a parameter. Swap `claude-haiku-4-5` for anything else — the workbench doesn't care.

**This pack is the foundation of the M6 terminal coding agent.** The M6 agent imports `agent-workbench-pack/` on initialization and does not rebuild it. The schemas, scripts, and rules it installs are the exact ones you authored here — locked, versioned, tested. The capstone exercise produces the artifact; M6 picks it up. Nothing is rebuilt; everything compounds.

Azure Pipelines' [approvals and checks](https://learn.microsoft.com/azure/devops/pipelines/process/approvals?view=azure-devops) let you enforce the same rule at the release level: a stage cannot start until the verification artifact passes the configured gate condition — human review optional, machine check mandatory.

## Why a single verifiable agent ships where a capable model doesn't

The complexity ladder holds here too. Before you compose agents into teams (Module 4) or point them at production codebases (Module 6), the single agent must be verifiable — meaning you can look at its output and know, from facts rather than confidence, whether the task is done. The workbench is what makes that possible. It is not a workaround for a weak model; it makes any model shippable.

Ship the `agent-workbench-pack/` and you have an answer to the question every skeptic asks — not a promise, but a verdict file, a scope report, a feedback log, and a handoff packet. Artifacts, not assurances.

## Core concepts

- A deterministic `verify_agent.py` reads scope, rules, feedback, and diff and emits one verdict that CI and the human reviewer both read — the agent never grades its own work.
- A reviewer loop with a different system prompt and read-only access scores a five-dimension rubric; it catches "solved the wrong half of the bug," which verification cannot.
- `generate_handoff.py` turns workbench artifacts into a seven-field packet that makes the next session's first action deterministic — without it, context recovery costs ten minutes every session.
- The `agent-workbench-pack/` packages all seven surfaces as a drop-in installer; the M6 coding agent imports this pack and does not rebuild it — that is what compounding means.

<div class="claude-handoff" data-exercise="exercises/module3/15-the-workbench-surfaces-ii-and-the-pack/">

**Build it in Claude Code** — complete the workbench and ship the pack: implement `verify_agent.py` reading scope/rules/feedback artifacts and emitting `verification_report.json` with block-severity checks; implement a reviewer loop in `reviewer.py` scoring the five-dimension rubric against the diff and verification report using `claude-haiku-4-5`, emitting `review_report.json`; implement `generate_handoff.py` producing `handoff.json` from all artifacts; then assemble `agent-workbench-pack/` with all seven surfaces, JSON Schemas, and `bin/install.sh`, and run the installer against a sample FastAPI repo to prove it lays down cleanly. Use `claude-opus-4-8` for the builder loop in the demo run; use `claude-haiku-4-5` for the reviewer. Open the repo and run the exercise for this lesson.

</div>
