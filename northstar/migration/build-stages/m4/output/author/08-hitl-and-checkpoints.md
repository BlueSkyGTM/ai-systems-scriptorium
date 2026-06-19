# HITL Propose-Then-Commit + Checkpoints/Rollback

Some actions you cannot take back. Wiring money, dropping a table, emailing a customer, merging to main — for these, "the agent decided to" is not an answer you want to give an auditor. Human-in-the-loop (HITL) is the protocol that puts a person between the agent's intent and the irreversible act, and getting it right is more than slapping an "Approve?" button on a tool call.

## Propose-then-commit, in five moves

The naive HITL is a prompt: the agent is about to act, a dialog pops up, the human clicks yes, the action runs. It fails in two directions — the approval is lost when the process dies before the human answers, and the human, asked yes-or-no fifty times an hour, stops reading. The 2026 consensus pattern fixes both by treating approval as a durable, structured transaction, not a popup.

It has five moves, and skipping any one reopens a hole:

**1. Persist the proposal.** The agent does not hold the pending action in memory; it writes the *proposed* action to a durable store with an **idempotency key** — a unique ID for this specific intended act. This is what lets the run pause (lesson 05's durable execution) and survive the wait. A proposal in RAM is a proposal lost to the next deploy.

**2. Surface what the human needs to judge.** Not "Run tool `transfer`?" but the full case: the **intent** (why the agent wants this), the **data lineage** (where its inputs came from), the **blast radius** (what this touches and how much), and the **rollback plan** (how it gets undone if it's wrong). A human cannot approve what they cannot see, and a one-line tool name shows them nothing.

**3. Commit only on positive acknowledgement.** The action runs *only* after an explicit yes. Not on timeout, not on silence, not on a default. Absence of a no is not a yes.

**4. Verify after.** Once committed, confirm the side effect actually happened — the row was written, the email was sent, the transfer cleared. An approved action is not a completed action until you've checked.

**5. Record the whole transaction.** Proposal, approver, timestamp, outcome — the audit trail is a byproduct of doing the protocol, not extra work.

```python
# module4-fleet/hitl/propose.py — propose-then-commit, control plane in Python
import uuid

def propose(action: Action, store: ProposalStore) -> str:
    key = action.idempotency_key or str(uuid.uuid4())
    store.put(key, {
        "status": "pending",
        "action": action.serialize(),
        "intent": action.intent,
        "lineage": action.input_sources,      # data lineage
        "blast_radius": action.blast_radius,  # what it touches, magnitude
        "rollback": action.rollback_plan,
    })
    return key                                 # the run suspends here (durable pause)

def commit(key: str, ack: Acknowledgement, store: ProposalStore) -> Result:
    rec = store.get(key)
    if rec["status"] != "pending":
        return rec["result"]                   # idempotent: already committed, return prior result
    if not ack.is_positive:                    # silence/timeout/no -> do NOT run
        store.patch(key, status="rejected")
        raise Rejected(key)
    result = execute(rec["action"])            # the irreversible act, exactly once
    store.patch(key, status="committed", result=result)
    return result
```

Three frameworks ship this shape, and naming them is worth your time because you'll meet at least one. LangGraph's `interrupt()` suspends a graph at an approval node and resumes from the checkpoint when the human answers. [verify: LangGraph — interrupt() / human-in-the-loop] Cloudflare's `waitForApproval()` does the same on a Durable Object. [verify: Cloudflare Agents — waitForApproval()] On Azure, the Microsoft Agent Framework raises a `RequestInfoEvent` to hand control to a human and waits for the response before continuing. [MS-Learn: Microsoft Agent Framework RequestInfoEvent / human-in-the-loop] Same protocol, three surfaces.

## The rubber-stamp is the failure that matters

Here is the uncomfortable truth about HITL: the protocol above can be perfectly implemented and still fail completely, because the weak point is not the code. It is the human who clicks "approve" without reading.

A reviewer asked the same yes/no question fifty times a day, who has clicked yes forty-nine times because forty-nine were fine, will click yes on the fiftieth — the one that wires money to the wrong account. This is the **rubber-stamp**, and it is the canonical HITL failure. A gate that everyone waves through is not a gate; it is latency with a logged signature.

The mitigation is to make approval cost attention. **Challenge-and-response** replaces the yes/no with a short checklist the approver must actively answer — *what is the dollar amount? what is the target account? is this reversible?* — surfaced from the proposal, requiring the human to engage with the specifics rather than pattern-match a button. The goal is not friction for its own sake; it is to break the reflex, to make the fiftieth approval as deliberate as the first. Tune it: too much friction and people route around the gate, too little and it's a rubber stamp again. The right amount scales with blast radius — a one-dollar action gets a glance, a wire transfer gets the full checklist.

## Checkpoints and rollback: why a retry can double-execute

Now connect HITL to durability, because the connection is where a subtle, expensive bug lives. You have a long-horizon run (lesson 05) that retries on failure. You have an approved action. What happens if the process dies *after* the action runs but *before* it records that it ran?

A naive retry re-executes it. The transfer goes out twice. The approved-once action commits twice. Durability that protects work also, done carelessly, duplicates irreversible side effects.

The combination that closes this needs all four pieces, and dropping any one reopens the gap:

- **Idempotency key** — the same key on a retried action means "you already did this; return the prior result" instead of doing it again. (This is why the proposal carried one from move 1.)
- **Precondition check** — before committing, confirm the state still matches what the human approved. State drifted since approval? Don't blindly fire; re-propose.
- **Post-action verify** — confirm the side effect actually landed (move 4).
- **Rollback on verify-fail** — if the verify fails, undo cleanly using the rollback plan, so a half-applied action doesn't leave the system inconsistent.

Idempotency key prevents the double-execute. Precondition check prevents acting on stale approval. Post-action verify catches the silent failure. Rollback-on-fail keeps a broken commit from leaving wreckage. Three of the four is not "mostly safe" — it is a specific, nameable way to corrupt state.

## This is now a legal requirement, not a best practice

For high-risk systems, queryable checkpoints and rehearsed rollbacks are no longer a matter of engineering taste. The EU AI Act's Article 14 mandates effective human oversight of high-risk AI systems — which, read against this protocol, means the proposal must be inspectable, the human must be able to intervene and stop, and the rollback must be something you've actually tested rather than something you hope works. [verify: EU AI Act Article 14 — human oversight requirements] A rollback plan you have never rehearsed is a rollback plan you do not have; under Article 14, that gap is a compliance failure, not just an operational risk.

## Where this goes at fleet scale

Everything here is defined for a single agent and a single approver. The fleet lessons in M4's back half apply it across many agents through a **shared inbox** — proposals from a fleet land in one queue, approvers work the queue, and the same propose-then-commit protocol governs each. They reference this lesson; they do not re-teach the commit protocol. Define HITL once, here, and the fleet inbox is just this protocol with more proposers.

Build the gate so the approve button means something — a persisted proposal, a real case to judge, a positive ack, a verify, and a rollback you've run — and you have human oversight. Build it as a popup over a tool call and you have a rubber stamp with extra steps.

## Core concepts

- Propose-then-commit HITL persists the proposed action with an idempotency key, surfaces intent / data lineage / blast radius / rollback, commits only on positive acknowledgement, and verifies after — silence or timeout is never a yes.
- The rubber-stamp is the canonical HITL failure: a human approving without reading; mitigate with challenge-and-response checklists that cost attention, scaled to blast radius.
- Safe checkpoint/rollback needs all four of idempotency key + precondition check + post-action verify + rollback-on-fail; with any one missing, a retry after a crash can double-execute an approved, irreversible action.
- EU AI Act Article 14 makes queryable checkpoints and rehearsed rollbacks mandatory for high-risk systems — an unrehearsed rollback is a compliance gap, not just an operational one.

<div class="claude-handoff" data-exercise="exercises/module4/08-hitl-and-checkpoints/">

**Build it in Claude Code** — put a propose-then-commit gate in front of the `_harness/` agents' mutating actions: persist each proposal with an idempotency key and a surfaced case (intent, blast radius, rollback plan), commit only on positive acknowledgement, and verify the side effect after. Then prove the double-execute defense — commit an action, simulate a crash-and-retry with the same idempotency key, and confirm it returns the prior result instead of firing twice. Add a challenge-and-response checklist for high-blast-radius actions. Open the repo and run the exercise for this lesson.

</div>
