# Exercise 13 — Design Patterns and Anti-Patterns

**Goal** — Produce a pattern audit of the `module3-agent/` harness: identify which patterns are present, which anti-patterns exist or are one missed line away, and what a production-ready version would add.

**Why** — Naming the pattern in live code — with file and line — is the skill that separates an architect from a reader; this exercise builds that muscle before Module 4 introduces multi-agent complexity.

**Steps**

1. Read `module3-agent/` in full — the harness files from lessons 01–11.
2. Produce `module3-agent/PATTERN_AUDIT.md` with three sections:

   **Patterns present** — for each pattern from lesson 13 you find in the code, name it, cite the file + approximate line, and state what problem it solves in this specific harness.

   **Anti-patterns present or latent** — for each anti-pattern you find (or that would appear if one guard were removed), name it, explain what triggers it in this harness, and estimate the cost (token waste, runaway loop, silent regression) if the system ran in production without the fix.

   **What a production-ready version adds** — list three concrete additions (not vague improvements), each in one sentence. Each must address a specific anti-pattern from lesson 13. If `module3-agent/` already has all three, find three more from the broader catalog.

3. Verify your audit covers at minimum: the turn budget and kill switch (infinite loop guard), the observation formatter (God Prompt surface inside the loop), the stop condition (done-detection), and the absence or presence of a Golden Set.

**Done when**

- `PATTERN_AUDIT.md` exists with all three sections populated.
- Every "Patterns present" entry cites a specific file and line (not a general description).
- Every "Anti-patterns present or latent" entry includes a one-line cost estimate grounded in what the harness actually does, not a hypothetical.
- At least one "What production adds" entry references a pattern from the catalog (not an anti-pattern fix) that the harness does not yet implement.

**Stretch** — Pick the highest-priority anti-pattern from your audit and fix it: write the code, run the harness, and show that the fix is testable (add one assertion or print that proves the guard is active).
