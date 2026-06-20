# Exercise 09 — Guardrails: Constitutional AI & Llama Guard

## Goal

Add a guardrail layer to the `_harness/` agents — an input/output content classifier plus a small constitution with hardcoded prohibitions the agent config cannot disable — and then prove the chapter's honest caveat: slip an obfuscated input past the classifier, and show that the deterministic layer underneath (kill switch, budget, or HITL gate from the prior lessons) still stops the action the classifier missed.

## Why

Guardrails govern content — what the agent should refuse, what it must never do. They are necessary and they are the layer most likely to give false confidence: Emoji Smuggling hit 100% attack-success against six guard systems. The point of this exercise is not to ship a classifier and declare the agent safe; it is to wire the classifier as one probabilistic layer *on top of* the hard limits that don't bend, and to demonstrate — with a working bypass — why the hard limits are the thing you actually trust.

## Steps

1. **Classifier hook.** Add `module4-fleet/guardrails/classifier.py` with `guarded_turn(agent, user_input, guard)` that screens input *and* output: classify the incoming prompt (refuse if unsafe), run the agent, classify the response (refuse if unsafe). Implement `guard` as a Llama-Guard-style screen — either a real small guard model, or a cheap classifier model given a short hazard taxonomy. Label each turn safe/unsafe with the matched category.

2. **Constitution config.** Add `module4-fleet/guardrails/constitution.yaml`: a four-tier priority (safety/oversight → ethics → operator guidelines → helpfulness) plus two rule classes — **hardcoded prohibitions** (the agent and operator config cannot disable these) and **operator-adjustable defaults** (length, topical scope, style, tool patterns; tunable within bounds). Enforce the split: an attempt to toggle a hardcoded prohibition from the operator config is rejected.

3. **Catch the obvious.** Send a batch of plainly unsafe inputs and confirm the input rail refuses them, and a prompt that coaxes an unsafe response and confirm the output rail refuses it. This is the classifier doing its real, legitimate job.

4. **Break it (the caveat, made concrete).** Craft an obfuscated input — emoji/Unicode smuggling, or another encoding the classifier reads as benign — that carries an instruction to perform a mutating action the classifier *would* have flagged in plain text. Confirm it slips past both rails.

5. **The hard layer holds.** Show that the smuggled action is still stopped by a deterministic control from the prior lessons: the HITL gate (exercise 08) still demands human approval for the mutating action, or the kill switch / budget (exercises 06–07) still halts it. The classifier was beaten; the limits that don't bend were not.

## Done when

- Input and output rails refuse plainly unsafe content with the matched hazard category.
- The constitution enforces the hardcoded-vs-adjustable split: operator config can tune defaults but cannot disable a hardcoded prohibition.
- A crafted obfuscated input demonstrably slips past the classifier.
- The smuggled mutating action is still stopped by a deterministic layer (HITL, kill switch, or budget) — proving guardrails are a layer, not the solution.

## Stretch

Stack a second, different classifier in front of the first and show an input crafted to fool *both* — making the "stack more classifiers" instinct visibly insufficient. Then write up, in the exercise's notes, exactly which layer you trust for which job: the classifier to reduce noise and catch the careless, the hard limits to be the thing that holds against a motivated adversary.
