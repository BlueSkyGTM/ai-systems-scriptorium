# VERIFY verdict — 02-reference-architectures.md

Subagent: Sonnet VERIFY (M8 capstone guides). Gate: guide prose (claims, STYLE, coherence).

## Coherence check (a) — CATALOG ACCURACY (the heart of this guide)

Source of truth: `synthesis/source/module4/asdg-module4-case-studies.md` (the 20 Ch16 case studies),
cross-checked against the underlying case-study files in
`synthesis/raw/ai-system-design-guide/16-case-studies/`.

**Numbers, names, architecture types, what-you-replicate — all 20 rows match the source** (faithful
condensations of the source wording; e.g. #03 architecture "Ensemble verification" = source "Ensemble
verification pipeline"; #04 "IDE code-generation service" = source "IDE-integrated code generation service").
No numbering drift, no renamed case study, no mis-typed architecture.

**Seam column — intentionally and correctly transformed.** The source "Seam" column is in fact a
Build/Both phase marker ("Build"/"Both"), NOT an architectural seam. The guide replaces it with a genuine
architectural seam per case study. Every derived seam was validated against the actual case-study source:

| # | Guide seam | Grounded in source |
|---|-----------|--------------------|
| 01 | Permission filter on retrieval | "permission-filtered vector search" | ✓ |
| 02 | The confidence gate to a human | "confidence-gated ... with escalation" | ✓ |
| 03 | The verification panel | panel-of-judges quality gating, fact verification | ✓ |
| 07 | The test-gated loop | "sandboxed test-gated self-correction" | ✓ |
| 08 | The isolation boundary | "Absolute data isolation ... WHERE tenant_id = X" | ✓ |
| 11 | The explanation cache | "cached LLM explanations" | ✓ |
| 12 | The audit trail | "full audit logging" | ✓ |
| 13 | The on-prem boundary | "On-prem voice-to-EHR" | ✓ |
| 16 | The isolation + approval tiers | "Firecracker isolation ... two-tier human approval" | ✓ |
| 17 | Eval-gated promotion | "eval-gated promotion" | ✓ |
| 18 | The statistical eval gate | "statistical correction ... before a merge button appears" | ✓ |
| 20 | The trust boundary | OAuth audience binding, STDIO sandboxing, IPI trust-tagging | ✓ |

(Remaining rows 04/05/06/09/10/14/15/19 likewise grounded — no fabricated seam.)

**Track groupings — sound.** eval-gated CI/CD = #18/#19/#17; multi-tenant RAG = #08/#01/#12/#15;
agentic = #07/#09/#16/#20. Anchors match PLAN.md and spec.py. The "canonical one" calls (#18, #08, #07)
are correct. The "outside this fleet's reach" note (fraud #14 sub-100ms, voice #13 on-prem ASR,
recommendation #11 ANN index) is accurate against the source constraints.

Coherence check (a): **PASS — catalog is accurate.**

## Coherence checks (b) and (c)
- (b) Rubric == checker — guide states each case study "carries a seam ... that seam is what the rubric grades"; consistent with rubric R6 PROBLEM-FRAMED (spec names track + ref arch). CONSISTENT.
- (c) Runbook == surfaces — N/A (no operator surfaces described in 02).

## Claim ledger
| # | Claim | Source | Result |
|---|-------|--------|--------|
| 1 | "twenty production architectures, distilled from Chapter 16" | asdg source (20 case studies, Ch16 extract) | VERIFIED |
| 2 | #07 is "the one the sample spec replicates" | sample_spec.md (#07) | VERIFIED |
| 3 | "a multi-tenant RAG version leans on sharding" / eval-gated leans on caching golden-set | standard architecture mapping; consistent with 03 vocab note | VERIFIED |

No platform markers; no unsourced external claims.

## STYLE result
- H1 `# Reference Architectures`. ✓  Seam lead: "You do not invent the system you build for the exam. You replicate one." — hooks, present, second person. ✓
- `## Core concepts` present (3 propositions). ✓
- Unity: second person + present tense; no "we"/"the student". ✓
- Catalog-table acronyms (ASR/NER/EHR/FHIR/ANN/LoRA/OAuth/STDIO/IPI/MCP) retained inside the table as faithful source reproductions (STYLE §6 + catalog fidelity); body prose uses plain glosses. Acceptable.
- No banned template ending. Closer — contrast: "the difference between a portfolio that says *I can design a system* and one that says *I read a real design and shipped a version that holds the line that matters.*" — varied shape, lands. ✓

## FLAGGED
- None.

## VERDICT: PASS
Catalog is accurate to the source on every axis; the seam column is a correct, source-grounded
transformation of the source's phase marker. STYLE clean. No fixes required.
