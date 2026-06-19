# Guardrails: Constitutional AI & Llama Guard

Every control in this chapter so far is mechanical — a budget that counts, a switch that flips, a gate that waits for a human. Guardrails are the layer that tries to govern the agent's *content*: what it should refuse, what it should never do, what crosses a line. They are necessary, and they are the layer most likely to give you false confidence, so this lesson does two jobs — show you how they work, and show you exactly where they don't.

## Two kinds of guardrail, two places they live

Content governance comes in two shapes, and conflating them is a common mistake. One bakes values into the model's training; the other classifies traffic at the edges of the running system. You want both, and you want to know which is which.

**Constitutional AI** trains the model itself to reason about principles rather than match a list of banned strings. Anthropic's approach gives the model a written constitution and a **four-tier priority hierarchy** the model resolves when principles conflict:

1. **Safety and supporting human oversight** — the top tier. Nothing overrides it.
2. **Ethics** — broad ethical conduct.
3. **Operator guidelines** — the deploying organization's rules.
4. **Helpfulness** — be useful to the user.

The order is the point. When helpfulness pulls against safety, safety wins by construction, not by a patch. And the constitution splits its rules into two hardness classes that matter operationally:

- **Hardcoded prohibitions** — the absolute floor. Bioweapons uplift, child sexual abuse material, attacks on critical infrastructure. Neither the operator nor the user can switch these off. They do not bend.
- **Operator-adjustable defaults** — response length, topical scope, style, tool-use patterns. The deploying team tunes these within bounds for their use case.

This split is what you operate against: you get knobs, but the knobs stop at the prohibitions, and that boundary is not yours to move. The honest limit of reason-based alignment is that it relies on the model *generalizing* its principles to situations nobody anticipated — which is more robust than a keyword list and still not a guarantee. [verify: Anthropic — Constitutional AI / the Claude constitution / four-tier priority]

**Llama Guard** is the other shape: a separate classifier model that screens content at runtime, on the way in and on the way out. Meta's Llama Guard 3 and 4 take a message — a user prompt or a model response — and label it safe or unsafe against a hazard taxonomy (Llama Guard 4 covers categories S1–S14, including code-interpreter abuse). [verify: Meta — Llama Guard 3 / Llama Guard 4 / MLCommons hazard taxonomy] It runs as input/output classification around your agent:

```python
# module4-fleet/guardrails/classifier.py — input/output screening around the loop
def guarded_turn(agent, user_input: str, guard) -> str:
    if guard.classify(user_input).unsafe:        # input rail
        return refuse("input flagged")
    output = agent.act(user_input)
    if guard.classify(output).unsafe:            # output rail
        return refuse("output flagged")
    return output
```

Constitutional AI shapes what the model *is*; Llama Guard checks what passes *through*. The first is alignment; the second is a filter. Defense in depth wants both — and even both is not enough, which is the part of this lesson you must not skip.

## The honest caveat: a classifier is a layer, not a solution

It is tempting to wire up Llama Guard, watch it catch a batch of obvious attacks, and conclude the agent is safe. It is not, and the evidence is blunt. Research on bypassing prompt-injection and jailbreak detection demonstrated **Emoji Smuggling** — hiding malicious instructions inside emoji-adjacent Unicode the classifier reads as benign — reaching a **100% attack-success rate against six different guard systems**. One technique, total bypass, across the field. [verify: Emoji Smuggling — "Bypassing Prompt Injection and Jailbreak Detection" / 100% ASR on six guard systems]

Sit with what that means. A classifier is a model, and a model can be fooled by an input crafted to fool it. Stack two classifiers and an attacker finds the input that fools both. The classifier raises the cost of an attack; it does not close the door. Treating it as the door is how teams ship an agent they believe is guarded and is, against a motivated adversary, wide open.

This is not an argument against guardrails. It is an argument about what they are *for*. A guardrail classifier is one probabilistic layer in a stack — it catches the unsophisticated majority and buys you signal. What it cannot be is the thing standing between a determined attacker and an irreversible action.

## Layer the soft with the hard

The resolution is the through-line of this whole chapter: layer the probabilistic guardrails *on top of* the deterministic limits that don't bend. A classifier might be smuggled past; a per-task dollar budget cannot be talked into raising itself, a kill switch the agent can't write cannot be jailbroken into the off-to-on direction, and an idempotency-keyed HITL gate on a wire transfer does not care how clever the prompt was — the human still has to approve, and the action still runs at most once.

So the safe posture is concrete. Put a guardrail classifier on input and output to catch the obvious. Anchor it to a constitution whose hardcoded prohibitions you cannot disable. And underneath both, keep the mechanical controls from lessons 06 through 08 — budgets, kill switch, HITL — because those are the layer that holds when the classifier is fooled. The soft layers reduce how often the hard layers are tested; the hard layers are what you actually trust.

The decision this lesson hands you is not "which guardrail." It is *where each layer earns trust*. Trust the classifier to reduce noise and catch the careless. Trust the budget, the switch, and the human gate to be the thing that holds when content governance fails — because against a real adversary, it will. An agent guarded only by classifiers is an agent guarded by something that has already been beaten 100% of the time; the limits that don't bend are why it still can't spend your money or drop your table.

## Core concepts

- Constitutional AI trains the model to resolve principle conflicts by a four-tier priority — safety/oversight → ethics → operator guidelines → helpfulness — and splits rules into hardcoded prohibitions (un-overridable) and operator-adjustable defaults (your knobs, bounded).
- Llama Guard 3/4 is a separate classifier that screens input and output against a hazard taxonomy; it is a runtime filter, not alignment, and complements (does not replace) a trained constitution.
- A classifier is a layer, not a solution: Emoji Smuggling reached 100% attack-success against six guard systems, so a guardrail raises attack cost but never closes the door.
- The safe posture layers probabilistic guardrails on top of deterministic limits — budgets, kill switches, HITL — because the hard limits are what hold when a classifier is fooled, which against a real adversary it will be.

<div class="claude-handoff" data-exercise="exercises/module4/09-guardrails/">

**Build it in Claude Code** — add a guardrail hook to the `_harness/` agents: an input/output classifier pass (a Llama-Guard-style screen, or a cheap model classifier) that flags unsafe content on the way in and the way out, plus a small constitution config with hardcoded prohibitions the agent config cannot disable. Then prove the caveat: craft an obfuscated input that slips past the classifier, and show that the deterministic layer underneath — the kill switch, budget, or HITL gate from the prior lessons — still stops the action the classifier missed. Open the repo and run the exercise for this lesson.

</div>
