# M6 VERIFY ledger — Module 6, Agent Artifacts (build-guide prose)

The CODE passed the BUILD→TEST gate separately (`build-test/SUMMARY.md`). VERIFY (2 subagents, connector +
WebFetch) checked the build-guide PROSE: platform-binding claims, STYLE, and **guide-matches-scaffold**. All 4
guides PASS. Zero markers remain in student-facing text. Per-guide verdicts: this folder.

## Per guide
- **01 Terminal Coding Agent** — Claude Agent SDK tool-use loop confirmed; Azure AI Foundry Run/Run-Steps
  mapping confirmed (MS Learn); model IDs/pricing confirmed (`claude-opus-4-8` $5/$25 MTok, not hardcoded).
  **Defect fixed:** build step mislabeled component 22 (JSON-RPC) as the dispatcher (23). Gate re-run: 6 passed.
- **02 Production RAG Chatbot** — Azure AI Search hybrid retrieval (BM25+vector, RRF) confirmed (MS Learn);
  Docling claims match the repo + M5 lesson-11; the `VectorIndex` Protocol seam (Azure AI Search ↔ local index,
  one constructor) confirmed against the scaffold. SLO expanded on first use. Gate re-run: 5 passed.
- **03 Real-Time Voice Assistant** — Pipecat core classes + all five service import paths verified against the
  repo; ~450–600 ms budget carried from M4. **3 guide-vs-scaffold drifts fixed:** the guarded-import set
  (Pipecat + Deepgram/Anthropic/Cartesia, not LiveKit/numpy), the `VOICE_BUDGET_MS` config wording, and the
  named cascade-vs-direct (MultimodalAgent vs VoicePipelineAgent) comparison. Gate re-run: 9 passed.
- **04 Issue-to-PR Agent** — GitHub webhook events / Actions run-status API / fine-grained PAT scopes confirmed;
  EU AI Act Art. 14 confirmed and not overstated; the load-bearing "cannot merge" claim verified true in code
  (`git_ops.py` has no `merge()`). HITL expanded on first use. Gate re-run: 4 passed.

## Cross-cutting
- **Guide-matches-scaffold** confirmed for all 4 (the described build sequence, operator surfaces, and file
  names exist in the runnable code) — the prose can't drift from what ships.
- **Dry-run-first** honored: every guide frames local-first, cloud opt-in; `_prereqs/CLOUD-SETUP.md` written.
- **mdbook build PASS** with all 4 guides live.
