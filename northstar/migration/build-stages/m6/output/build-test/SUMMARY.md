# M6 BUILD→TEST gate ledger — Module 6, Agent Artifacts

The runnable code gate that begins at M6. Each artifact's scaffold was run **locally, offline, stdlib-only**
(deterministic mock LLM; no Docker, no cloud, no GPU). Re-run and confirmed by Opus, not just self-reported.

| Artifact | `python smoke.py` | `python -m pytest tests/` | Operator surfaces exercised |
|---|---|---|---|
| 01 terminal-coding-agent | exit 0 (read→fix→run_tests→verify ACCEPT; $0.04 / 4 turns) | **6 passed** | cost ceiling stops on breach; kill-switch halts (agent has no write handle); verify gate REJECTs a bad patch |
| 02 production-rag-chatbot | exit 0 (ingest→index→cited answer; guardrail block; eval precision 1.00 / faithfulness 0.83 PASS) | **5 passed** | guardrail blocks unsafe query; drift metric logged; acceptance gate fails a low-faithfulness answer |
| 03 realtime-voice-assistant | exit 0 (turn completes; budget gate bites; barge-in cancels mid-turn) | **9 passed** | latency budget enforced (flags a blown budget); barge-in kill-switch cancels in-flight turn |
| 04 issue-to-pr-agent | exit 0 (issue→branch→fix→local CI→PR artifact, **no merge**) | **4 passed** | scoped creds refuse out-of-scope/merge; kill-switch halts before spend; CI-verify defaults REJECT → escalates; never auto-merges |

**Total: 4/4 smoke PASS, 24/24 tests PASS.** Toolchain: Python 3.12 + pytest 9.1.1; `npx tsc --noEmit` available
(no TS in these scaffolds). No `cargo`/Docker needed. Stdlib-only smoke paths confirmed (third-party imports —
anthropic/docling/faiss/pipecat — guarded behind `try/except ImportError` with deterministic fallbacks).

The gate proves the artifacts **run**, not just render — the difference the M6→M8 portfolio bar depends on.
