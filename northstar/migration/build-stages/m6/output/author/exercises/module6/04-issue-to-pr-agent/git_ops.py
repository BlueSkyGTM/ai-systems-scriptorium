"""Local git only. A "PR" here = a branch + a PR-body file in outputs/.

The whole point of this module is that it CANNOT merge. There is no merge, no
push, no force-push, no network. The portable seam is the shape:

    issue -> branch -> commit -> PR-body artifact

In production that last step is a GitHub API call (`POST /pulls`) made with a
scoped installation token. Here it writes a markdown file. Swap the host by
swapping this one function; the loop above it does not change.

All git happens through `subprocess` against the local `git` binary, scoped to
one repo directory. No GitPython, no SDK, no third-party import.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from creds import CredentialBroker, Grant


class GitError(RuntimeError):
    """A git command failed. Carries the command and its stderr."""


def _git(repo: Path, *args: str) -> str:
    """Run a git command inside `repo` and return stdout, or raise GitError."""
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


@dataclass
class PullRequest:
    """The artifact a passing run produces. A branch plus a body file on disk."""

    repo: str
    branch: str
    base: str
    title: str
    body_path: Path
    head_sha: str


def current_branch(repo: Path) -> str:
    return _git(repo, "rev-parse", "--abbrev-ref", "HEAD")


def create_branch(repo: Path, branch: str, broker: CredentialBroker, repo_id: str) -> Grant:
    """Create and check out a new branch. Gated by the credential broker.

    The broker refuses any branch outside the scope's allowlist (e.g. `main`),
    so the agent cannot create a branch it would later try to merge into trunk.
    """
    grant = broker.request("branch", repo=repo_id, branch=branch)
    _git(repo, "checkout", "-b", branch)
    return grant


def has_staged_changes(repo: Path) -> bool:
    """True when `git add -A` would produce a non-empty commit."""
    proc = subprocess.run(
        ["git", "-C", str(repo), "diff", "--cached", "--quiet"],
        capture_output=True, text=True,
    )
    # `--quiet` exits 1 when there ARE staged differences.
    return proc.returncode == 1


def commit_all(repo: Path, message: str, broker: CredentialBroker, repo_id: str, branch: str) -> str | None:
    """Stage every change and commit. Returns the new SHA, or None if nothing changed.

    A coder that proposes no edit produces no commit. The loop then lets CI run
    on the unchanged (still-failing) repo and escalate — it does not crash.
    """
    broker.request("commit", repo=repo_id, branch=branch)
    _git(repo, "add", "-A")
    if not has_staged_changes(repo):
        return None
    # Local identity + no signing so the smoke path never prompts.
    _git(
        repo,
        "-c", "user.email=agent@local",
        "-c", "user.name=issue-to-pr-agent",
        "-c", "commit.gpgsign=false",
        "commit", "-m", message,
    )
    return _git(repo, "rev-parse", "HEAD")


def open_pr(
    repo: Path,
    *,
    branch: str,
    base: str,
    title: str,
    body: str,
    broker: CredentialBroker,
    repo_id: str,
    outputs_dir: Path,
) -> PullRequest:
    """Write the PR body to outputs/ as the "opened PR". NEVER merges.

    This is the swappable seam. Replace the file write with a GitHub API call
    and the rest of the agent is unchanged. The function intentionally exposes
    no path to merge: it returns a PullRequest record and stops.
    """
    broker.request("open_pr", repo=repo_id, branch=branch)
    head_sha = _git(repo, "rev-parse", "HEAD")
    outputs_dir.mkdir(parents=True, exist_ok=True)
    body_path = outputs_dir / f"pr-{branch.replace('/', '-')}.md"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body_path.write_text(
        f"# PR: {title}\n\n"
        f"- repo: `{repo_id}`\n"
        f"- base: `{base}`\n"
        f"- head: `{branch}` @ `{head_sha}`\n"
        f"- opened (artifact): {stamp}\n"
        f"- merge: **NOT performed** — review required (HITL gate)\n\n"
        f"---\n\n{body}\n",
        encoding="utf-8",
    )
    return PullRequest(
        repo=repo_id,
        branch=branch,
        base=base,
        title=title,
        body_path=body_path,
        head_sha=head_sha,
    )


# Note: there is deliberately no `merge()` in this module. Merging is a human
# action behind the HITL gate. See README.md and the guide's operator surfaces.
