# M2 — Retroactive VERIFY report

Stage: VERIFY (retroactive, run before M3 authoring per the locked plan). Gate: directive #4.
Date: 2026-06-19. Editor: Opus. M2 was already shipped; this pass closes the gap left by its
1-of-7 editorial read and zero MS-Learn validation.

## Method (the four directive-#4 checks)

- **(c) Full-read against STYLE** — all 7 lessons read in full by the editor (not a structural sweep).
- **(a) Source-verify** — every cited number/claim traced against `synthesis/source/module2/` (5 files)
  by a fact-check pass. ~94 claims checked: ~83 trace, 7 NOT-FOUND, 0 contradictions.
- **(b) Microsoft Learn validation** — the one named-tool factual claim (MLflow aliases) validated via the
  connector; API-shape claims (assistant prefill, prompt caching, structured output) validated via the
  `claude-api` skill.
- **(d) Build for real** — `mdbook build` (v0.5.3, installed this stage) exits 0, renders clean; no stray
  files; `book/` is gitignored.

## Defects fixed (4 edits)

| # | Lesson | Was | Now | Authority |
|---|--------|-----|-----|-----------|
| 1 | 01-prompt-engineering | "the model's prior output returns as an **assistant** prefill you can seed" / "survives a crafty assistant prefill" | assistant = prior replies / conversation history, lowest-trust tier; "outranks anything the assistant turn carries" | `claude-api` skill: last-assistant-turn prefill **400s** on Opus 4.6/4.7/4.8 + Fable 5. This was the known shipped defect. |
| 2 | 01-prompt-engineering | MLflow aliases `champion`, `challenger`, **`shadow`** | `champion`, `challenger`, **`staging`** | MS Learn: MLflow Prompt Registry uses version aliases; documented examples are `production`/`staging`/`development`, and `champion`/`challenger` are documented model-registry aliases. `shadow` is **not** a documented MLflow alias. |
| 3 | 02-context-engineering | "Anthropic requires explicit `cache_control` markers; OpenAI applies prefix caching automatically" | "Anthropic makes you opt in with a `cache_control` marker — on individual blocks, or one top-level marker that auto-caches the longest stable prefix; OpenAI caches automatically with no markers" | `claude-api` skill: Anthropic supports top-level auto-caching (auto-places on the last cacheable block), so "explicit markers" was stale. |
| 4 | 05-evaluation | "Score a set of ~100 human-labeled examples. Require Spearman ρ ≥ 0.7…" (unsourced numbers as a hard gate) | reframed as rules of thumb ("a hundred is a reasonable target"; "Spearman ρ around 0.7 or higher is a common bar") | Source-verify: neither figure traces to `synthesis/source`. Kept as heuristics (defensible), de-asserted as hard facts. |

## NOT-FOUND claims — disposition (directive #4a: trace, cut, or flag)

| Claim | Lesson | Disposition |
|-------|--------|-------------|
| MLflow `champion`/`challenger`/`shadow` aliases | 01 | FIXED (`shadow`→`staging`; MS-Learn validated). |
| Spearman ρ ≥ 0.7 hard threshold | 05 | FIXED (reframed as a heuristic). |
| "~100 human labels" | 05 | FIXED in the same edit (now "a hundred is a reasonable target"). |
| "78%→80% noise / 78%→91% real" | 05 | KEPT — explicitly illustrative ("likely noise"/"likely real"), teaches the significance-testing concept; appropriately hedged, not presented as cited data. |
| RRF formula `1/(rank+k)` | 03 | KEPT — the canonical RRF formula (Cormack et al.); correct standard knowledge though the source only names the technique. |
| FP16/ONNX "2–3x" cross-encoder speedup | 03 | KEPT/FLAGGED — technique is sourced; the multiplier is not, but is roughly accurate and hedged. Low risk. |
| Semantic cache ">30%" hit rate | 03 | KEPT/FLAGGED — sourced concept, unsourced specific benchmark; already hedged ("achievable"). Low risk. |

## Flagged for awareness (traces to source, but soft)

- **03: "RAG fails in retrieval roughly 73% of the time in enterprise deployments."** Traces to
  `asdg-module2-retrieval-systems.md §14`, so it passes source-verification — but it is a soft, widely-circulated
  industry stat with no primary citation. Not a production/API claim MS Learn can confirm. Acceptable as-shipped
  (it traces); consider attributing or softening in a future polish if a primary source can't be found.

## Per-lesson verdict

| Lesson | Verdict |
|--------|---------|
| 01-prompt-engineering | **SHIP** — 2 defects fixed (prefill, MLflow alias). |
| 02-context-engineering | **SHIP** — 1 staleness fixed (caching marker). All 15 claims trace. |
| 03-rag-system | **SHIP** — all numbers trace or are correct standard knowledge; 3 soft figures flagged, none false. |
| 04-advanced-rag | **SHIP** — clean; 15/15 claims trace. |
| 05-evaluation | **SHIP** — 1 reframe (Spearman/labels); illustrative figures kept. |
| 06-structured-output-and-tools | **SHIP** — clean; 16/16 trace; constrained-decoding characterization validated. |
| 07-the-complexity-ladder | **SHIP** — clean; 10/10 trace. |

**Stage verdict: M2 PASSES VERIFY.** The known prefill defect is fixed and the confidence-but-wrong risk
is closed. M3 authoring is unblocked. (Note: M3+ will emit per-lesson `output/verify/<lesson>-verdict.md`
files per hardening decision #2; M2's retroactive pass is consolidated here.)
