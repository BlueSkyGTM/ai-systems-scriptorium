# GLM Extractor — 100-exercises-to-learn-rust

Repo-specific extractor for the **100 Exercises to Learn Rust** repo (Module 1 — Rust language foundation). Self-contained; sibling skills in the other sub-repos have different shapes — do not reuse them.

**Operating principle:** Claude orchestrates, GLM writes. Rust is taught as the **serving layer / CLI tooling / concurrency-async substrate** for the AI course — frame seam relevance accordingly.

## 1. Repo shape (important quirk)
- `exercises/NN_topic/NN_section/` — code only (`Cargo.toml` + `src/`), **NO README**. The problem statements live in the **book**.
- `book/src/NN_topic/NN_section.md` — the mdBook narrative; `book/src/SUMMARY.md` is the TOC mapping every section → topic (1:1 with exercise folders).
- `helpers/` — supporting crates (`common/`, `ticket_fields/`) + `json2redirects.sh`.
- 8 topics: 01_intro, 02_basic_calculator, 03_ticket_v1, 04_traits, 05_ticket_v2, 06_ticket_management, 07_threads, 08_futures (98 exercises). **No antilibrary** (all topics curriculum). **No images, no Mermaid.**

## 2. Runner (`extract.py`)
- `single` — one GLM call from a blob (inventory, book structure, curriculum map).
- `topics` — fan out per `book/src/<NN_topic>/`, concatenating all `*.md`, → per-topic summary (Rust concepts + seam relevance), assembled in order.

```bash
python3 skills/glm-extractor/extract.py topics --topics-dir book/src \
  --out output/content/module1-rust-exercises-by-topic.md --instr-file I.txt --header-file H.txt
python3 skills/glm-extractor/extract.py single --user-file BLOB.txt --out output/FILE.md
```

## 3. API config (universal)
`glm-5.1` (`GLM_MODEL` to override), coding endpoint `/api/coding/paas/v4/chat/completions`, coding-plan key, **no second keys**. Traps: `1113` on a general endpoint = model-not-in-plan; glm-5.x reasoning → `thinking` disabled (baked in). RPM `1302` → 6 workers + 1.3s throttle.

## 4. Targets
| # | Output | Mode |
|---|---|---|
| 1 | `output/inventory.md` | single — table (topic # \| name \| sub-exercises \| seam note) + **Helpers** section (T5) |
| 2 | `module1-rust-book-structure.md` | single — from `SUMMARY.md` + topic intros: chapter list, concept, exercise numbers |
| 3 | `module1-rust-exercises-by-topic.md` | topics — 8 sections: concepts + why it matters for AI Systems (serving/CLI/concurrency/async) |
| 4 | `output/curriculum-map.md` | single — topic \| Rust concept \| Sans-Python use case \| module (08_futures → async tool calls/agents) |
| — | `output/antilibrary.md` | single/mechanical — **expected empty**; note "no antilibrary; all 8 topics are curriculum" |
| 6 | `output/visuals/diagrams.md` | mechanical — "no visuals found" (no images, no Mermaid) |

## 5. Verify
8 topic sections; inventory has 8 topic rows + helpers; book structure covers all topics; no FAILED markers; no empty files. Mark Done Checklist with verified counts.

## 6. Manifest
```
skills/glm-extractor/
├── SKILL.md
└── extract.py   (single | topics)
```
