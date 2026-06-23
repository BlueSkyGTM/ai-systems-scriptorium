# Module 5 — The Eval Pipeline — Build Plan

Status: **PLAN LOCKED 2026-06-22** (self-cleared; W&M M3-M8 straight-through). Fifth stage.

## The stage in one line

M4 produced a trained adapter checkpoint; M5 asks whether it is any good. This module
builds the eval pipeline: four task-level metrics, a weighted aggregate, and a gate script
that promotes or blocks a checkpoint based on whether the tuned model beats the baseline.

## The locked decision: teach eval as a gate, not a report

Loss curves are not eval. The deliverable is `eval_gate.py`: a script that exits 0 (PASS)
or 1 (BLOCK) based on whether the tuned model outscores the baseline on a held-out set by
at least a margin. Four metrics cover four dimensions loss misses: exact-match (string
correctness), token F1 (lexical overlap), perplexity (language model fit), mock_judge
(deterministic quality proxy). MLflow and real LLM-as-judge are shown as REFERENCE ONLY.

## Locked decisions

1. Stage = module; `build-log/weights-and-measures/m5/`. Consumes M4's adapter; feeds M6
   (the tuned classifier artifact that ships with an eval gate).
2. STYLE + STANDARDS; overview + 4 lessons + 4 exercises.
3. Grounded: aefs L36/41/49/73/75, aefs Phase 11 L10, mwml evaluate.py + test_behavioral.py,
   Azure ML eval docs, MLflow API docs.
4. CPU-verifiable: `eval_gate.py --selftest` exit 0; pure stdlib + math, no torch required.

## M5 split (overview + 4 lessons + 4 exercises)

| # | Lesson (slug) | The move |
|---|---------------|----------|
| 0 | `00-overview` | Eval as a gate; the four lessons; what feeds forward to M6/M7. |
| 1 | `loss-is-not-enough` | Why loss curves lie: four dimensions loss misses; the eval contract. |
| 2 | `task-metrics` | Exact match, token F1, perplexity: the math, edge cases, normalisation to [0,1]. |
| 3 | `llm-as-judge` | The mock judge (deterministic); the real judge (reference); rubric design; cost math. |
| 4 | `building-the-eval-gate` | Stitch metrics into a weighted aggregate; the baseline comparison; exit 0/1; MLflow reference. |

## Throughline

- `exercises/spine/eval_gate.py` — FREEZE-VERIFIED 2026-06-22 (28/28 selftest pass).
  Contains: normalize, exact_match, token_f1, mock_judge, perplexity_from_nll,
  normalise_perplexity, aggregate_scores, EvalResult, run_eval, mean_aggregate, eval_gate,
  --selftest, --demo CLI.
- `exercises/spine/check_loop.py` — unchanged at --module 4.

## Fleet

Haiku-fetch (aefs vault + live docs) DONE. Spine-engineer (Sonnet/conductor) DONE.
5 authors (Sonnet/conductor) + Opus review. VERIFY -> BUILD -> SHIP.
