"""The M4 loop: trigger -> action -> verification -> budget/kill-switch.

This is lesson 10's four-stage shape, applied to one job: turn a GitHub issue
into a reviewed pull request. Nothing here is new machinery; it wires the parts:

    trigger      -> an open issue exists (no issue => no-op, spend nothing)
    action       -> draft a fix (action.py; artifact 01 in production)
    verification -> run CI (ci.py); defaults REJECT; the agent cannot fake it
    budget/kill  -> charge each step; the operator's kill-switch halts the loop

The loop NEVER merges. On APPROVE it opens a PR (a branch + a PR-body artifact)
and hands the merge decision to a human. On REJECT it escalates with a note.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import action as action_mod
import ci as ci_mod
import git_ops
from ci import Verdict
from creds import Budget, BudgetExceeded, CredentialBroker, KillSwitch, ScopeError


@dataclass
class LoopResult:
    outcome: str  # "no-op" | "halted" | "acted" | "escalated" | "stopped"
    reason: str = ""
    pr: git_ops.PullRequest | None = None
    escalation_path: Path | None = None
    verdict: Verdict | None = None
    spent: dict = field(default_factory=dict)


def _escalate(outputs_dir: Path, branch: str, issue_title: str, detail: str) -> Path:
    """Write an escalation note for a human. NEVER opens a PR on a failed gate."""
    outputs_dir.mkdir(parents=True, exist_ok=True)
    path = outputs_dir / f"escalation-{branch.replace('/', '-')}.md"
    path.write_text(
        f"# Escalation: {issue_title}\n\n"
        f"- branch: `{branch}`\n"
        f"- status: **CI did not pass** — no PR opened, no merge\n\n"
        f"## Why this needs a human\n\n{detail}\n\n"
        f"The agent stopped here by design: the verification gate defaults REJECT, "
        f"and a rejected change is handed back to a person, not merged.\n",
        encoding="utf-8",
    )
    return path


def run_loop(
    repo: Path,
    *,
    issue: action_mod.Issue | None,
    broker: CredentialBroker,
    kill_switch: KillSwitch,
    budget: Budget,
    outputs_dir: Path,
    base_branch: str,
    branch: str,
    repo_id: str,
    use_real_llm: bool = False,
) -> LoopResult:
    """One pass of the four-stage loop. Returns a structured outcome."""

    # --- 0. Kill-switch: checked before anything spends. ----------------------
    if kill_switch.tripped():
        return LoopResult("halted", reason="kill_switch", spent=budget.spent)

    # --- 1. Trigger: is there work? No issue => no-op, near-zero spend. -------
    if issue is None:
        return LoopResult("no-op", reason="no open issue", spent=budget.spent)

    try:
        # Confirm read scope before touching the repo at all.
        broker.request("read", repo=repo_id)

        # --- 2. Action: draft a fix on an isolated branch. --------------------
        git_ops.create_branch(repo, branch, broker, repo_id)
        budget.charge(tokens=500)  # the trigger/plan step costs something
        if kill_switch.tripped():
            return LoopResult("halted", reason="kill_switch", spent=budget.spent)

        proposal = action_mod.draft_fix(repo, issue, use_real_llm=use_real_llm)
        budget.charge(tokens=proposal.tokens_used)

        git_ops.commit_all(
            repo,
            f"fix: {issue.title}\n\n{proposal.summary}",
            broker, repo_id, branch,
        )

        # --- 3. Verification: run CI. Defaults REJECT. Agent can't fake it. ---
        if kill_switch.tripped():
            return LoopResult("halted", reason="kill_switch", spent=budget.spent)
        result = ci_mod.run_ci(repo)
        budget.charge(tokens=300)  # reading the CI result costs something

        if result.verdict is not Verdict.APPROVE:
            note = _escalate(
                outputs_dir, branch, issue.title,
                f"CI exited {result.exit_code}. Tail of output:\n\n"
                f"```\n{result.output[-1500:]}\n```",
            )
            return LoopResult(
                "escalated", reason="ci_failed",
                escalation_path=note, verdict=result.verdict, spent=budget.spent,
            )

        # --- 4. APPROVE: open a PR (branch + body artifact). NEVER merge. -----
        pr = git_ops.open_pr(
            repo,
            branch=branch,
            base=base_branch,
            title=f"Fix: {issue.title}",
            body=(
                f"## What changed\n\n{proposal.summary}\n\n"
                f"## Why\n\n{proposal.rationale}\n\n"
                f"## Verification\n\n"
                f"CI passed locally (`{' '.join(result.command)}`, exit 0). "
                f"A human reviews and merges; the agent does not.\n"
            ),
            broker=broker,
            repo_id=repo_id,
            outputs_dir=outputs_dir,
        )
        return LoopResult(
            "acted", reason="ci_passed",
            pr=pr, verdict=result.verdict, spent=budget.spent,
        )

    except BudgetExceeded as exc:
        return LoopResult("stopped", reason=f"budget: {exc}", spent=budget.spent)
    except ScopeError as exc:
        # An out-of-scope credential request is a hard stop, never a retry.
        return LoopResult("stopped", reason=f"scope: {exc}", spent=budget.spent)
