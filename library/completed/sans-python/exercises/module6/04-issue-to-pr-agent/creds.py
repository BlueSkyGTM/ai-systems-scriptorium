"""Scoped credentials + a kill-switch the agent reads but cannot write.

Two operator surfaces live here:

  1. CredentialBroker — the agent never holds a raw token. It asks the broker
     for a capability ("write to repo X on branch Y"). The broker grants only
     what is on its scope allowlist and refuses everything else. An out-of-scope
     request raises ScopeError; the loop treats that as a hard stop, not a retry.

  2. KillSwitch — a file the operator owns. The agent reads it before every
     action. It has no method to clear or write it. Halting is the operator's
     privilege, not the agent's.

Nothing here touches the network. A "credential" on the smoke path is a scope
grant, not a real GitHub token. The real token (if you opt in via .env) is read
once at the edge and never passed into the loop; see README.md.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


class ScopeError(PermissionError):
    """Raised when the agent asks for a capability outside its grant."""


@dataclass(frozen=True)
class Scope:
    """What the agent is allowed to do. Frozen: the agent cannot widen it."""

    repo: str
    # Branch prefixes the agent may create/commit on. "main"/"master" are never here.
    branch_prefixes: tuple[str, ...] = ("agent/",)
    # Capabilities the agent may request. "merge" is deliberately absent.
    actions: frozenset[str] = frozenset({"read", "branch", "commit", "open_pr"})

    def permits_branch(self, branch: str) -> bool:
        return any(branch.startswith(p) for p in self.branch_prefixes)


@dataclass
class Grant:
    """A single approved capability the broker hands back. Not a token."""

    repo: str
    action: str
    branch: str | None = None


class CredentialBroker:
    """Gates capability requests against a fixed Scope.

    The agent calls `request(...)`. The broker returns a Grant on an in-scope
    request and raises ScopeError otherwise. The broker is the only object that
    would ever see a real token; the agent sees grants.
    """

    def __init__(self, scope: Scope, *, real_token: str | None = None) -> None:
        self._scope = scope
        # On the smoke path this stays None. A real GITHUB_TOKEN, if present,
        # is held here and NEVER returned to the caller.
        self._real_token = real_token

    @property
    def scope(self) -> Scope:
        return self._scope

    def request(self, action: str, *, repo: str, branch: str | None = None) -> Grant:
        if repo != self._scope.repo:
            raise ScopeError(
                f"out-of-scope repo: asked for {repo!r}, scoped to {self._scope.repo!r}"
            )
        if action not in self._scope.actions:
            raise ScopeError(
                f"out-of-scope action: {action!r} not in {sorted(self._scope.actions)}"
            )
        if action in ("branch", "commit", "open_pr"):
            if branch is None:
                raise ScopeError(f"action {action!r} requires a branch")
            if not self._scope.permits_branch(branch):
                raise ScopeError(
                    f"out-of-scope branch: {branch!r} not under {self._scope.branch_prefixes}"
                )
        return Grant(repo=repo, action=action, branch=branch)

    def has_real_token(self) -> bool:
        return bool(self._real_token)


class KillSwitch:
    """A file the operator owns. The agent reads it; it cannot write it.

    `tripped()` returns True when the file exists with non-empty content. The
    class exposes no method to create or clear that file: only the operator,
    out of band (`touch outputs/KILL`), can flip it. This is the lesson-07
    control-plane rule — the off switch is in the operator's hand.
    """

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self._path = Path(path)

    def tripped(self) -> bool:
        try:
            return self._path.is_file() and self._path.read_text().strip() != ""
        except OSError:
            # A switch we cannot read is treated as tripped: fail safe.
            return True

    @property
    def path(self) -> Path:
        return self._path


@dataclass
class Budget:
    """Per-run cost ceiling. The loop charges it per step; breach stops it."""

    max_steps: int = 25
    max_tokens: int = 200_000
    _steps: int = field(default=0, init=False)
    _tokens: int = field(default=0, init=False)

    def charge(self, *, tokens: int) -> None:
        self._steps += 1
        self._tokens += tokens
        if self._steps > self.max_steps:
            raise BudgetExceeded(f"step budget {self.max_steps} exceeded")
        if self._tokens > self.max_tokens:
            raise BudgetExceeded(f"token budget {self.max_tokens} exceeded")

    @property
    def spent(self) -> dict[str, int]:
        return {"steps": self._steps, "tokens": self._tokens}


class BudgetExceeded(RuntimeError):
    """Raised on a budget breach. The next action does not run."""
