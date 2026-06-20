# CONTEXT — ML in Proportion (PLANNED)

A planned book covering the **machine-learning gaps** Sans Python set aside as Path-A (MLE) material:
classic ML fundamentals (regression, trees, boosting, AUC-ROC, feature engineering) **and the math they
actually require** (linear algebra / calculus / probability), at applied / point-of-use depth —
conceptual fluency for the ML-system-design interview, not from-scratch derivation.

**Scope call (recorded):** the *fundamentals* lead — they are the interview-relevant gap (row 3, medium
risk); the *math* (row 6, low applied risk) is included only where a fundamental needs it. This replaces
the narrower "Machine Learning Math" framing: math-only would be a thin book about the least-tested
layer. Sans Python stays the core roadmap; this branches from it. Origin: rows 3 + 6 of
`build-log/sans-python/antilibrary-gap-report.md`.

**Not started.** Starting it is gated at `GATE-NAME-BOOK` (propose the real title first).

## Ore (in the vault — not yet distilled)

- `ai-engineering-from-scratch` math + ML-fundamentals foundations; `made-with-ml` classic-ML chapters.
  Survey at process-ore time via `vault/MANIFEST.md`.

## Dual-use

Written to be **read by a human learner and ingested by an LLM** — dense, linked, plain markdown. The
same page serves either party.

## Load / don't-load

- **Load (when it graduates):** this folder's `README.md`, the named vault ore via `vault/MANIFEST.md`,
  `ingredients`, `platform/pipeline`.
- **Do NOT load:** the shipped book, other planned books.

## Handoff & gates

`GATE-NAME-BOOK` → process ore via `vault/CONTEXT.md` → `platform/pipeline/CONTEXT.md`
(`GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`). See `platform/HUMAN-GATES.md`.
