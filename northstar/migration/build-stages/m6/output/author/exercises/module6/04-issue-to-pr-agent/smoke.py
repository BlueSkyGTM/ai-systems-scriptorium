"""End-to-end smoke run on the local fixture repo. Stdlib-only. No network.

    read the issue -> branch -> draft a fix (mock LLM) -> run local CI
      -> on pass:  write a PR body to outputs/   (NEVER merge)
      -> on fail:  write an escalation note       (NEVER open a PR)

Enforces every operator surface: a scoped credential broker, a kill-switch the
agent reads but cannot write, and a per-run budget. Run it:

    python smoke.py

It prints the outcome and exits 0 when the happy path produces a PR artifact.
The real-GitHub path is opt-in via .env and never touched here.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import action as action_mod
import loop as loop_mod
from creds import Budget, CredentialBroker, KillSwitch, Scope

HERE = Path(__file__).resolve().parent
FIXTURE_SRC = HERE / "fixture_repo"
REPO_ID = "local/fixture-repo"
AGENT_BRANCH = "agent/fix-add-off-by-one"


def prepare_workspace(dest: Path) -> Path:
    """Copy the pristine fixture into `dest` and make it a real git repo.

    The source `fixture_repo/` is a template; each run gets a fresh clone-like
    copy so the seeded bug is always present and runs don't pollute each other.
    """
    repo = dest / "repo"
    shutil.copytree(FIXTURE_SRC, repo)
    _git(repo, "init", "-q")
    # Deterministic, prompt-free local git for the smoke path.
    _git(repo, "config", "core.autocrlf", "false")
    _git(repo, "config", "user.email", "fixture@local")
    _git(repo, "config", "user.name", "fixture")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "checkout", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed: calculator with off-by-one bug")
    return repo


def _git(repo: Path, *args: str) -> None:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")


def build_broker() -> CredentialBroker:
    """A broker scoped to the fixture repo and the agent/ branch prefix only."""
    scope = Scope(repo=REPO_ID, branch_prefixes=("agent/",))
    return CredentialBroker(scope)  # no real token on the smoke path


def run(workdir: Path | None = None) -> loop_mod.LoopResult:
    """Run one full loop pass on a fresh workspace. Returns the outcome."""
    tmp = Path(tempfile.mkdtemp(prefix="issue2pr-")) if workdir is None else workdir
    repo = prepare_workspace(tmp)
    outputs_dir = tmp / "outputs"

    issue = action_mod.parse_issue((repo / "ISSUE.md").read_text(encoding="utf-8"))
    broker = build_broker()
    kill_switch = KillSwitch(outputs_dir / "KILL")
    budget = Budget(max_steps=25, max_tokens=200_000)

    return loop_mod.run_loop(
        repo,
        issue=issue,
        broker=broker,
        kill_switch=kill_switch,
        budget=budget,
        outputs_dir=outputs_dir,
        base_branch="main",
        branch=AGENT_BRANCH,
        repo_id=REPO_ID,
    )


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="issue2pr-"))
    try:
        result = run(tmp)
        print(f"outcome : {result.outcome}")
        print(f"reason  : {result.reason}")
        print(f"verdict : {result.verdict}")
        print(f"spent   : {result.spent}")
        if result.pr is not None:
            print(f"PR body : {result.pr.body_path}")
            print(f"branch  : {result.pr.branch} @ {result.pr.head_sha[:10]}")
            print("merge   : NOT performed (HITL gate) — by design")
        if result.escalation_path is not None:
            print(f"escalated -> {result.escalation_path}")

        if result.outcome == "acted" and result.pr is not None:
            print("\nSMOKE PASS: issue -> branch -> fix -> CI -> PR artifact, no merge.")
            return 0
        print(f"\nSMOKE FAIL: expected 'acted' with a PR, got '{result.outcome}'.")
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
