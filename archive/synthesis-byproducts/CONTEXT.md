# Synthesis — Consolidation & Indexing

**Status:** Consolidation complete. `source/` is a crawlable library, fully indexed.

## What this is

Synthesis is the consolidation step. It pulls every extraction output from all 9 sub-repos
into one place and organizes it into a single crawlable tree so downstream extraction is
easy. That's it.

It is **not** classification, distillation, or curriculum authoring. No content is judged,
cut, or written here. (An earlier draft framed synthesis as an editorial classification pass
— that was the wrong job. The old spec is preserved in `_archive/` for reference.)

## What's here

```
synthesis/
├── CONTEXT.md     ← this file
├── source/        ← the consolidated, crawlable library (see source/INDEX.md)
├── output/        ← empty; reserved for downstream work
└── _archive/      ← the superseded classification spec
```

`source/` holds:
- **40 content files** organized by module (`module1/`–`module5/`, `reference/`), each
  filename source-prefixed for provenance.
- **`_repos/`** — per-repo metadata that can't split by module: inventory, curriculum-map,
  antilibrary, and visuals for each of the 9 repos.
- **`INDEX.md`** — the master crawl map. Start here.

## How to use this

1. Open `source/INDEX.md`. It lists every file, the prefix→repo mapping, which repos feed
   each module, and where per-repo metadata lives.
2. For module content, go to `source/moduleN/`. Each module folder is a bounded unit — a
   downstream extraction task can be pointed at one module without loading the whole tree.
3. For deep context on a source (what it held, what was held back), read that repo's folder
   under `source/_repos/<repo>/`.

## State

- Files were **copied**, not moved — originals remain in each sub-repo's `output/`.
- One content file excluded by decision: `ahab-interview-prep.md` (Ahab is its own project).
- If files are added to a module folder, update `source/INDEX.md` so the tree stays fully
  indexed.

## Open questions for Ray

- Clean up the copied originals in sub-repo `output/content/` folders, or leave them?
- Does the next phase (downstream extraction / lesson authoring) get its own sibling spec
  folder, and what is its exact scope?
