# GLM Extractor — ai-performance-engineering

Repo-specific extractor for the **AI Performance Engineering** O'Reilly book repo. Self-contained: this folder is the skill. Sibling skills exist in the other sub-repos (lesson folders / Python project / markdown chapters) — different shapes, do not reuse them.

**Operating principle:** Claude orchestrates, GLM writes. **Seam = inference serving only.** Students deploy and benchmark; they do NOT write GPU kernels.

---

## 1. The seam & chapter classification (the key editorial call)

20 chapters. The book spans GPU performance broadly; the curriculum keeps only the **inference-serving** subset.

- **KEEP (Module 4 — inference serving):** `ch15` Disaggregated Inference & KV Management · `ch16` Production Inference Optimization · `ch17` Disaggregated Prefill/Decode & Routing · `ch18` Advanced Attention & Decoding · `ch19` Dynamic & Adaptive Inference Precision/Memory · `ch20` AI-Assisted Performance Optimization & Case Studies.
- **ANTILIBRARY (training/CUDA/kernels):** `ch01–ch14` — performance fundamentals, GPU hardware, system tuning, distributed/multi-GPU, storage/IO, CUDA programming, memory access, occupancy/warp, arithmetic intensity/kernel fusion, tensor cores, streams, CUDA graphs, PyTorch profiling internals, compiler/Triton. (`ch13`/`ch14` are framework/kernel optimization — pre-serving, kernel-writing — so antilibrary.)

---

## 2. Repo shape → why this runner

| Target | Nature |
|---|---|
| Inventory, antilibrary one-liners | **GLM `single`** |
| Keep-chapter READMEs (concepts + tasks + full README) | **GLM `chapters`** (per-chapter concepts/tasks block + verbatim README via `--append-readme`) |
| Docs, FULL_SWEEP checklist | **MECHANICAL `passthrough`** — "full content preserved" / "as-is" means verbatim, NOT summarized |
| Code files | **Never extracted** (students use the real files) |
| Visuals | **None to collect** — keep-chapter READMEs + docs reference **0 images** and contain **0 Mermaid**. (The 260 `img/` files are bulk; only referenced ones would be copied, and none are referenced in keep content.) |

So `extract.py` has three modes: `single`, `chapters`, `passthrough`.

---

## 3. API config (universal — same key/plan across all sub-repos)

- **Model:** `glm-5.1` (`GLM_MODEL` to override). **Endpoint:** `https://api.z.ai/api/coding/paas/v4/chat/completions`. **Key:** coding-plan (`3ee9e7...`). **No second keys.**
- **Trap 1:** `1113` on a general endpoint = model-not-in-plan, not no-balance (this key only works on `/api/coding/`).
- **Trap 2:** glm-5.x are reasoning models → `"thinking":{"type":"disabled"}` or content is empty. Baked into `call_glm`.
- **Bottleneck:** RPM limit `1302` → `chapters` mode runs 6 workers behind a ~1.3s min-interval gate + jittered 8-retry backoff. Raise `MIN_INTERVAL` if `1302` appears.

---

## 4. Runner usage

```bash
# single: one blob -> one doc
python3 skills/glm-extractor/extract.py single --user-file BLOB.txt --out output/FILE.md [--max-tokens 3000]

# chapters: per-chapter concepts/tasks block (+ verbatim README)
python3 skills/glm-extractor/extract.py chapters \
  --chapter-dir code/ch15 code/ch16 code/ch17 code/ch18 code/ch19 code/ch20 \
  --out output/content/module4-inference-serving-chapters.md \
  --instr-file INSTR.txt --header-file HEADER.txt --append-readme [--max-tokens 1200]

# passthrough: verbatim concat under per-file headers (no GLM)
python3 skills/glm-extractor/extract.py passthrough \
  --file docs/tooling-and-profiling.md docs/appendix.md docs/environment.md docs/gb300-nvfp4-dual2sm.md \
  --out output/content/module4-inference-reference-docs.md --header-file HEADER.txt
```

---

## 5. Targets

| # | Output | Mode |
|---|---|---|
| 1 | `output/inventory.md` | single — 20-chapter table (chapter \| title \| KEEP/ANTILIBRARY \| file count) + docs listing |
| 2 | `module4-inference-serving-chapters.md` | chapters (ch15–20, `--append-readme`) — concepts + hands-on tasks + verbatim README |
| 3 | `module4-inference-reference-docs.md` | passthrough — `docs/*.md` verbatim |
| 4 | `module4-full-sweep-checklist.md` | passthrough — `code/FULL_SWEEP.md` verbatim |
| 5 | `output/antilibrary.md` | single — ch01–14, title + one-line why-antilibrary |
| 6 | `output/visuals/diagrams.md` | mechanical — log "no visuals collected" (no refs, no Mermaid) |
| — | `output/curriculum-map.md` | single — seam mapping to Module 4 |

Also note `code/TODO.md` + `code/BOOK-ERRATA.md` in inventory (known gaps).

## 6. Verification — never trust "done"
Keep-chapter sections = 6; docs passthrough = all 4 files verbatim (byte-compare); FULL_SWEEP verbatim; antilibrary = 14 chapters; no FAILED markers. Mark the Done Checklist only with verified counts.

## 7. File manifest
```
skills/glm-extractor/
├── SKILL.md      ← this spec (ai-performance-engineering)
└── extract.py    ← runner: single | chapters | passthrough
```
