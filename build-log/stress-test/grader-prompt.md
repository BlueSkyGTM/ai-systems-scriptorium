# Pinned Grader — the ceiling judge

The measurement instrument. "Pinned" = fixed model + fixed prompt + fixed rubric + a threshold set in
advance (`PILOT-SPEC.md`). Changing any of these invalidates comparison across runs, so they are
frozen here. The grader sees two blind texts and scores each on `ceiling-rubric.md`. It is never told
which model wrote which, or that model tier is even the variable.

## Pinned settings (do not change mid-study)
- **Judge model:** `claude-opus-4-8`, a fresh instance with no session context (the judge must not be
  one of the authoring hosts and must not have seen the pilot spec's hypothesis).
- **Runs:** 3 independent runs per pilot, fresh instance each. Average per dimension; report the spread.
- **Temperature:** lowest available / default-deterministic. (LLM judging is not fully deterministic;
  the 3-run average + reported variance is how we handle that, per the spec's inconclusive rule.)
- **Order:** randomize which text is A vs B per run; the operator holds the A/B→tier mapping offline.

## The prompt (paste verbatim; fill the two blocks)

```
You are grading two versions of the same instructional module from a technical book for AI engineers.
They cover the same topic from the same brief. Score each INDEPENDENTLY on the rubric below. You do
not know who or what wrote either version; do not speculate. Judge only the text.

Rubric — five dimensions, 1 to 5 each (anchors):
1. Insight Density — 5: nearly every paragraph teaches something non-obvious, no padding; 3: useful
   but diluted by filler; 1: mostly restatement, could be halved.
2. Explanatory Depth — 5: explains the mechanism/why, when it breaks, the tradeoff; 3: names the why
   but stops a level short; 1: surface only, rule without reason.
3. Voice/Craft — 5: concrete, direct, confident, no AI-tells, machine tokens separated from prose;
   3: competent but flatter, occasional generic phrasing; 1: pervasive AI-tells, vague, hedging.
4. Pedagogical Scaffolding — 5: examples do real teaching, each step earns the next, transferable;
   3: examples decorative or under-explained; 1: filler or absent.
5. Grounding Fidelity — 5: every load-bearing claim grounded and the citation truly supports it;
   3: grounded overall but one citation is a stretch; 1: fabricated/mismatched or ungrounded claims.

For EACH version, output a table: dimension | score | one-line justification that QUOTES a specific
passage. A justification with no quote = that dimension is discarded. Then the total out of 25.
Output nothing else — no overall verdict, no comparison, no preamble. Just the two tables and totals.

=== VERSION A ===
{{PASTE VERSION A — attribution stripped}}

=== VERSION B ===
{{PASTE VERSION B — attribution stripped}}
```

## After 3 runs
Average each dimension across runs for each version; sum to a /25 per version; compute A−B deltas;
report the per-version inter-run spread. Unblind via the operator's mapping. Apply the
`PILOT-SPEC.md` decision rule. Record in `pilot-M3-scores.md` and append the verdict to `FINDINGS.md`.

## Why this is a gate, not a vibe
It is blind (no attribution), paired (same module), pinned (fixed model + prompt + rubric),
pre-thresholded (the pass/fail number is set in the spec before scoring), and repeated (3 runs with a
reported spread, so a noisy judge is caught rather than trusted). That is the difference between a
ceiling *gate* and an "it reads worse to me" rationale — which is the whole point of the ECP frame.
```
