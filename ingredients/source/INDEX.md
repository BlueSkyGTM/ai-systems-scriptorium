# Ingredients Source — Master Index

This folder (`ingredients/source/`) is the consolidated, crawlable mirror of all 9 sub-repo
extractions. Everything here is listed in this index. Nothing is uncatalogued.

**What this is:** a librarian's inventory. Content is organized by module (the unit a
later extraction task is pointed at). Per-repo metadata that can't split by module lives
under `_repos/`. Provenance is baked into every content filename via a source prefix.

**What this is NOT:** classification or curriculum. No content has been judged, cut, or
authored here. That happens downstream.

---

## Source prefix → repo

Every content filename starts with a prefix identifying its origin repo.

| Prefix  | Repo                          | `_repos/` folder                  |
|---------|-------------------------------|-----------------------------------|
| `aefs`  | ai-engineering-from-scratch   | `_repos/ai-engineering-from-scratch/` |
| `aipe`  | ai-performance-engineering    | `_repos/ai-performance-engineering/`  |
| `asdg`  | ai-system-design-guide        | `_repos/ai-system-design-guide/`      |
| `fleet` | fleet-engineering             | `_repos/fleet-engineering/`           |
| `loop`  | loop-engineering              | `_repos/loop-engineering/`            |
| `obook` | loop-engineering-orange-book  | `_repos/loop-engineering-orange-book/`|
| `mwml`  | made-with-ml                  | `_repos/made-with-ml/`                |
| `ts`    | typescript-projects           | `_repos/typescript-projects/`         |
| `rust`  | 100-exercises-to-learn-rust   | `_repos/100-exercises-to-learn-rust/` |

---

## Folder map

```
ingredients/source/
├── INDEX.md          ← this file
├── module1/          ← 5 content files
├── module2/          ← 5 content files
├── module3/          ← 18 content files
├── module4/          ← 9 content files
├── module5/          ← 1 content file
├── reference/        ← 2 cross-module content files
└── _repos/           ← per-repo metadata (inventory, curriculum-map, antilibrary, visuals)
```

**Totals:** 40 content files · 9 repo metadata folders · 48 metadata/visual files.

---

## Module 1 — 5 files

Contributing repos: aefs, rust, ts

| File | Repo |
|------|------|
| `module1/aefs-module1-nlp-transformer-forward.md` | aefs |
| `module1/aefs-module1-setup-tooling.md` | aefs |
| `module1/rust-module1-rust-book-structure.md` | rust |
| `module1/rust-module1-rust-exercises-by-topic.md` | rust |
| `module1/ts-module1-typescript-topics.md` | ts |

## Module 2 — 5 files

Contributing repos: aefs, asdg

| File | Repo |
|------|------|
| `module2/aefs-module2-generative-ai.md` | aefs |
| `module2/aefs-module2-llm-engineering.md` | aefs |
| `module2/asdg-module2-eval-guides.md` | asdg |
| `module2/asdg-module2-prompting-context.md` | asdg |
| `module2/asdg-module2-retrieval-systems.md` | asdg |

## Module 3 — 18 files

Contributing repos: aefs, asdg, fleet, loop

| File | Repo |
|------|------|
| `module3/aefs-module3-agent-engineering.md` | aefs |
| `module3/aefs-module3-tools-protocols.md` | aefs |
| `module3/asdg-module3-agentic-systems.md` | asdg |
| `module3/asdg-module3-design-patterns.md` | asdg |
| `module3/asdg-module3-frameworks-tools.md` | asdg |
| `module3/asdg-module3-memory-state.md` | asdg |
| `module3/asdg-module3-tool-use-computer-agents.md` | asdg |
| `module3/fleet-module3-fleet-patterns.md` | fleet |
| `module3/fleet-module3-fleet-reference.md` | fleet |
| `module3/fleet-module3-fleet-schemas.md` | fleet |
| `module3/fleet-module3-fleet-stories.md` | fleet |
| `module3/fleet-module3-fleet-templates.md` | fleet |
| `module3/loop-module3-loop-docs.md` | loop |
| `module3/loop-module3-loop-patterns.md` | loop |
| `module3/loop-module3-loop-reference.md` | loop |
| `module3/loop-module3-loop-skills.md` | loop |
| `module3/loop-module3-loop-stories.md` | loop |
| `module3/loop-module3-loop-templates.md` | loop |

## Module 4 — 9 files

Contributing repos: aefs, aipe, asdg, mwml

| File | Repo |
|------|------|
| `module4/aefs-module4-infrastructure-production.md` | aefs |
| `module4/aipe-module4-full-sweep-checklist.md` | aipe |
| `module4/aipe-module4-inference-reference-docs.md` | aipe |
| `module4/aipe-module4-inference-serving-chapters.md` | aipe |
| `module4/asdg-module4-case-studies.md` | asdg |
| `module4/asdg-module4-deploy-chapters.md` | asdg |
| `module4/mwml-module4-deploy-scripts.md` | mwml |
| `module4/mwml-module4-madewithml-code-inventory.md` | mwml |
| `module4/mwml-module4-madewithml-notebook-outline.md` | mwml |

## Module 5 — 1 file

Contributing repos: aefs

| File | Repo |
|------|------|
| `module5/aefs-module5-capstone.md` | aefs |

## Reference — 2 files

Cross-module material, not tied to a single module.

| File | Repo |
|------|------|
| `reference/aefs-scripts-inventory.md` | aefs |
| `reference/obook-orange-book-structure.md` | obook |

---

## `_repos/` — per-repo metadata

Each repo folder mirrors its original `output/` metadata: `inventory.md` (what the repo
held), `curriculum-map.md` (how the extraction mapped it to modules), `antilibrary.md`
(material held back, not cut), and `visuals/` (diagrams and assets). Use these for deep
context on a source; they are not module content.

| Repo | inventory | curriculum-map | antilibrary | visuals |
|------|-----------|----------------|-------------|---------|
| ai-engineering-from-scratch | ✓ | ✓ | ✓ | diagrams.md, banner.svg |
| ai-performance-engineering | ✓ | ✓ | ✓ | diagrams.md |
| ai-system-design-guide | ✓ | ✓ | ✓ | diagrams.md |
| fleet-engineering | ✓ | ✓ | ✓ | diagrams.md, cobus-greyling.jpg, fleet-engineering-header.jpg |
| loop-engineering | ✓ | ✓ | ✓ | diagrams.md, social-preview.jpg, author-banner.jpg, primitives-infographic.jpg, loop-anatomy.jpg, loop-engineering-social-banner.jpg, loop-engineering-logo.jpg |
| loop-engineering-orange-book | ✓ | — | ✓ | cover.jpg, page-cover.png, page-toc.png, page-ch01.png, page-ch03.png |
| made-with-ml | ✓ | ✓ | ✓ | diagrams.md |
| typescript-projects | ✓ | ✓ | ✓ | diagrams.md |
| 100-exercises-to-learn-rust | ✓ | ✓ | ✓ | diagrams.md |

Note: loop-engineering-orange-book has no curriculum-map (it produced a single structural
content file; nothing to map across modules).

---

## Provenance notes

- Files were **copied**, not moved. Originals remain in each sub-repo's `output/` folder.
- One content file was **not** carried over: `ahab-interview-prep.md`
  (from ai-system-design-guide). Ahab is a separate project; excluded by decision.
- This index reflects state as of consolidation. If files are added to a module folder,
  add the row here so the tree stays fully indexed.
