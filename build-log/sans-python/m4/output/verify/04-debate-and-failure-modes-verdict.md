# VERIFY verdict — Lesson 04: Debate & Multi-Agent Failure Modes (MASFT)

**Lesson:** `build-stages/m4/output/author/04-debate-and-failure-modes.md`
**Verifier:** Sonnet VERIFY subagent (M4 ch01 Multi-Agent & Swarms)
**Date:** 2026-06-19

## Markers resolved (4 of 4)

| Marker | Source checked | Result |
|---|---|---|
| `[verify: multi-agent debate — Du et al., "Improving Factuality and Reasoning…through Multiagent Debate"]` (line 7) | WebFetch: arxiv.org/abs/2305.14325 | **PASS → removed.** Confirmed: Du, Li, Torralba, Tenenbaum, Mordatch; "multiple language model instances propose and debate… over multiple rounds"; improves factuality and reasoning, reduces hallucinations. Paper title woven into prose. |
| `[verify: debate topology cost — sparse vs full-mesh critique counts, Du et al. / MultiAgentBench]` (line 15) | Synthesis source `aefs-module3-agent-engineering.md` §25 | **PASS → removed.** Verbatim match: "Sparse topology (star/ring/hub-and-spoke) matches full-mesh accuracy at lower token cost (star N=5,R=3 = 12 critique ops vs full-mesh 60)." Draft's "twelve instead of sixty" is exact. |
| `[verify: MASFT — Cemri et al., "Why Do Multi-Agent LLM Systems Fail?"]` (line 21) | WebFetch: arxiv.org/abs/2503.13657 + arxiv.org/html/2503.13657v1 + WebSearch | **FIXED → removed.** 14 modes / 3 categories / κ=0.88 / 1600+ traces all confirmed. Added "(MAST in the paper itself)" — the paper's own abbreviation is **MAST**, not MASFT. |
| Lead failure-rate claim "between 41% and 87% across real benchmarks" (line 3, implicit verify) | arxiv.org/html/2503.13657v1 (full-text search) + WebSearch | **FIXED.** The paper contains **no** "41" or "87"; the lowest correctness it reports is ChatDev "as low as 25%." The 41–87% range is a *secondary-source* framing (Berkeley work; upper bound is actually 86.7%, not 87), not a paper claim. Reworded to the verified ChatDev 25% figure + the conservative "failure rates well above 40%." |

## Claim ledger

| Claim | Source consulted | Verdict |
|---|---|---|
| Debate ("society of minds"): N propose, then critique/revise over R rounds to converge | Du et al. abstract; aefs §25 | PASS |
| Beats single-model zero-shot on factuality, rule-following, reasoning | Du et al. abstract; aefs §25 | PASS |
| Agent count and round count contribute independently | aefs §25 framing; draft's nuance is editorial but consistent with the paper's ablations | PASS |
| Cross-model debate beats single-model monoculture (decorrelated errors) | aefs §25: "cross-model debate beating single-model" | PASS |
| Sparse (star/ring) matches full-mesh accuracy at a fraction of cost; star N=5,R=3 = 12 ops vs 60 | aefs §25 (verbatim) | PASS |
| Topology is a cost knob, not just a correctness knob | Editorial generalization; sound | PASS |
| MASFT/MAST: 14 modes, 3 categories, κ=0.88, 1600+ traces | arXiv 2503.13657 abstract + aefs §26 | PASS |
| Three families: Specification ~42%, Coordination ~37%, Verification ~21% | WebSearch (MAST per-mode figures): Specification & System Design **41.8%**, Inter-Agent Misalignment **36.9%**, Task Verification & Termination **21.3%** | PASS — rounds to 42/37/21 exactly. (Official names: FC1 Specification & System Design Failures, FC2 Inter-Agent Misalignment, FC3 Task Verification & Termination; the draft's plain-language labels are faithful renderings.) |
| Five recurring modes: hallucinated actions, scope creep, cascading errors, context loss, tool misuse | aefs §26 (verbatim five) | PASS |
| "Design flaws, not model limitations; a better model doesn't fix them" | aefs §26: "fundamental design flaws, not LLM limitations fixable with better base models" | PASS |
| Failure rate: lowest correctness ~25% (ChatDev); field reports well above 40% | MAST html ("can be as low as 25%"); secondary 41–86.7% framing | **FIXED** (was unsourced "41%–87%") |
| Each MASFT family maps to a back-half governance answer | PLAN safety spine; editorial | PASS |

## STYLE result — PASS

- H1 single; second person, present tense, one blunt voice. ✓
- Seam-framed lead (line 3): the failure-rate shock → "it's the wiring, not the model"; grabs, no throat-clearing; now anchored to the verified 25% figure. ✓
- One `## Core concepts` block (3 propositions, percentages verified). ✓
- `claude-handoff` div well-formed (opens "Try it in Claude Code"). ✓
- Ending (line 47): "The model is not the variable you control. The system around it is." — reframe shape, not the banned template; distinct from siblings. ✓
- Acronyms: MASFT expanded in body (Multi-Agent System Failure Taxonomy); MLOps standard. ✓
- "You don't need to memorize fourteen" + the 5-item list respects reader stamina (STYLE §8). ✓

## Overall verdict: **FIX-APPLIED** (4 markers resolved, 1 unsourced-number defect corrected; 0 FLAGGED). Ship-ready.

### Note for Opus (naming, module-wide — not blocking)
The paper's own abbreviation is **MAST** (Multi-Agent System Failure Taxonomy). The course (PLAN title, this lesson's H1/headings, and aefs source) uses **MASFT**. I kept the course's "MASFT" for internal consistency and added a one-clause parenthetical noting "MAST in the paper itself" so a student who looks it up isn't misled. If you want the whole module standardized to the paper's MAST, that's a global find/replace decision above this lesson's pay grade — flagging, not changing.
