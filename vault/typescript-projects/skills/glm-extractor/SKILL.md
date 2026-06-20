# GLM Extractor — typescript-projects

Repo-specific extractor for **typescript-projects** (Module 1 — TypeScript language foundation; the product-layer language: APIs, agent orchestration, tooling). Self-contained; do not reuse sibling skills.

**Operating principle:** Claude orchestrates, GLM writes. Frame seam relevance toward **type-safe agent schemas, tool interfaces, MCP contracts, async LLM calls**.

## 1. Repo shape
- `projects/<topic>/README.md` — 15 topics (from the *Learning TypeScript* book): arrays, classes, configuration-options, declaration-files, from-javascript-to-typescript, functions, generics, interfaces, objects, syntax-extensions, the-type-system, type-modifiers, type-operations, unions-and-literals, using-ide-features. Each topic dir also has exercise code + tests.
- `test/files.test.ts`, `jest.config.js`, `package.json` — the test harness.
- `cover-conure.png` is the book cover (not a curriculum diagram). **No Mermaid, no topic diagrams.** **No antilibrary** (all 15 topics are curriculum).

## 2. Runner (`extract.py`)
- `single` — one GLM call from a blob (inventory, curriculum map).
- `topics` — fan out per `projects/<topic>/README.md` → per-topic summary (TS concepts + Sans-Python use case), assembled in order.

```bash
python3 skills/glm-extractor/extract.py topics --topics-dir projects \
  --out output/content/module1-typescript-topics.md --instr-file I.txt --header-file H.txt
```

## 3. API config (universal)
`glm-5.1` (`GLM_MODEL`), coding endpoint, coding-plan key, **no second keys**. Traps: `1113` general-endpoint = model-not-in-plan; glm-5.x reasoning → `thinking` disabled (baked in). RPM `1302` → 6 workers + 1.3s throttle.

## 4. Targets
| # | Output | Mode |
|---|---|---|
| 1 | `output/inventory.md` | single — table (topic \| description \| seam relevance) + **Test structure** section (T4: jest setup + 1 example test pattern) |
| 2 | `module1-typescript-topics.md` | topics — 15 sections: TS concepts + Sans-Python use case (agent schemas / tool wrappers / async LLM calls / MCP contracts) |
| 3 | `output/curriculum-map.md` | single — topic \| TS concept \| Sans-Python application \| module |
| — | `output/antilibrary.md` | mechanical — **expected empty**, note it |
| 5 | `output/visuals/diagrams.md` | mechanical — "no visuals found" (no Mermaid; only a book-cover PNG, not a curriculum diagram) |

Seam highlights (CONTEXT notes): `from-javascript-to-typescript` (LLM tooling is JS-first), `generics` (reusable type-safe tool defs / MCP contracts), `declaration-files` (untyped npm packages).

## 5. Verify
15 topic sections; inventory has 15 rows + test-structure section; curriculum-map has 15 rows; no FAILED markers; no empty files.

## 6. Manifest
```
skills/glm-extractor/
├── SKILL.md
└── extract.py   (single | topics)
```
