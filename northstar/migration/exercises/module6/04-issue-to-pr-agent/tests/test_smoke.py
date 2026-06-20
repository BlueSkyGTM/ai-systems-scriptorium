"""Operator-surface tests for the issue-to-PR agent. Stdlib + the scaffold only.

Run:  python -m pytest tests/        (or: python tests/test_smoke.py)

Each test pins one of the operator surfaces the M8 student will drive:
  - a passing fix opens a PR (branch + body artifact) and does NOT merge
  - a failing CI run escalates instead of opening a PR
  - the kill-switch halts the loop before it spends
  - an out-of-scope credential request is refused
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

# Make the scaffold importable whether run from the dir or via `pytest tests/`.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import action as action_mod  # noqa: E402
import loop as loop_mod  # noqa: E402
import smoke  # noqa: E402
from ci import Verdict  # noqa: E402
from creds import Budget, CredentialBroker, KillSwitch, Scope, ScopeError  # noqa: E402


def _branch_exists(repo: Path, branch: str) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", branch],
        capture_output=True, text=True,
    )
    return proc.returncode == 0


def _current_branch(repo: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip()


def _main_is_unmerged(repo: Path) -> bool:
    """main must still hold the buggy code: the agent never merged."""
    src = subprocess.run(
        ["git", "-C", str(repo), "show", "main:calculator.py"],
        capture_output=True, text=True,
    ).stdout
    return "a + b + 1" in src


# --------------------------------------------------------------------------- #

def test_passing_fix_opens_pr_and_does_not_merge():
    tmp = Path(tempfile.mkdtemp(prefix="t-pass-"))
    result = smoke.run(tmp)
    repo = tmp / "repo"

    assert result.outcome == "acted", result
    assert result.verdict is Verdict.APPROVE
    # A PR artifact exists...
    assert result.pr is not None
    assert result.pr.body_path.is_file()
    assert "NOT performed" in result.pr.body_path.read_text(encoding="utf-8")
    # ...on a new agent branch...
    assert _branch_exists(repo, smoke.AGENT_BRANCH)
    assert _current_branch(repo) == smoke.AGENT_BRANCH
    # ...and main was NEVER merged into: it still has the bug.
    assert _main_is_unmerged(repo)


def test_failing_ci_escalates_and_opens_no_pr():
    """If the coder produces a non-fixing edit, CI stays red -> escalate."""
    tmp = Path(tempfile.mkdtemp(prefix="t-fail-"))
    repo = smoke.prepare_workspace(tmp)
    outputs_dir = tmp / "outputs"
    issue = action_mod.parse_issue((repo / "ISSUE.md").read_text(encoding="utf-8"))

    # A coder whose edit does NOT fix the bug: it changes a real line (so there
    # is a commit) but leaves the off-by-one in place. CI must catch it.
    def bad_fix(repo_path, _issue, **_kw):
        calc = repo_path / "calculator.py"
        src = calc.read_text(encoding="utf-8")
        calc.write_text(src + "\n# touched, but the bug remains\n", encoding="utf-8")
        return action_mod.FixProposal(
            file="calculator.py",
            summary="touched an unrelated line; bug remains",
            tokens_used=1000,
            rationale="deliberately non-fixing edit for the test",
        )

    original = action_mod.draft_fix
    loop_mod.action_mod.draft_fix = bad_fix  # type: ignore[attr-defined]
    try:
        result = loop_mod.run_loop(
            repo,
            issue=issue,
            broker=smoke.build_broker(),
            kill_switch=KillSwitch(outputs_dir / "KILL"),
            budget=Budget(),
            outputs_dir=outputs_dir,
            base_branch="main",
            branch=smoke.AGENT_BRANCH,
            repo_id=smoke.REPO_ID,
        )
    finally:
        loop_mod.action_mod.draft_fix = original  # type: ignore[attr-defined]

    assert result.outcome == "escalated", result
    assert result.verdict is Verdict.REJECT
    assert result.pr is None
    assert result.escalation_path is not None and result.escalation_path.is_file()
    # No PR artifact was written.
    assert not list(outputs_dir.glob("pr-*.md"))


def test_kill_switch_halts_before_spending():
    tmp = Path(tempfile.mkdtemp(prefix="t-kill-"))
    repo = smoke.prepare_workspace(tmp)
    outputs_dir = tmp / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    # Operator trips the switch out of band.
    (outputs_dir / "KILL").write_text("halt: incident in progress\n", encoding="utf-8")

    issue = action_mod.parse_issue((repo / "ISSUE.md").read_text(encoding="utf-8"))
    budget = Budget()
    result = loop_mod.run_loop(
        repo,
        issue=issue,
        broker=smoke.build_broker(),
        kill_switch=KillSwitch(outputs_dir / "KILL"),
        budget=budget,
        outputs_dir=outputs_dir,
        base_branch="main",
        branch=smoke.AGENT_BRANCH,
        repo_id=smoke.REPO_ID,
    )

    assert result.outcome == "halted"
    assert result.reason == "kill_switch"
    assert budget.spent["tokens"] == 0  # halted before any spend
    assert not _branch_exists(repo, smoke.AGENT_BRANCH)  # no branch created


def test_out_of_scope_cred_request_is_refused():
    broker = CredentialBroker(Scope(repo="local/fixture-repo", branch_prefixes=("agent/",)))

    # Wrong repo.
    try:
        broker.request("read", repo="someone-else/private")
        assert False, "expected ScopeError for out-of-scope repo"
    except ScopeError:
        pass

    # Branch outside the allowlist (e.g. trunk).
    try:
        broker.request("commit", repo="local/fixture-repo", branch="main")
        assert False, "expected ScopeError for out-of-scope branch"
    except ScopeError:
        pass

    # An action the scope does not grant — merge is never in scope.
    try:
        broker.request("merge", repo="local/fixture-repo", branch="agent/x")
        assert False, "expected ScopeError for ungranted action"
    except ScopeError:
        pass

    # In-scope request still works.
    grant = broker.request("commit", repo="local/fixture-repo", branch="agent/fix-1")
    assert grant.action == "commit" and grant.branch == "agent/fix-1"


if __name__ == "__main__":
    test_passing_fix_opens_pr_and_does_not_merge()
    test_failing_ci_escalates_and_opens_no_pr()
    test_kill_switch_halts_before_spending()
    test_out_of_scope_cred_request_is_refused()
    print("all smoke tests passed")
