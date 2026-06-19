# VERIFY verdict — Lesson 09: Guardrails: Constitutional AI & Llama Guard

**Lesson:** `build-stages/m4/output/author/09-guardrails.md`
**Verifier:** Sonnet VERIFY subagent (M4 ch02 Op-Safety, safety-critical — verified hardest)
**Date:** 2026-06-19

## Markers resolved (3 of 3)

| Marker | Source checked | Result |
|---|---|---|
| `[verify: Anthropic — Constitutional AI / the Claude constitution / four-tier priority]` | WebSearch + Anthropic Jan 2026 constitution coverage (Dataconomy, CIO, BISI, Oxford; the constitution PDF) | **FIXED → removed.** Four tiers confirmed: safety/oversight → ethics → **Anthropic's guidelines** → helpfulness. Hardcoded prohibitions (bioweapons, CSAM, critical-infra) vs operator-adjustable defaults confirmed as a *separate* axis. See DEFECT below. |
| `[verify: Meta — Llama Guard 3 / Llama Guard 4 / MLCommons hazard taxonomy]` | WebSearch Meta/HuggingFace Llama Guard 4 model card | **PASS → removed.** Llama Guard 4 = 12B multimodal classifier aligned to the MLCommons hazard taxonomy, categories S1–S14 incl. S14 Code Interpreter Abuse. Added "12B multimodal" + "MLCommons hazard taxonomy" precision. |
| `[verify: Emoji Smuggling — "Bypassing Prompt Injection and Jailbreak Detection" / 100% ASR on six guard systems]` | WebFetch arxiv.org/html/2504.11168v3 + abstract | **PASS (confirmed exactly) → removed.** Six guard systems (Azure Prompt Shield, ProtectAI v1/v2, Meta Prompt Guard, NeMo Guard Jailbreak Detect, Vijil Prompt Injection); paper: "The most successful attack was Emoji Smuggling, which achieved a 100% ASR for both prompt injections and jailbreaks" — 100% against all six. Reworded to name the study + three example systems and assert "100% against all six" (now stronger AND verified, not softened). |

## DEFECT found + fixed

- **Constitutional four-tier third tier was WRONG.** Draft said tier 3 = "**Operator guidelines** — the deploying organization's rules." The real Jan 2026 constitution's third tier is "**compliant with Anthropic's guidelines**" — the *model developer's* rules, not the operator's. The draft conflated the tier (Anthropic's guidelines) with the separate hardcoded/operator-adjustable hardness split. The Ph15 source extract (L17) also says "Anthropic guidelines." Fixed the ordered list (tier 3 → "Anthropic's guidelines — the model developer's rules for the model"), added "Separate from this ordering" to the hardness-split transition, and corrected the matching Core-concepts bullet. The hardcoded-prohibition / operator-adjustable-default content was already correct and is retained.

## Claim ledger

| Claim | Source | Verdict |
|---|---|---|
| Two guardrail shapes: trained-in (Constitutional AI) vs runtime classifier (Llama Guard) | Ph15 L17 + L18 | PASS |
| Reason-based (not rule-based) alignment; written constitution; four-tier priority | Ph15 L17 + Jan 2026 constitution coverage | PASS |
| Four tiers: safety/oversight → ethics → Anthropic's guidelines → helpfulness | Jan 2026 constitution (safety, ethics, compliant-with-Anthropic's-guidelines, helpfulness) + Ph15 L17 | FIXED → PASS |
| Hardcoded prohibitions (bioweapons uplift, CSAM, critical-infra) un-overridable | Ph15 L17 verbatim + constitution coverage ("hard constraints… bright lines") | PASS |
| Operator-adjustable defaults (length, scope, style, tool patterns) within bounds | Ph15 L17 verbatim ("soft-coded defaults… operator-adjustable within bounds") | PASS |
| Honest limit: relies on the model generalizing principles to unanticipated situations | Ph15 L17 verbatim | PASS |
| Llama Guard 3/4 = separate runtime classifier, input + output | Ph15 L18 | PASS |
| Llama Guard 4 covers S1–S14 incl. S14 Code Interpreter Abuse; MLCommons taxonomy; 12B multimodal | Ph15 L18 + Meta model card | PASS |
| Emoji Smuggling = 100% ASR vs six guard systems (Huang/arXiv 2504.11168, 2025) | Ph15 L18 + arXiv 2504.11168v3 (confirmed against all six) | PASS |
| Caveat: a classifier is a layer, not a solution; stacking classifiers still beatable | Ph15 L18 ("classifiers are a layer, not a solution") | PASS |
| Resolution: layer probabilistic guardrails on top of deterministic limits (budget/kill-switch/HITL from L06–08) | PLAN safety spine + de-dup; chapter through-line | PASS |
| `classifier.py` input/output rail code | Self-consistent illustrative screening shape | PASS |

## STYLE result — PASS

- Single H1, present tense, 2nd person, one voice. ✓
- Lead: states the problem (content governance + false confidence) and the lesson's two jobs; cusp implicit (alignment is AI-Engineer, the deterministic-limit posture is MLOps). ✓
- One `## Core concepts` block, 4 testable propositions (tier-3 bullet corrected). ✓
- Handoff div well-formed. ✓
- Ending ("the limits that don't bend are why it still can't spend your money or drop your table"): consequence shape, callbacks to L06–08; not the banned template; varied vs. siblings. ✓
- Acronyms: ASR no longer appears bare ("attack-success rate" / "attack-success" in prose + concepts); CSAM expanded. ✓
- De-dup: explicitly leans on budgets/kill-switch/HITL "from lessons 06 through 08" as the hard layer; does not re-teach them. ✓

## Antilibrary fence — PASS
No frontier-safety/policy material (no RSP/FSF/Preparedness/STaR/DGM/AlphaEvolve/METR/CAIS). The lesson stays on operational guardrails (Constitutional AI as a *product* alignment mechanism + runtime classifiers), not the research/policy half. ✓

## Overall verdict: **PASS** (3 markers resolved, 1 DEFECT FIXED [constitutional tier-3: Operator → Anthropic's guidelines], 0 FLAGGED — Emoji Smuggling confirmed exactly, no softening needed). Ship-ready.
