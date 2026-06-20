"""The fleet orchestrator — runs the governed SWE team end to end.

This is the control plane. It loads the registry (the contract), builds the
operator console from it (budget guard, audit log, kill switch, policy, shared
inbox), and drives the five-agent team through typed A2A handoffs under that
governance:

    feature request
        -> architect plans            (A2A: plan_feature)
        -> coder-1, coder-2 implement (A2A: implement_slice; the M6 loop, governed)
        -> tester runs the suite      (A2A: run_acceptance)
        -> reviewer gates             (A2A: review_changes)
        -> merge PROPOSED to the shared HITL inbox  <-- suspends here
        -> human approves through the inbox
        -> merge committed; audit answers all four clauses for every action

The merge is the one irreversible action, so it is the one that never
auto-executes: the orchestrator submits a proposal to the inbox and stops. A
``merge`` only happens when a human approves the proposal by its ``inbox_id``.

The whole run is a control plane reading a registry to know what it governs —
Claude Code now, a local model later. Point the registry at a new problem and the
orchestrator runs it unchanged. That is the M8 hand-off.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from a2a import A2AResult, A2ATask
from agents import architect, coder, reviewer, tester
from context import FleetContext
from governance.audit import AuditLog, new_correlation_id
from governance.fleet_budget import FleetBudgetGuard
from governance.inbox import SharedInbox
from governance.killswitch import KillSwitch
from mock_llm import CoderMockLLM, SinglePassMockLLM
from policy import FleetPolicy
from schema import load_registry


@dataclass
class FleetRun:
    """The outcome an operator reads: did the team ship, and is it accountable?"""

    status: str  # "merged" | "awaiting_approval" | "blocked" | "halted" | "budget_breach"
    detail: str
    correlation_id: str
    merge_inbox_id: str | None = None
    budget: dict = field(default_factory=dict)
    plan: list = field(default_factory=list)


class Fleet:
    """A governed multi-agent SWE team, assembled from the registry."""

    def __init__(self, registry: dict, kill_switch_path: str, on_event=None):
        self.registry = registry
        self.policy = FleetPolicy(registry)
        self.budget = FleetBudgetGuard.from_registry(registry)
        self.audit = AuditLog()
        self.inbox = SharedInbox()
        self.kill_switch = KillSwitch(kill_switch_path)
        self.on_event = on_event

    # --- the run ---------------------------------------------------------------

    def ship_feature(self, feature: str, project_root: str,
                     models: dict | None = None) -> FleetRun:
        """Drive the team to a MERGE PROPOSAL. Never merges on its own.

        Returns when the proposal is in the inbox (``awaiting_approval``), or
        earlier on a block / halt / budget breach. Call ``commit_merge`` after a
        human approves the proposal through the inbox.
        """
        corr = new_correlation_id()
        ctx = FleetContext(self.policy, self.budget, self.audit,
                           self.kill_switch, corr, self.on_event)
        models = models or {}

        # resolve the team from the registry by role
        arch_id = self.policy.agents_by_role("architect")[0]
        coder_ids = self.policy.agents_by_role("coder")
        tester_id = self.policy.agents_by_role("tester")[0]
        reviewer_id = self.policy.agents_by_role("reviewer")[0]

        def model_for(agent_id, default):
            return models.get(agent_id, default)

        # 1) architect plans -----------------------------------------------------
        plan_task = A2ATask("plan_feature", "operator", "architect", corr,
                            {"feature": feature})
        plan_res = architect.run(plan_task, ctx, arch_id, model_for(arch_id, SinglePassMockLLM()))
        if not plan_res.ok:
            return self._stop(plan_res, corr)
        plan = plan_res.artifacts["plan"]

        # 2) coders implement (the M6 loop, governed) ----------------------------
        coder_results = []
        for i, slice_spec in enumerate(plan):
            coder_id = coder_ids[i % len(coder_ids)]
            impl_task = A2ATask("implement_slice", arch_id, "coder", corr,
                                {"instruction": slice_spec["instruction"], "slice": slice_spec["slice"]})
            res = coder.run(impl_task, ctx, coder_id,
                            model_for(coder_id, CoderMockLLM()), project_root)
            if not res.ok:
                return self._stop(res, corr)
            coder_results.append({"agent": coder_id, "accepted": res.artifacts.get("accepted")})

        # 3) tester runs the acceptance suite ------------------------------------
        test_task = A2ATask("run_acceptance", arch_id, "tester", corr, {})
        test_res = tester.run(test_task, ctx, tester_id,
                              model_for(tester_id, SinglePassMockLLM()), project_root)
        if not test_res.ok:
            return self._stop(test_res, corr)

        # 4) reviewer gates ------------------------------------------------------
        review_task = A2ATask("review_changes", arch_id, "reviewer", corr,
                              {"coder_results": coder_results,
                               "tester_accepted": test_res.artifacts.get("accepted", False)})
        review_res = reviewer.run(review_task, ctx, reviewer_id,
                                  model_for(reviewer_id, SinglePassMockLLM()))
        if not review_res.ok:
            return self._stop(review_res, corr)

        if not review_res.artifacts["approve_merge"]:
            ctx.emit("blocked", reason=review_res.artifacts["reason"])
            return FleetRun("blocked", review_res.artifacts["reason"], corr,
                            budget=self.budget.summary(), plan=plan)

        # 5) merge PROPOSED to the shared inbox — suspend here -------------------
        # No agent has can_merge: true. The orchestrator does not merge; it
        # proposes, and the run waits for a human.
        inbox_id = self.inbox.submit(
            agent_id=reviewer_id, correlation_id=corr, action="merge",
            summary=f"Merge {feature!r}: tester ACCEPT, reviewer approved.",
            payload={"feature": feature},
        )
        ctx.emit("merge_proposed", inbox_id=inbox_id)
        self.audit.record(
            correlation_id=corr, agent=reviewer_id, authority=self.policy.authority(reviewer_id),
            task="propose_merge", evidence=f"merge proposed to inbox {inbox_id}; awaiting human",
        )
        return FleetRun("awaiting_approval",
                        f"merge proposed; awaiting human approval ({inbox_id})",
                        corr, merge_inbox_id=inbox_id,
                        budget=self.budget.summary(), plan=plan)

    def commit_merge(self, run: FleetRun, approver: str) -> FleetRun:
        """Commit the merge — ONLY if the proposal is approved in the inbox.

        The orchestrator re-reads the inbox gate; an unapproved (or off-channel)
        proposal does not merge. This is the propose-then-commit commit step.
        """
        inbox_id = run.merge_inbox_id
        if not inbox_id or not self.inbox.is_approved(inbox_id):
            return FleetRun("awaiting_approval",
                            "merge NOT committed: no inbox approval on record",
                            run.correlation_id, merge_inbox_id=inbox_id,
                            budget=self.budget.summary(), plan=run.plan)
        proposal = self.inbox.get(inbox_id)
        self.audit.record(
            correlation_id=run.correlation_id, agent="operator",
            authority=f"human={proposal.decided_by} via inbox {inbox_id}",
            task="commit_merge",
            evidence=f"merge committed; approved by {proposal.decided_by} ({inbox_id})",
        )
        if self.on_event:
            self.on_event({"event": "merged", "inbox_id": inbox_id, "by": proposal.decided_by})
        return FleetRun("merged", f"merged; approved by {proposal.decided_by}",
                        run.correlation_id, merge_inbox_id=inbox_id,
                        budget=self.budget.summary(), plan=run.plan)

    def _stop(self, res: A2AResult, corr: str) -> FleetRun:
        """Map an agent failure (halt / budget / refusal) to a fleet outcome."""
        reason = res.reason
        if reason.startswith("halted"):
            status = "halted"
        elif "budget" in reason:
            status = "budget_breach"
        else:
            status = "blocked"
        if self.on_event:
            self.on_event({"event": "stop", "status": status, "reason": reason})
        return FleetRun(status, reason, corr, budget=self.budget.summary())


def load_fleet(kill_switch_path: str, registry_path: str | None = None, on_event=None) -> Fleet:
    """Build a fleet from the registry contract — the M8 entry point."""
    registry = load_registry(registry_path) if registry_path else load_registry()
    return Fleet(registry, kill_switch_path, on_event=on_event)
