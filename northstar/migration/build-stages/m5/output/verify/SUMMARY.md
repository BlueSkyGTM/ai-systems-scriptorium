# M5 VERIFY ledger — Module 5, Deploy & Performance Engineering

VERIFY ran as a 6-subagent fleet (one per chapter), each resolving markers via the MS Learn connector +
WebFetch, source-checking against `synthesis/source/module4/` (+ live docs for Docling/MLflow/PEFT/Rust),
and full-reading against STYLE. **All 15 lessons PASS. Zero residual markers.** Per-lesson verdicts: this folder.

## Defects caught and fixed
- **L01** — TGI release date tightened ("late 2025" → "December 2025"); removed an unsupported "patches the host" Azure ML claim → blue/green framing.
- **L02** — reframed the 4.16× continuous-batching figure as illustrative (one microbenchmark, not a target); confirmed PagedAttention <4% waste / 60–80% naive waste *verbatim* against the vLLM source.
- **L03** — generalized a single-source domain acceptance number out of prose; un-jargoned "ITL"; quantization-format map confirmed.
- **L04** — TTFT/TPOT reference numbers (162 ms / 7.3 ms) reframed as one-benchmark illustrations, "measure your own hardware" kept; load-test GIL-trap wording tightened.
- **L05** — GPU non-determinism rewritten with the precise mechanism (non-associative FP + non-batch-invariant kernels); APIM `llm-token-limit` policy name verified.
- **L06** — **OTel `gen_ai.*` attribute names verified against the real semconv registry**; added the two real attribute names the draft described generically; noted `gen_ai.system → gen_ai.provider.name` deprecation (not used, no fix needed).
- **L07** — compliance discipline held: no statutory dates/fines shipped; Key Vault/Managed Identity/Azure Policy claims confirmed.
- **L08** — batch-API ~50% discount confirmed (OpenAI + Anthropic); Foundry per-project cost attribution noted as Preview; **banned "The platform engineer who…" ending rewritten** (Opus, at SHIP).
- **L09–L10** — every perf delta verified **exact-to-source** (15.65× / 23.53× / 7.07× / 6.11× / 5.07× / 4.16× / 1.78×); NVLink 1.8 TB/s triple-confirmed (source + NVIDIA + MS Learn); inference-only confirmed (no training/CUDA leak from the 200-item appendix); **2 missing exercise briefs written**.
- **L11** — every Docling claim grounded in the repo/docs; removed an unverified GraniteDocling CLI claim; HybridChunker behavior matched verbatim.
- **L12** — MLflow API confirmed; "stages → aliases" deprecation fixed.
- **L13** — PEFT/LoRA/QLoRA confirmed (incl. the "65B on a 48 GB GPU" figure, verbatim in PEFT docs); **literacy-depth confirmed** (no training loop; deep build routed to antilibrary → Avec Python).
- **L14** — removed an invented "50 ms GC pause" figure (perf kept qualitative); fixed a `Result` example's error variant.
- **L15** — the "futures are inert/lazy" claim verified against the async book and reworded to its exact phrasing; tokio facts (work-stealing default, `JoinHandle`, `Semaphore`, `timeout`, `'static`+`Send`) confirmed.

## Cross-cutting
- **Perf-number discipline (M4-ch04 rule) held:** every throughput/latency/bandwidth figure checked; single-source numbers reframed as illustrative with a measure-it-yourself gate.
- **Cross-module cohesion confirmed:** M3 lesson-10 KV-cache payoff (L02), M2-eval inner→outer loop (L04–06, L12), M4 budget→FinOps (L08).
- **mdbook build PASS** with all 15 M5 lessons live (M1–M5 render together).

## Carried flags (for M1/M2 reconciliation, not blocking M5)
- The "~73% retrieval-failure" figure is shipped in M2 (`03-rag-system.md`) and back-referenced in M5 L11; both hedged "roughly," provenance is industry-commentary. Rule on attribution across both lessons together at reconciliation.
